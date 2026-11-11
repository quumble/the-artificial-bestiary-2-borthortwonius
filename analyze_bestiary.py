#!/usr/bin/env python3
"""Run only after collection closes. Deterministic literal scoring and word-level analysis."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sys
import numpy as np
import bestiary_scorer as scorer
import run_bestiary as collector

PRIMARY = ["M01","M02","M03","M09"]
FRAMES = ["imaginary","type_of"]


def read_jsonl(path):
    if not path.exists():
        return []
    records = []
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except ValueError as exc:
                raise ValueError(f"Malformed JSONL at {path.name}:{number}; no lines silently discarded") from exc
    return records


def mean(values):
    return float(np.mean(values)) if values and all(v is not None for v in values) else None


def bound_cell(values, planned):
    observed = [v for v in values if v is not None]
    yes = sum(observed)
    return [yes/planned,(yes+planned-len(observed))/planned]


def validate_manifest(manifest, root):
    copy = dict(manifest)
    h = copy.pop("manifest_sha256")
    if collector.digest(collector.canonical(copy).encode()) != h:
        raise ValueError("Freeze manifest integrity failure.")
    for name,expected in manifest["code_hashes"].items():
        if collector.digest((root/name).read_bytes()) != expected:
            raise ValueError("Frozen source changed: "+name)
    if manifest["numpy"] != np.__version__ or manifest["python"] != sys.version:
        raise ValueError("Analysis runtime differs from freeze.")


def select_records(manifest, attempts):
    planned = {(batch,model,t["trial_id"]):t for batch,models in manifest["batches"].items() for model,trials in models.items() for t in trials}
    selected, audit, counts = {}, [], defaultdict(int)
    for attempt in sorted(attempts,key=lambda a:a["id"]):
        batch,model = attempt["phase"],attempt["model"]
        if batch not in collector.REPS:
            continue
        key = (batch,model,attempt["trial_id"])
        counts[key] += 1
        fields = attempt.get("fields") or {}
        reason = None
        if key not in planned:
            reason = "unplanned_slot"
        elif attempt["trial"] != planned[key]:
            reason = "trial_metadata_mismatch"
        else:
            config = manifest["settings"][model]
            expected = collector.payload(config["model_config"],planned[key]["prompt"])
            if attempt["request"] != expected or attempt["request_hash"] != collector.digest(collector.canonical(expected).encode()):
                reason = "request_mismatch"
            elif not fields.get("terminal"):
                reason = "nonterminal_attempt"
            elif not fields.get("valid") or fields.get("error") or fields.get("protocol_violation") or fields.get("issue"):
                reason = "invalid_terminal"
            elif fields.get("model_returned") != config["model_returned"]:
                reason = "returned_model_mismatch"
            elif key in selected:
                reason = "duplicate_terminal"
        if reason:
            audit.append(dict(attempt_id=attempt["attempt_id"],slot=key,reason=reason))
        else:
            selected[key] = attempt
    return planned,selected,audit,counts


def make_cells(planned, selected, counts):
    groups, response_rows = defaultdict(list), []
    for key,trial in planned.items():
        batch,model,_ = key
        attempt = selected.get(key)
        fields = attempt["fields"] if attempt else {}
        result = scorer.score(fields.get("response"),trial["word"],trial["prompt"])
        row = dict(trial,model_requested=model,attempt_count=counts.get(key,0),terminal=bool(attempt),
                   complete=fields.get("complete",False),truncated=fields.get("truncated",False),
                   refusal=fields.get("refusal",False),attempt_id=attempt["attempt_id"] if attempt else None,
                   response=fields.get("response"),scoring=result)
        response_rows.append(row)
        groups[(batch,model,trial["word"],trial["condition"])].append(row)
    cells = {}
    for key,rows in groups.items():
        usable = [r for r in rows if r["scoring"]["usable"]]
        cell = dict(batch=key[0],model=key[1],word=key[2],condition=key[3],word_set=rows[0]["word_set"],
                    source_set_label=rows[0]["source_set_label"],planned=len(rows),
                    attempts=sum(r["attempt_count"] for r in rows),terminal=sum(r["terminal"] for r in rows),usable=len(usable),
                    complete_usable=sum(r["complete"] for r in usable),cap_truncated=sum(r["truncated"] and r["terminal"] for r in rows),
                    other_incomplete=sum(r["terminal"] and not r["complete"] and not r["truncated"] for r in rows),
                    empty=sum(r["terminal"] and not r["scoring"]["usable"] for r in rows),missing=len(rows)-len(usable),
                    primary={},bounds={},completion_bounds={})
        for family in PRIMARY:
            values = [r["scoring"]["features"][family]["any"] if r["scoring"]["usable"] else None for r in rows]
            observed = [v for v in values if v is not None]
            cell["primary"][family] = mean(observed)
            cell["bounds"][family] = bound_cell(values,len(rows))
            completion = [v if v==1 or r["complete"] else None for r,v in zip(rows,values)]
            cell["completion_bounds"][family] = bound_cell(completion,len(rows))
        cell["repetition"] = scorer.cell_features([r["response"] for r in rows])
        cells[key] = cell
    return cells,response_rows


def contrasts(cells,batch,models,word_sets,field="primary"):
    """Return word vectors carrying all eight endpoints, with fixed weights."""
    per_model,per_word = {},{}
    for model in models:
        per_model[model] = {}
        for source,words in word_sets.items():
            per_model[model][source] = []
            for word in words:
                vector = []
                for family in PRIMARY:
                    for frame in FRAMES:
                        deltas = []
                        for category in collector.CATEGORIES:
                            a = cells[(batch,model,word,frame+"_"+category)][field][family]
                            b = cells[(batch,model,word,"real_"+category)][field][family]
                            deltas.append(a-b if a is not None and b is not None else None)
                        vector.append(mean(deltas))
                per_model[model][source].append(vector)
    for source,words in word_sets.items():
        per_word[source] = [[mean([per_model[m][source][i][j] for m in models]) for j in range(8)] for i in range(len(words))]
    return per_model,per_word


def primary_word_sets(manifest,batch):
    """Use the planned source bank, never the words surviving outcome exclusions."""
    bank = defaultdict(set)
    word_labels = {}
    for trials in manifest["batches"][batch].values():
        for trial in trials:
            label = trial["source_set_label"] if batch == "fresh" else trial["word_set"]
            if trial["word"] in word_labels and word_labels[trial["word"]] != label:
                raise ValueError("Word has inconsistent source labels in the frozen schedule.")
            word_labels[trial["word"]] = label
            bank[label].add(trial["word"])
    expected = set(collector.FRESH_SETS) if batch == "fresh" else {"known-animal-intent","known-no-intent"}
    if set(bank) != expected:
        raise ValueError("Frozen schedule is missing the required word-source groups: "+batch)
    return {source:sorted(words) for source,words in sorted(bank.items())}


def source_weights(word_sets,batch,equal_intent=False):
    if batch == "fresh" and equal_intent:
        return {source:0.5 if source == "fresh-animal-intent" else 0.25 for source in word_sets}
    return {source:1/len(word_sets) for source in word_sets}


def weighted_mean(values,weights):
    if any(values.get(source) is None for source in weights):
        return None
    return float(sum(weights[source]*values[source] for source in weights))


def summarize_primary(cells,batch,manifest,draws=50000):
    models = list(manifest["batches"][batch])
    word_sets = primary_word_sets(manifest,batch)
    weights = source_weights(word_sets,batch)
    intent_weights = source_weights(word_sets,batch,equal_intent=True)
    per_model,per_word = contrasts(cells,batch,models,word_sets)
    arrays = {s:np.array(v,dtype=float) for s,v in per_word.items()}
    rng = np.random.Generator(np.random.PCG64(20261111 if batch=="fresh" else 20261112))
    bootstrap = np.zeros((draws,8))
    intent_bootstrap = np.zeros((draws,8))
    index_bank={s:np.empty((draws,len(arr)),dtype=int) for s,arr in arrays.items()}
    for draw in range(draws):
        for source,arr in arrays.items():
            index_bank[source][draw]=rng.integers(0,len(arr),size=len(arr))
    for source,arr in arrays.items():
        indices = index_bank[source]
        sampled_means = arr[indices].mean(axis=1)
        bootstrap += sampled_means*weights[source]
        intent_bootstrap += sampled_means*intent_weights[source]
    result = []
    for j,(family,frame) in enumerate((f,r) for f in PRIMARY for r in FRAMES):
        estimates = {s:mean([v[j] for v in per_word[s]]) for s in word_sets}
        effect = weighted_mean(estimates,weights)
        intent_effect = weighted_mean(estimates,intent_weights)
        valid_boot = np.isfinite(bootstrap[:,j]).all()
        ci95 = np.quantile(bootstrap[:,j],[.025,.975],method="linear").tolist() if valid_boot else None
        adjusted = np.quantile(bootstrap[:,j],[.003125,.996875],method="linear").tolist() if valid_boot and batch=="fresh" else None
        degenerate = bool(valid_boot and np.ptp(bootstrap[:,j])==0)
        bounds, intent_bounds = {}, {}
        for field in ["bounds","completion_bounds"]:
            model_bounds, intent_model_bounds = [], []
            for model in models:
                set_bounds = {}
                for source,words in word_sets.items():
                    word_bounds=[]
                    for word in words:
                        values=[]
                        for category in collector.CATEGORIES:
                            a=cells[(batch,model,word,frame+"_"+category)][field][family]
                            b=cells[(batch,model,word,"real_"+category)][field][family]
                            values.append([a[0]-b[1],a[1]-b[0]])
                        word_bounds.append(np.mean(values,axis=0))
                    set_bounds[source] = np.mean(word_bounds,axis=0)
                model_bounds.append(sum(weights[s]*set_bounds[s] for s in word_sets))
                intent_model_bounds.append(sum(intent_weights[s]*set_bounds[s] for s in word_sets))
            bounds[field]=np.mean(model_bounds,axis=0).tolist()
            intent_bounds[field]=np.mean(intent_model_bounds,axis=0).tolist()
        component={m:{s:mean([v[j] for v in per_model[m][s]]) for s in word_sets} for m in models}
        intent_valid = np.isfinite(intent_bootstrap[:,j]).all()
        alternative = dict(effect=intent_effect,
                           ci95=np.quantile(intent_bootstrap[:,j],[.025,.975],method="linear").tolist() if intent_valid else None,
                           bootstrap_degenerate=bool(intent_valid and np.ptp(intent_bootstrap[:,j])==0),
                           status="descriptive sensitivity; same paired source-stratified resamples; no additional confirmatory test",
                           **intent_bounds)
        leave_one_out={}
        for source,words in word_sets.items():
            for i,word in enumerate(words):
                values={}
                for s,arr in arrays.items():
                    subset=np.delete(arr[:,j],i) if s==source else arr[:,j]
                    values[s]=float(subset.mean()) if np.isfinite(subset).all() and len(subset) else None
                leave_one_out[word]=weighted_mean(values,weights)
        confirm=bool(batch=="fresh" and adjusted and not degenerate and (adjusted[0]>0 or adjusted[1]<0) and draws==50000)
        result.append(dict(outcome=family,contrast=frame+"-real",effect=effect,ci95=ci95,
            simultaneous_ci99375=adjusted,bootstrap_degenerate=degenerate,confirmatory_direction=confirm,
            conditional_on_observed=bool(bounds["bounds"][0]<=0<=bounds["bounds"][1]),
            model_set_components=component,alternative_equal_intent_weighting=alternative,leave_one_word_out=leave_one_out,**bounds))
    return dict(batch=batch,scale="proportions; multiply by 100 for percentage points",bootstrap_draws=draws,
                resampling="paired whole words within each planned source group; models fixed",
                weights=weights,alternative_equal_intent_weights=intent_weights,word_sets=word_sets,contrasts=result)


def scalar_features(value,prefix=""):
    if isinstance(value,dict):
        for key,sub in value.items():
            if key in {"entries","sources","raw_positions","vectors"}:
                continue
            yield from scalar_features(sub,prefix+"."+key if prefix else key)
    elif isinstance(value,(int,float)) and not isinstance(value,bool):
        yield prefix,value
    elif value is None:
        yield prefix,None


def secondary_tables(response_rows,cells):
    feature_cells=defaultdict(lambda:defaultdict(list))
    states=defaultdict(list)
    reuse=defaultdict(dict)
    for row in response_rows:
        key=(row["batch"],row["model_requested"],row["word"],row["condition"])
        if row["scoring"]["usable"]:
            for name,value in scalar_features(row["scoring"]["features"]):
                if value is not None:
                    feature_cells[key][name].append(value)
            states[key].append(row["scoring"]["features"]["M13"]["state"])
        group=reuse[(key[0],key[1],key[3])].setdefault(row["word"],dict(word_set=row["word_set"],responses=[]))
        group["responses"].append(row["response"])
    tables=[]
    for key,cell in cells.items():
        names=feature_cells[key]
        tables.append(dict(batch=key[0],model=key[1],word=key[2],condition=key[3],word_set=cell["word_set"],source_set_label=cell["source_set_label"],
            features={name:dict(mean=mean(values),eligible=len(values),planned=cell["planned"],usable=cell["usable"]) for name,values in names.items()},
            M13_states={state:states[key].count(state)/len(states[key]) if states[key] else None for state in ["definition_first","cue_first","tie","definition_only","cue_only","neither"]}))
    reuse_tables=[dict(batch=k[0],model=k[1],condition=k[2],M28=scorer.reuse_features(v)) for k,v in sorted(reuse.items())]
    # Complete-panel aggregates: missing eligible features remain null, never
    # silently renormalized over words or source sets that happened to respond.
    grouped=defaultdict(list)
    for row in tables:
        grouped[(row["batch"],row["model"],row["condition"],row["word_set"])].append(row)
    summaries=[]
    for key,rows in sorted(grouped.items()):
        names=set().union(*(r["features"] for r in rows))
        summaries.append(dict(batch=key[0],model=key[1],condition=key[2],word_set=key[3],words=len(rows),
            features={name:dict(mean=mean([r["features"].get(name,{}).get("mean") for r in rows]),
                                eligible_responses=sum(r["features"].get(name,{}).get("eligible",0) for r in rows)) for name in sorted(names)}))
    return tables,summaries,reuse_tables


def sensitivities(response_rows,base_cells,manifest):
    versions={}
    for name in ["complete_only","prefix50","prefix100","M01_without_imaginary","M02_modal_only"]:
        cells={key:dict(cell,primary={f:None for f in PRIMARY}) for key,cell in base_cells.items()}
        values=defaultdict(lambda:defaultdict(list))
        eligible=defaultdict(int)
        for row in response_rows:
            if not row["scoring"]["usable"]:
                continue
            key=(row["batch"],row["model_requested"],row["word"],row["condition"])
            result=row["scoring"]
            if name=="complete_only" and not row["complete"]:
                continue
            if name.startswith("prefix"):
                length=int(name[6:]); text=scorer.Text(row["response"])
                if len(text.tokens)<length:
                    continue
                result=scorer.score(row["response"][:text.tokens[length-1]["raw_end"]],row["word"],row["prompt"])
            eligible[key]+=1
            for family in PRIMARY:
                value=result["features"][family]["any"]
                if name=="M01_without_imaginary" and family=="M01":
                    value=int(any(m["family"]=="M01" and m["entry"]!="imaginary" for m in result["matches"]))
                if name=="M02_modal_only" and family=="M02":
                    value=result["features"]["M02"]["components"]["modal"]["any"]
                values[key][family].append(value)
        for key,cell in cells.items():
            cell["primary"]={f:mean(values[key][f]) for f in PRIMARY}
        summaries={}
        for batch in manifest["batches"]:
            word_sets=primary_word_sets(manifest,batch)
            weights=source_weights(word_sets,batch)
            _,pw=contrasts(cells,batch,list(manifest["batches"][batch]),word_sets)
            summaries[batch]=[weighted_mean({s:mean([v[j] for v in pw[s]]) for s in pw},weights) for j in range(8)]
        versions[name]=dict(contrast_order=[f+":"+r+"-real" for f in PRIMARY for r in FRAMES],effects=summaries,
                           eligibility=[dict(batch=k[0],model=k[1],word=k[2],condition=k[3],eligible=eligible[k],planned=c["planned"]) for k,c in cells.items()])
    return versions


def planned_secondary_contrasts(cells,manifest):
    """Fixed endpoint/frame/category/word-set comparisons, descriptive only."""
    rates={}
    banks,source_banks,report_banks={},{},{}
    for batch,models in manifest["batches"].items():
        bank=defaultdict(set)
        for trials in models.values():
            for t in trials:bank[t["word_set"]].add(t["word"])
        banks[batch]={s:sorted(v) for s,v in bank.items()}
        source_banks[batch]=primary_word_sets(manifest,batch)
        report_banks[batch]={**banks[batch],**source_banks[batch]}
        weights=source_weights(source_banks[batch],batch)
        conditions=sorted({c[3] for c in cells if c[0]==batch})
        for model in models:
            for condition in conditions:
                for family in PRIMARY:
                    for source,words in report_banks[batch].items():
                        rates[(batch,model,source,condition,family)]=mean([cells[(batch,model,w,condition)]["primary"][family] for w in words])
                    rates[(batch,model,"equal_intent",condition,family)]=mean([rates[(batch,model,s,condition,family)] for s in banks[batch]])
                    rates[(batch,model,"primary_weighting",condition,family)]=weighted_mean(
                        {s:rates[(batch,model,s,condition,family)] for s in source_banks[batch]},weights)
    out=[]
    def difference(a,b):return a-b if a is not None and b is not None else None
    pairings=[("claude-sonnet-5-5","claude-sonnet-4-6"),("claude-haiku-5-5","claude-haiku-4-5"),
              ("gpt-6-sol","gpt-5.4-mini"),("gpt-6-luna","gpt-5.4-nano")]
    frame_effects={}
    for batch,models in manifest["batches"].items():
        for model in models:
            for family in PRIMARY:
                for source in list(report_banks[batch])+["equal_intent","primary_weighting"]:
                    frames={frame:mean([rates[(batch,model,source,frame+"_"+c,family)] for c in collector.CATEGORIES]) for frame in ["real","imaginary","type_of"]}
                    for frame,value in frames.items():
                        out.append(dict(kind="frame_minus_neutral",batch=batch,model=model,word_set=source,outcome=family,
                                        contrast=frame+"-neutral",effect=difference(value,rates[(batch,model,source,"neutral",family)])))
                        for a,b in [("animal","object"),("animal","idea"),("object","idea")]:
                            out.append(dict(kind="category_difference",batch=batch,model=model,word_set=source,outcome=family,
                                            frame=frame,contrast=a+"-"+b,effect=difference(rates[(batch,model,source,frame+"_"+a,family)],rates[(batch,model,source,frame+"_"+b,family)])))
                    for frame in FRAMES:
                        frame_effects[(batch,model,source,frame,family)]=difference(frames[frame],frames["real"])
                animal=next(s for s in banks[batch] if s.endswith("animal-intent")); other=next(s for s in banks[batch] if s.endswith("no-intent"))
                conditions=sorted({key[3] for key in rates if key[0]==batch})
                for condition in conditions:
                    out.append(dict(kind="source_set_difference",batch=batch,model=model,condition=condition,outcome=family,
                                    contrast="animal_intent-minus-no_intent",effect=difference(rates[(batch,model,animal,condition,family)],rates[(batch,model,other,condition,family)])))
                for frame in FRAMES:
                    out.append(dict(kind="source_set_frame_interaction",batch=batch,model=model,outcome=family,contrast=frame+"-real",
                                    effect=difference(frame_effects[(batch,model,animal,frame,family)],frame_effects[(batch,model,other,frame,family)])))
        for current,historical in pairings:
            if current not in models or historical not in models:continue
            for family in PRIMARY:
                for frame in FRAMES:
                    out.append(dict(kind="generation_frame_interaction",batch=batch,models=[current,historical],outcome=family,contrast=frame+"-real",
                                    weighting="primary_weighting",effect=difference(frame_effects[(batch,current,"primary_weighting",frame,family)],frame_effects[(batch,historical,"primary_weighting",frame,family)])))
                for condition in sorted({key[3] for key in rates if key[0]==batch}):
                    out.append(dict(kind="generation_condition_difference",batch=batch,models=[current,historical],outcome=family,condition=condition,
                                    weighting="primary_weighting",effect=difference(rates[(batch,current,"primary_weighting",condition,family)],rates[(batch,historical,"primary_weighting",condition,family)])))
    if "fresh" in banks and "known" in banks:
        batch_effects={}
        shared=set(manifest["batches"]["fresh"]) & set(manifest["batches"]["known"])
        for model in sorted(shared):
            for family in PRIMARY:
                for condition in sorted({key[3] for key in rates if key[0]=="fresh"}):
                    for label in ["animal-intent","no-intent","equal_intent"]:
                        sa=label if label=="equal_intent" else "known-"+label
                        sb=label if label=="equal_intent" else "fresh-"+label
                        effect=difference(rates[("known",model,sa,condition,family)],rates[("fresh",model,sb,condition,family)])
                        out.append(dict(kind="known_minus_fresh",model=model,outcome=family,condition=condition,word_set=label,effect=effect))
                        batch_effects[(model,family,condition,label)]=effect
        for current,historical in pairings:
            if current not in shared or historical not in shared:continue
            for key,effect in batch_effects.items():
                if key[0]==current:
                    other=batch_effects[(historical,)+key[1:]]
                    out.append(dict(kind="generation_batch_interaction",models=[current,historical],outcome=key[1],condition=key[2],word_set=key[3],effect=difference(effect,other)))
    return dict(status="prespecified descriptive; no confirmatory p-values or exposure attribution",
                primary_weights={batch:source_weights(bank,batch) for batch,bank in source_banks.items()},
                cross_batch_weighting="equal_intent: one-half animal-intent and one-half no-intent in both batches",
                contrasts=out)


def repetition_summaries(cells):
    groups=defaultdict(list)
    for cell in cells.values():
        groups[(cell["batch"],cell["model"],cell["condition"],cell["word_set"])].append(cell)
    output=[]
    for key,values in sorted(groups.items()):
        flattened=[dict(scalar_features({f:c["repetition"][f] for f in ["M26","M27"]})) for c in values]
        names=set().union(*flattened)
        features={name:dict(mean=mean([v.get(name) for v in flattened]),eligible_word_cells=sum(v.get(name) is not None for v in flattened),
                            planned_word_cells=len(values)) for name in sorted(names)}
        output.append(dict(batch=key[0],model=key[1],condition=key[2],word_set=key[3],features=features))
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data",type=Path,default=collector.ROOT/"data")
    parser.add_argument("--output",type=Path,default=collector.ROOT/"analysis")
    args=parser.parse_args()
    if args.output.resolve()==args.data.resolve() or args.data.resolve() in args.output.resolve().parents:
        raise ValueError("Analysis output must be outside the raw data directory.")
    manifest=json.loads((args.data/"freeze.json").read_text(encoding="utf-8"))
    validate_manifest(manifest,collector.ROOT)
    closure=json.loads((args.data/"collection-status.json").read_text(encoding="utf-8"))
    if not all(closure.get(batch) for batch in collector.REPS):
        raise ValueError("Both batches must finish or be formally stopped before scoring.")
    attempts=read_jsonl(args.data/"attempts.jsonl")
    planned,selected,audit,counts=select_records(manifest,attempts)
    cells,rows=make_cells(planned,selected,counts)
    primary={batch:summarize_primary(cells,batch,manifest) for batch in manifest["batches"]}
    table,summaries,reuse=secondary_tables(rows,cells)
    sensitivity=sensitivities(rows,cells,manifest)
    tripwire=[]
    grouped=defaultdict(list)
    for c in cells.values():grouped[(c["batch"],c["model"],c["condition"])].append(c)
    for key,values in grouped.items():
        denominator=sum(v["terminal"] for v in values); truncated=sum(v["cap_truncated"] for v in values)
        tripwire.append(dict(batch=key[0],model=key[1],condition=key[2],terminal=denominator,truncated=truncated,
                            rate=truncated/denominator if denominator else None,flag=bool(denominator and truncated/denominator>.01)))
    args.output.mkdir(parents=True,exist_ok=True)
    files={"primary.json":primary,"sensitivities.json":sensitivity,"audit.json":audit,"truncation.json":tripwire,
           "secondary-contrasts.json":planned_secondary_contrasts(cells,manifest),
           "repetition-summaries.json":repetition_summaries(cells),
           "feature-summaries.json":summaries,"analysis-provenance.json":dict(protocol=manifest["protocol"],manifest_sha256=manifest["manifest_sha256"],
                scorer_version=scorer.VERSION,attempts_sha256=collector.digest((args.data/"attempts.jsonl").read_bytes()),bootstrap_draws=50000)}
    for name,value in files.items():collector.atomic_write(args.output/name,json.dumps(value,indent=2,allow_nan=False)+"\n")
    for name,values in [("response-features.jsonl",rows),("cell-features.jsonl",list(cells.values())),("secondary-cell-features.jsonl",table),("cross-word-reuse.jsonl",reuse)]:
        collector.atomic_write(args.output/name,"".join(json.dumps(v,ensure_ascii=False,allow_nan=False)+"\n" for v in values))
    print("Analysis written:",args.output,"; eight primary contrasts per batch; no response text printed.")


if __name__=="__main__":
    main()
