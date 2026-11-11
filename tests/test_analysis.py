import copy
import json
import tempfile
from pathlib import Path
import unittest
import numpy as np
import analyze_bestiary as a
import run_bestiary as r
import bestiary_scorer as s


def fixture():
    words=[("fresh-animal-intent","zuvema","fresh-animal-intent"),("fresh-animal-intent","zuvemb","fresh-animal-intent")]
    words += [("fresh-no-intent","fepal"+suffix,"fresh-no-intent-claude") for suffix in "ab"]
    words += [("fresh-no-intent","fepal"+suffix,"fresh-no-intent-gpt") for suffix in "cd"]
    manifest=dict(batches={"fresh":{}},settings={})
    planned={};selected={};counts={}
    ordinal=0
    for model in r.MODELS:
        trials=r.build_trials("fresh",words)
        # Deliberately unequal usable repetitions across source sets.
        manifest["batches"]["fresh"][model["id"]]=trials
        manifest["settings"][model["id"]]=dict(model_config=model,model_returned=model["id"])
        for trial in trials:
            key=("fresh",model["id"],trial["trial_id"])
            planned[key]=trial
            if trial["word_set"].endswith("no-intent") and trial["rep"]>1:continue
            response="This is fictional." if trial["word_set"].endswith("animal-intent") and trial["reality"]=="imaginary" else "Blue."
            ordinal+=1
            selected[key]=dict(id=ordinal,attempt_id=str(ordinal),fields=dict(response=response,complete=True,truncated=False,refusal=False))
            counts[key]=1
    cells,rows=a.make_cells(planned,selected,counts)
    return manifest,planned,selected,counts,cells,rows


