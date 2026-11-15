"""Record of how the three arms were scored against the human labels.

Not runnable from this folder as it stands: joined.pkl is a local join of the
context arm's response_codes.jsonl, the mechanical arm's coded_responses.csv and
the response texts, keyed by batch|model|trial_id. Its results are stored in
human_labels.json under scores_against_human.
"""
import pickle,json,csv
from collections import Counter
A,B,txt=pickle.load(open('joined.pkl','rb'))
C={r['key']:r for r in csv.DictReader(open('../zoned-heuristic-v1/results/response_codes.csv'))}
pick=json.load(open('../zoned-heuristic-v1/holdout_keys.json'));mine=json.load(open('../zoned-heuristic-v1/holdout_labels.json'))['labels']
H=json.load(open('human_labels_raw.json'));g=lambda k,f:A[k]['values'][f]
def T(d,r,m):
    desc=int(d in 'YH');R=int(r=='Y')
    return dict(description=desc,nonrecognition=R,nonrec_without_description=int(R and not desc),unmarked_description=int(desc and not R and m=='N'),unmarked_echo=int(desc and not R and m in('N','E')))
hum={};cl={}
for i,k in enumerate(pick):
    r,d,m,fl,ms=H[str(i)].split(',');hum[k]=T(d,r,m);hum[k].update(D=d,R=r,M=m,flag=fl,ms=int(ms))
    d2,r2,m2=mine[i].split(',');cl[k]=T(d2,r2,m2);cl[k].update(D=d2,R=r2,M=m2)
ms=sorted(hum[k]['ms'] for k in pick);print('total min',sum(ms)/60000,'median s',ms[42]/1000)
print('Human D',Counter(hum[k]['D'] for k in pick),'R',Counter(hum[k]['R'] for k in pick),'M',Counter(hum[k]['M'] for k in pick))
# human vs claude reader
cons=['description','nonrecognition','nonrec_without_description','unmarked_description','unmarked_echo']
def kap(x,y):
    n=len(x);po=sum(a==b for a,b in zip(x,y))/n;pa=sum(x)/n;pb=sum(y)/n;pe=pa*pb+(1-pa)*(1-pb);return po,(po-pe)/(1-pe) if pe<1 else 1
for c in cons:
    po,k_=kap([hum[k][c] for k in pick],[cl[k][c] for k in pick]);print(f'human vs claude-reader {c:28} agree {po*84:.0f}/84 kappa {k_:.2f}')
print('raw code agreement D',sum(hum[k]['D']==cl[k]['D'] for k in pick),'R',sum(hum[k]['R']==cl[k]['R'] for k in pick),'M (both desc)',sum(hum[k]['M']==cl[k]['M'] for k in pick if hum[k]['D'] in 'YH' and cl[k]['D'] in 'YH'),'of',sum(1 for k in pick if hum[k]['D'] in 'YH' and cl[k]['D'] in 'YH'))
for i,k in enumerate(pick):
    if (hum[k]['D'],hum[k]['R'],hum[k]['M'])!=(cl[k]['D'],cl[k]['R'],cl[k]['M']):print('  diff',i,'human',hum[k]['R'],hum[k]['D'],hum[k]['M'],'| claude',cl[k]['R'],cl[k]['D'],cl[k]['M'],'|',A[k]['framing'],A[k]['word'],'flag' if hum[k]['flag']=='1' else '')
# instruments vs human
pool=[k for k in A if g(k,'description_produced') is not None];cell=lambda k:(g(k,'description_produced'),int(B[k]['F_E']))
pop=Counter(cell(k) for k in pool);samp=Counter(cell(k) for k in pick);wt={k:(pop[cell(k)]/len(pool))/(samp[cell(k)]/len(pick)) for k in pick}
M={'description':(lambda k:g(k,'description_produced'),lambda k:int(B[k]['F_E']),lambda k:int(C[k]['E_description'])),
 'nonrecognition':(lambda k:int(g(k,'knowledge_limit')==1 or g(k,'external_negative')==1),lambda k:int(B[k]['F_nonrec']),lambda k:int(C[k]['nonrec_any'])),
 'nonrec_without_description':(lambda k:g(k,'nonrecognition_without_description'),lambda k:int(B[k]['F_N']),lambda k:int(C[k]['N_nonrecognition_without_description'])),
 'unmarked_description':(lambda k:g(k,'unmarked_target_description'),lambda k:int(B[k]['F_U']),lambda k:int(C[k]['U_unmarked_description'])),
 'unmarked_echo':(None,None,lambda k:int(C[k]['U_unmarked_discounting_prompt_echo']))}
out={}
for name,fs in M.items():
    row=[]
    for arm,f in zip('ABC',fs):
        if f is None:row.append('   -   ');continue
        n=raw=ok=w=fp=fn=0
        for k in pick:
            v=f(k)
            if v is None:continue
            t=hum[k][name];n+=1;raw+=v==t;ok+=wt[k]*(v==t);w+=wt[k];fp+=(v==1 and t==0);fn+=(v==0 and t==1)
        out.setdefault(name,{})[arm]=dict(n=n,correct=raw,weighted=ok/w,fp=fp,fn=fn);row.append(f'{arm} {raw}/{n} w={ok/w:.3f} FP{fp} FN{fn}')
    print(f'{name:28}',' | '.join(row))
print('C misses vs human:')
for i,k in enumerate(pick):
    c=dict(description=int(C[k]['E_description']),nonrecognition=int(C[k]['nonrec_any']),unmarked_description=int(C[k]['U_unmarked_description']))
    bad=[n for n in c if c[n]!=hum[k][n]]
    if bad:print('  ',i,hum[k]['R'],hum[k]['D'],hum[k]['M'],C[k]['response_type'],bad)
print('human S items -> C type',[(i,C[k]['response_type'],C[k]['substitute_description']) for i,k in enumerate(pick) if hum[k]['D']=='S'])
json.dump(dict(scores=out,strata={str(k):[samp[k],pop[k]] for k in samp}),open('scores_vs_human.json','w'),indent=1)
