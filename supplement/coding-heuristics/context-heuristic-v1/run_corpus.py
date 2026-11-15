"""Verify a frozen heuristic, score the release, export audit-ready observations.

Uses only Python's standard library. Does not contact any service or change
source archives. Existing output directories are rejected.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import zipfile
from heuristic import score, ROOT, VERSION, FIELDS

RAW_SHA='f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6'
OUTCOMES=['description_produced','target_description_produced','nonrecognition_without_description','unmarked_target_description','target_unqualified_description']
MEASURES=FIELDS+OUTCOMES


def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def require(ok,msg):
    if not ok:raise ValueError(msg)


def check_freeze(root=ROOT):
    f=json.loads((root/'FREEZE.json').read_text())
    claimed=f['freeze_sha256'];copy=dict(f);del copy['freeze_sha256']
    require(digest(copy)==claimed,'Freeze manifest hash mismatch')
    for name,h in f['files'].items():require(sha(root/name)==h,'Frozen file changed: '+name)
    require(f['version']==VERSION,'Version differs from freeze')
    return f


def load_raw(path):
    require(sha(path)==RAW_SHA,'Raw archive checksum mismatch')
    with zipfile.ZipFile(path) as z:
        names=z.namelist();require(len(names)==len(set(names)),'Duplicate archive member')
        for line in z.read('SHA256SUMS.txt').decode().splitlines():
            if not line.strip():continue
            h,n=line.split(None,1);n=n.strip().replace('\\','/')
            require(hashlib.sha256(z.read(n)).hexdigest()==h,'Release member checksum: '+n)
        freeze=json.loads(z.read('data/freeze.json'));fc=dict(freeze);h=fc.pop('manifest_sha256')
        require(digest(fc)==h,'Collection manifest mismatch')
        plan={(b,m,t['trial_id']):t for b,models in freeze['batches'].items() for m,ts in models.items() for t in ts}
        rows=[]
        for name in sorted(names):
            if name.startswith(('data/raw/fresh/','data/raw/known/')) and name.endswith('.jsonl'):
                rows.extend(json.loads(line) for line in z.read(name).decode().splitlines() if line.strip())
        keys=[(r['batch'],r['model_requested'],r['trial_id']) for r in rows]
        require(len(keys)==16000 and len(set(keys))==16000,'Response count or duplicate key')
        require(set(keys)==set(plan),'Schedule and exports differ')
        for k,r in zip(keys,rows):
            require(all(r[n]==v for n,v in plan[k].items()),'Schedule metadata mismatch')
            require(r['valid'] and r['terminal'] and r['complete'] and not r['truncated'],'Ineligible response')
            require(not any(r.get(x) for x in ['error','issue','protocol_violation','reasoning_tokens','thinking_blocks']),'Unexpected response issue')
        require(Counter(r['batch'] for r in rows)=={'fresh':9600,'known':6400},'Bank counts')
    return sorted(rows,key=lambda r:(r['batch'],r['model_requested'],r['trial_id'])),h


def rates(rows):
    """Source-balanced detection mass, unknown mass, and available-case rate.

    Within each source weight words equally, then records equally within word.
    Groupings retain balanced endpoints/conditions in the supplied corpus.
    """
    groups=defaultdict(lambda:defaultdict(list))
    for r in rows:groups[r['source']][r['word']].append(r)
    result={}
    for m in MEASURES:
        counts=Counter(r['values'][m] for r in rows)
        yes=unknown=0.0
        for words in groups.values():
            for rs in words.values():
                weight=1/(len(groups)*len(words)*len(rs))
                yes+=sum(r['values'][m]==1 for r in rs)*weight
                unknown+=sum(r['values'][m] is None for r in rs)*weight
        result[m]=dict(detected=counts[1],not_detected=counts[0],unresolved=counts[None],n=len(rows),
                       weighted_detected=yes,weighted_unresolved=unknown,
                       available_case_rate=yes/(1-unknown) if unknown<1-1e-12 else None,
                       unresolved_assignment_interval=[yes,min(1.0,yes+unknown)])
    return result


def pair_counts(values):
    c=Counter(values);n=len(values);available=c[0]+c[1]
    den=comb(available,2) if available>=2 else 0
    same=sum(comb(c[x],2) for x in (0,1) if c[x]>=2)
    total=comb(n,2) if n>=2 else 0
    return dict(n=n,detected=c[1],not_detected=c[0],unresolved=c[None],
                matching_resolved_pairs=same,resolved_pairs=den,all_pairs=total,
                pair_agreement=same/den if den else None,
                pair_coverage=den/total if total else None)


def run(archive,out):
    freeze=check_freeze()
    require(not out.exists(),'Output directory exists; preserve previous execution')
    records,collection_sha=load_raw(archive)
    out.mkdir(parents=True)
    rows=[];keys=[]
    with (out/'response_codes.jsonl').open('x',encoding='utf-8') as codes, (out/'evidence.jsonl').open('x',encoding='utf-8') as traces:
        for i,r in enumerate(records,1):
            s=score(r['prompt'],r['response'])
            k=[r['batch'],r['model_requested'],r['trial_id']];keys.append(k)
            values={f:s['findings'][f]['value'] for f in FIELDS};values.update(s['outcomes'])
            row=dict(key=k,batch=r['batch'],model=r['model_requested'],word=r['word'],condition=r['condition'],
                     rep=r['rep'],source=r['source_set_label'],framing=s['prompt']['framing'],category=s['prompt']['category'],
                     prompt_sha256=s['prompt_sha256'],response_sha256=s['response_sha256'],
                     values=values,qualifier_scope=s['qualifier_scope'],fictional_frame=s['fictional_frame'])
            codes.write(canonical(row)+'\n');traces.write(canonical(dict(key=k,**s))+'\n');rows.append(row)
            if i%4000==0:print(f'Scored {i}/16000',flush=True)
    summaries=[]
    for dims in [('batch',),('batch','framing'),('batch','model','framing')]:
        grouped=defaultdict(list)
        for r in rows:grouped[tuple(r[x] for x in dims)].append(r)
        for k,rs in sorted(grouped.items()):summaries.append(dict(group=dict(zip(dims,k)),measures=rates(rs)))
    dump(out/'detection_summary.json',summaries)
    contrasts=[]
    for bank in ['fresh','known']:
        frame_rates={f:rates([r for r in rows if r['batch']==bank and r['framing']==f]) for f in ['real','imaginary','type_of']}
        for f in ['imaginary','type_of']:
            for m in MEASURES:
                a,b=frame_rates[f][m],frame_rates['real'][m]
                contrasts.append(dict(batch=bank,contrast=f+'-real',measure=m,
                    available_case_difference=None if a['available_case_rate'] is None or b['available_case_rate'] is None else a['available_case_rate']-b['available_case_rate'],
                    unresolved_assignment_interval=[a['unresolved_assignment_interval'][0]-b['unresolved_assignment_interval'][1],a['unresolved_assignment_interval'][1]-b['unresolved_assignment_interval'][0]],
                    interpretation='Exploratory mechanical difference; not a confidence interval or original preregistered estimator'))
    dump(out/'exploratory_contrasts.json',contrasts)
    cells=defaultdict(list)
    for r in rows:cells[(r['batch'],r['word'],r['model'],r['condition'])].append(r)
    require(len(cells)==2560,'Unexpected cell count')
    cell_rows=[]
    with (out/'cell_consistency.jsonl').open('x',encoding='utf-8') as f:
        for k,rs in sorted(cells.items()):
            require(len(rs)==(5 if k[0]=='fresh' else 10),'Unexpected cell repetitions')
            c=dict(cell=list(k),source=rs[0]['source'],measures={m:pair_counts([r['values'][m] for r in rs]) for m in MEASURES})
            cell_rows.append(c);f.write(canonical(c)+'\n')
    pair_summary=[]
    for bank in ['fresh','known']:
        cs=[c for c in cell_rows if c['cell'][0]==bank]
        for m in MEASURES:
            sums={x:sum(c['measures'][m][x] for c in cs) for x in ['matching_resolved_pairs','resolved_pairs','all_pairs']}
            pair_summary.append(dict(batch=bank,measure=m,**sums,
                pair_agreement=sums['matching_resolved_pairs']/sums['resolved_pairs'] if sums['resolved_pairs'] else None,
                pair_coverage=sums['resolved_pairs']/sums['all_pairs']))
    dump(out/'consistency_summary.json',pair_summary)
    # This receipt is written last; its presence marks a completed validated run.
    receipt=dict(version=VERSION,freeze_sha256=freeze['freeze_sha256'],raw_archive_sha256=RAW_SHA,
                 collection_manifest_sha256=collection_sha,completed_utc=datetime.now(timezone.utc).isoformat(),
                 python=platform.python_version(),n=16000,cells=2560,banks={'fresh':9600,'known':6400},
                 key_columns=['batch','model_requested','trial_id'],ordered_keys_sha256=digest(keys),
                 raw_texts_modified=False,provider_calls=0,original_scores_overwritten=False,
                 files={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    dump(out/'execution.json',receipt)
    print(canonical(dict(n=receipt['n'],cells=receipt['cells'],freeze_sha256=receipt['freeze_sha256'])))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--raw-archive',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();run(args.raw_archive.resolve(),args.out.resolve())