class AnalysisTests(unittest.TestCase):
    def test_equal_word_source_and_model_weights(self):
        manifest,_,_,_,cells,_=fixture()
        result=a.summarize_primary(cells,"fresh",manifest,draws=100)
        first=result["contrasts"][0]
        self.assertAlmostEqual(first["effect"],1/3)
        self.assertAlmostEqual(first["alternative_equal_intent_weighting"]["effect"],.5)
        self.assertEqual(result["weights"],{s:1/3 for s in r.FRESH_SETS})
        self.assertEqual(result["alternative_equal_intent_weights"],{
            "fresh-animal-intent":.5,"fresh-no-intent-claude":.25,"fresh-no-intent-gpt":.25})
        self.assertTrue(first["bootstrap_degenerate"])
        self.assertFalse(first["confirmatory_direction"])
        self.assertAlmostEqual(first["bounds"][0],-.2)
        self.assertAlmostEqual(first["bounds"][1],13/15)
        self.assertAlmostEqual(first["alternative_equal_intent_weighting"]["bounds"][0],.1)
        self.assertAlmostEqual(first["alternative_equal_intent_weighting"]["bounds"][1],.9)

    def test_bootstrap_preserves_each_model_author_group(self):
        manifest,_,_,_,cells,_=fixture()
        # Each Claude word has effect 1 and each GPT/human word effect 0.
        # Mixing Claude and GPT in one resampling pool would create spurious
        # variation despite every word within each fixed source agreeing.
        for cell in cells.values():
            cell["primary"]["M01"]=int(cell["source_set_label"]=="fresh-no-intent-claude" and cell["condition"].startswith("imaginary_"))
        result=a.summarize_primary(cells,"fresh",manifest,draws=100)["contrasts"][0]
        self.assertAlmostEqual(result["effect"],1/3)
        self.assertEqual(result["ci95"],[1/3,1/3])
        self.assertTrue(result["bootstrap_degenerate"])
        self.assertEqual(result["alternative_equal_intent_weighting"]["ci95"],[.25,.25])
        self.assertFalse(result["confirmatory_direction"])

    def test_missing_source_is_not_reweighted_away(self):
        manifest,_,_,_,cells,_=fixture()
        for model,trials in manifest["batches"]["fresh"].items():
            manifest["batches"]["fresh"][model]=[t for t in trials if t["source_set_label"]!="fresh-no-intent-gpt"]
        with self.assertRaisesRegex(ValueError,"required word-source groups"):
            a.summarize_primary(cells,"fresh",manifest,draws=100)

    def test_missing_required_cell_nulls_pool_but_bounds_remain(self):
        manifest,_,_,_,cells,_=fixture()
        key=next(k for k in cells if k[3]=="real_animal")
        cells[key]["primary"]["M01"]=None
        result=a.summarize_primary(cells,"fresh",manifest,draws=100)["contrasts"][0]
        self.assertIsNone(result["effect"])
        self.assertIsNone(result["ci95"])
        self.assertIsNone(result["alternative_equal_intent_weighting"]["effect"])
        self.assertIsNone(result["alternative_equal_intent_weighting"]["ci95"])
        self.assertEqual(len(result["bounds"]),2)

    def test_bounds_and_complete_only_eligibility(self):
        self.assertEqual(a.bound_cell([1,0,None,None,None],5),[.2,.8])
        manifest,planned,selected,counts,_,_=fixture()
        key=next(iter(selected));selected[key]["fields"].update(response="Blue.",complete=False,truncated=True)
        cells,rows=a.make_cells(planned,selected,counts)
        c=cells[(key[0],key[1],planned[key]["word"],planned[key]["condition"])]
        self.assertEqual(c["primary"]["M01"],0)
        self.assertEqual(c["completion_bounds"]["M01"],[0,.2])
        sensitivity=a.sensitivities(rows,cells,manifest)
        eligibility=sensitivity["complete_only"]["eligibility"]
        item=next(e for e in eligibility if (e["batch"],e["model"],e["word"],e["condition"])==(key[0],key[1],planned[key]["word"],planned[key]["condition"]))
        self.assertEqual(item["eligible"],4)
        self.assertAlmostEqual(sensitivity["complete_only"]["effects"]["fresh"][0],1/3)
        self.assertAlmostEqual(sensitivity["M01_without_imaginary"]["effects"]["fresh"][0],1/3)

    def test_audit_duplicate_and_wrong_request(self):
        model=r.MODELS[-1];trial=r.build_trials("fresh",[("fresh-animal-intent","zuvem","human")])[0]
        manifest=dict(batches={"fresh":{model["id"]:[trial]}},settings={model["id"]:dict(model_config=model,model_returned=model["id"])})
        body=r.payload(model,trial["prompt"])
        rec=dict(id=1,attempt_id="first",phase="fresh",model=model["id"],trial_id=trial["trial_id"],trial=trial,request=body,
                 request_hash=r.digest(r.canonical(body).encode()),fields=dict(valid=True,terminal=True,model_returned=model["id"],error=None,response="Blue."))
        second=copy.deepcopy(rec);second.update(id=2,attempt_id="second")
        wrong=copy.deepcopy(rec);wrong.update(id=3,attempt_id="wrong");wrong["request"]["temperature"]=0
        issue=copy.deepcopy(rec);issue.update(id=4,attempt_id="issue");issue["fields"]["issue"]="schema_error"
        _,selected,audit,counts=a.select_records(manifest,[wrong,second,rec,issue])
        self.assertEqual(next(iter(selected.values()))["attempt_id"],"first")
        self.assertEqual({x["reason"] for x in audit},{"duplicate_terminal","request_mismatch","invalid_terminal"})
        self.assertEqual(next(iter(counts.values())),4)

    def test_known_fresh_comparison_keeps_common_intent_weights(self):
        manifest,_,_,_,cells,_=fixture()
        words=[("known-animal-intent","kanima","known-animal-intent"),
               ("known-animal-intent","kanimb","known-animal-intent"),
               ("known-no-intent","knonea","known-no-intent"),
               ("known-no-intent","knoneb","known-no-intent")]
        manifest["batches"]["known"]={}
        for model in r.MODELS:
            mid=model["id"]
            manifest["batches"]["known"][mid]=r.build_trials("known",words)
            for intent,word,source in words:
                template="zuvema" if intent.endswith("animal-intent") else "fepala"
                for condition in {k[3] for k in cells if k[0]=="fresh"}:
                    c=copy.deepcopy(cells[("fresh",mid,template,condition)])
                    c.update(batch="known",word=word,word_set=intent,source_set_label=source)
                    cells[("known",mid,word,condition)]=c
        # The underlying within-intent effects match exactly. Raw batch
        # averages differ because fresh has 1/3 animal-intent and known 1/2.
        fresh=a.summarize_primary(cells,"fresh",manifest,draws=100)["contrasts"][0]["effect"]
        known=a.summarize_primary(cells,"known",manifest,draws=100)["contrasts"][0]["effect"]
        self.assertAlmostEqual(known-fresh,1/6)
        secondary=a.planned_secondary_contrasts(cells,manifest)
        comparisons=[x for x in secondary["contrasts"] if x["kind"]=="known_minus_fresh" and x["word_set"]=="equal_intent" and x["condition"].startswith("imaginary_") and x["outcome"]=="M01"]
        self.assertTrue(comparisons)
        self.assertTrue(all(x["effect"]==0 for x in comparisons))

    def test_jsonl_corruption_is_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"broken.jsonl";p.write_text('{}\n{"bad":')
            with self.assertRaises(ValueError):a.read_jsonl(p)

    def test_all_secondary_outputs_serialize_and_bootstrap_repeats(self):
        manifest,_,_,_,cells,rows=fixture()
        primary=a.summarize_primary(cells,"fresh",manifest,draws=100)
        self.assertEqual(primary,a.summarize_primary(cells,"fresh",manifest,draws=100))
        tables,summaries,reuse=a.secondary_tables(rows,cells)
        contrasts=a.planned_secondary_contrasts(cells,manifest)
        repetition=a.repetition_summaries(cells)
        json.dumps(dict(primary=primary,tables=tables,summaries=summaries,reuse=reuse,contrasts=contrasts,repetition=repetition),allow_nan=False)
        self.assertTrue(any(r["features"] for r in repetition))
        self.assertTrue(any(c["kind"]=="generation_frame_interaction" for c in contrasts["contrasts"]))


if __name__=="__main__":unittest.main()
