import pickle,json,csv,numpy as np
from collections import Counter,defaultdict
A,B,txt=pickle.load(open('/home/claude/work/out/joined.pkl','rb'))
C={r['key']:r for r in csv.DictReader(open('/home/claude/c_arm/results/response_codes.csv'))}
assert set(C)==set(A) and all(C[k]['response_sha256']==A[k]['response_sha256'] for k in A)
keys=sorted(A);g=lambda k,f:A[k]['values'][f]
M={ # construct: (A getter, B getter, C getter)
 'description':(lambda k:g(k,'description_produced'),lambda k:int(B[k]['F_E']),lambda k:int(C[k]['E_description'])),
 'nonrecognition':(lambda k:int(g(k,'knowledge_limit')==1 or g(k,'external_negative')==1),lambda k:int(B[k]['F_nonrec']),lambda k:int(C[k]['nonrec_any'])),
 'nonrec_without_description':(lambda k:g(k,'nonrecognition_without_description'),lambda k:int(B[k]['F_N']),lambda k:int(C[k]['N_nonrecognition_without_description'])),
 'unmarked_description':(lambda k:g(k,'unmarked_target_description'),lambda k:int(B[k]['F_U']),lambda k:int(C[k]['U_unmarked_description'])),
}
def kap(x,y):
    p=[(a,b) for a,b in zip(x,y) if a is not None and b is not None];n=len(p)
    po=sum(a==b for a,b in p)/n;pa=sum(a for a,b in p)/n;pb=sum(b for a,b in p)/n;pe=pa*pb+(1-pa)*(1-pb)
    return dict(n=n,agree=po,kappa=(po-pe)/(1-pe),rate_x=pa,rate_y=pb,x_only=sum(a==1 and b==0 for a,b in p),y_only=sum(a==0 and b==1 for a,b in p))
out={'pairwise':{},'rates':{}}
for name,(fa,fb,fc) in M.items():
    va=[fa(k) for k in keys];vb=[fb(k) for k in keys];vc=[fc(k) for k in keys]
    out['pairwise'][name]={'A_B':kap(va,vb),'A_C':kap(va,vc),'B_C':kap(vb,vc)}
    print(name,' '.join(f"{p}: k={v['kappa']:.2f} agr={v['agree']:.2f}" for p,v in out['pairwise'][name].items()),'| rates A %.3f B %.3f C %.3f'%(np.mean([x for x in va if x is not None]),np.mean(vb),np.mean(vc)))
    out['rates'][name]=dict(A=float(np.mean([x for x in va if x is not None])),B=float(np.mean(vb)),C=float(np.mean(vc)))
# holdout
pick=json.load(open('/home/claude/c_arm/holdout_keys.json'));lab=json.load(open('/home/claude/c_arm/holdout_labels.json'))['labels']
pool=[k for k in keys if g(k,'description_produced') is not None]
cell=lambda k:(g(k,'description_produced'),int(B[k]['F_E']))
pop=Counter(cell(k) for k in pool);samp=Counter(cell(k) for k in pick)
wt={k:(pop[cell(k)]/len(pool))/(samp[cell(k)]/len(pick)) for k in pick}
T={}
for k,l in zip(pick,lab):
    d,r,m=l.split(',');desc=int(d in 'YH');R=int(r=='Y')
    T[k]=dict(description=desc,nonrecognition=R,nonrec_without_description=int(R and not desc),unmarked_description=int(desc and not R and m=='N'),unmarked_echo=int(desc and not R and m in('N','E')),D=d)
out['holdout']={'n':len(pick),'strata':{str(k):[samp[k],pop[k]] for k in samp},'scores':{}}
print('\nHOLDOUT n=%d strata(sample,pop) %s'%(len(pick),{k:(samp[k],pop[k]) for k in samp}))
def acc(name,f,arm,truth=None):
    truth=truth or name;ok=w=tp=fp=fn=0;raw=0;n=0
    for k in pick:
        v=f(k)
        if v is None:continue
        t=T[k][truth];n+=1;raw+=(v==t);ok+=wt[k]*(v==t);w+=wt[k];tp+=(v==1 and t==1);fp+=(v==1 and t==0);fn+=(v==0 and t==1)
    out['holdout']['scores'].setdefault(name,{})[arm]=dict(n=n,raw_correct=raw,weighted_accuracy=ok/w,false_pos=fp,false_neg=fn,true_pos=tp)
    return f"{arm}: {raw}/{n} raw, {ok/w:.3f} weighted, FP {fp} FN {fn}"
