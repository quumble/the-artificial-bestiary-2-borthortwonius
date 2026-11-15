"""Validate the completed export and every quoted evidence span."""
import argparse
import json
from collections import Counter
from itertools import zip_longest
from pathlib import Path
from run_corpus import check_freeze,load_raw,sha,require,digest,MEASURES

def verify(archive,out):
    f=check_freeze();receipt=json.loads((out/'execution.json').read_text())
    require(receipt['freeze_sha256']==f['freeze_sha256'],'Execution used a different freeze')
    for name,h in receipt['files'].items():require(sha(out/name)==h,'Output changed: '+name)
    records,_=load_raw(archive)
    count=spans=unknown=0;keys=[];by_bank=Counter()
    with (out/'response_codes.jsonl').open() as a,(out/'evidence.jsonl').open() as b:
        for r,line,trace in zip_longest(records,a,b):
            require(r is not None and line is not None and trace is not None,'Output/source row counts differ')
            x=json.loads(line);t=json.loads(trace);k=[r['batch'],r['model_requested'],r['trial_id']]
            require(x['key']==t['key']==k,'Order/key mismatch');keys.append(k)
            require(x['response_sha256']==t['response_sha256']==__import__('hashlib').sha256(r['response'].encode()).hexdigest(),'Response identity mismatch')
            require(x['prompt_sha256']==t['prompt_sha256']==__import__('hashlib').sha256(r['prompt'].encode()).hexdigest(),'Prompt identity mismatch')
            require(set(x['values'])==set(MEASURES),'Wrong measure columns')
            ids={e['id'] for e in t['events']};require(len(ids)==len(t['events']),'Duplicate evidence IDs')
            for e in t['events']:
                require(0<=e['start']<e['end']<=len(r['response']),'Evidence out of bounds')
                require(e['text']==r['response'][e['start']:e['end']],'Evidence quotation mismatch');spans+=1
            for name,v in t['findings'].items():
                require(v['value'] in [0,1,None] and x['values'][name]==v['value'],'Feature mismatch')
                require(set(v['evidence'])<=ids,'Evidence reference missing')
                require(v['value']==0 or bool(v['evidence']),'Detected/unresolved feature lacks evidence')
            require(all(x['values'][name]==v for name,v in t['outcomes'].items()),'Derived outcome mismatch')
            count+=1;by_bank[r['batch']]+=1;unknown+=bool(t['unresolved_fields'])
    require(digest(keys)==receipt['ordered_keys_sha256'],'Ordered-key hash mismatch')
    with (out/'cell_consistency.jsonl').open() as f:cells=[json.loads(l) for l in f]
    require(len(cells)==2560 and len({tuple(c['cell']) for c in cells})==2560,'Cell identity count')
    return dict(passed=True,responses=count,evidence_spans=spans,cells=len(cells),banks=dict(by_bank),responses_with_unresolved_fields=unknown,freeze_sha256=receipt['freeze_sha256'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw-archive',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();print(json.dumps(verify(args.raw_archive,args.out),indent=2))