for name,(fa,fb,fc) in M.items():print(f'{name:28}',acc(name,fa,'A'),'|',acc(name,fb,'B'),'|',acc(name,fc,'C'))
print('unmarked (echo discounted)    ',acc('unmarked_echo',lambda k:int(C[k]['U_unmarked_discounting_prompt_echo']),'C'))
print('A personal-only nonrec        ',acc('nonrecognition_personal_only',lambda k:g(k,'knowledge_limit'),'A','nonrecognition'))
# where C errs
for k,l in zip(pick,lab):
    t=T[k];c=dict(description=int(C[k]['E_description']),nonrecognition=int(C[k]['nonrec_any']),unmarked_description=int(C[k]['U_unmarked_description']))
    bad=[n for n in c if c[n]!=t[n]]
    if bad:print('  C miss',pick.index(k),l,C[k]['response_type'],bad,C[k]['fragile'])
# substitute
print('label S:',[ (pick.index(k),C[k]['response_type']) for k in pick if T[k]['D']=='S'])
# aggregate patterns three-way
grp={'claude-sonnet-4-6':'Anthropic','claude-haiku-4-5':'Anthropic','claude-sonnet-5-5':'Anthropic','claude-haiku-5-5':'Anthropic','gpt-5.4-mini':'OpenAI','gpt-5.4-nano':'OpenAI','gpt-6-sol':'OpenAI','gpt-6-luna':'OpenAI'}
fresh=[k for k in keys if A[k]['batch']=='fresh'];sub=[k for k in fresh if A[k]['framing'] in('real','type_of')]
def rate(ks,f):
    v=[f(k) for k in ks];v=[x for x in v if x is not None];return float(np.mean(v))
out['framing']={};out['models']={};out['contrasts']={}
for name,fs in M.items():
    out['framing'][name]={fr:[rate([k for k in fresh if A[k]['framing']==fr],f) for f in fs] for fr in ['neutral','real','type_of','imaginary']}
    out['models'][name]={m:[rate([k for k in sub if A[k]['model']==m],f) for f in fs] for m in grp}
    out['contrasts'][name]={'imaginary-real':[out['framing'][name]['imaginary'][i]-out['framing'][name]['real'][i] for i in range(3)],
      'type_of-real':[out['framing'][name]['type_of'][i]-out['framing'][name]['real'][i] for i in range(3)],
      'Anthropic-OpenAI':[rate([k for k in sub if grp[A[k]['model']]=='Anthropic'],f)-rate([k for k in sub if grp[A[k]['model']]=='OpenAI'],f) for f in fs]}
    print(name,{c:[round(x,2) for x in v] for c,v in out['contrasts'][name].items()})
    print('   models',{m:[round(x,2) for x in v] for m,v in out['models'][name].items()})
# C class vs B class
x=Counter((C[k]['response_type'],B[k]['response_class']) for k in keys);out['C_vs_B_class']={f'{a}|{b}':v for (a,b),v in x.items()}
ct=sorted({a for a,b in x});bt=sorted({b for a,b in x});print(' '*28,bt)
for a in ct:print(f'{a:28}',[x[(a,b)] for b in bt])
# who does C side with on A/B description disagreements
d=Counter((g(k,'description_produced'),int(B[k]['F_E']),int(C[k]['E_description'])) for k in pool);print('A,B,C description triples',dict(d));out['triples']={str(k):v for k,v in d.items()}
out['C_types_by_model']={m:dict(Counter(C[k]['response_type'] for k in sub if A[k]['model']==m)) for m in grp}
json.dump(out,open('/home/claude/work/out/three.json','w'),indent=1)
