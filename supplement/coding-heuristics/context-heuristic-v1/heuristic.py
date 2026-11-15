"""Bestiary contextual heuristic, deterministic, offline, standard library only.

Values are mechanical detections: 1 detected, 0 not detected, None unresolved.
Neither 0 nor 1 is a verified semantic judgment. Raw evidence uses Python
Unicode code-point offsets [start, end). See METHOD.md for scope assumptions.
"""
from __future__ import annotations
import hashlib
import json
import re
import unicodedata
from pathlib import Path

VERSION = 'bestiary-context-heuristic/1.0.0'
ROOT = Path(__file__).resolve().parent
FIELDS = [f['id'] for f in json.loads((ROOT/'codebook.json').read_text())['fields']]


def sha_text(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def normalize(text):
    out, positions = [], []
    for i, char in enumerate(text):
        if char in '*_`#':
            continue
        char = {'’':"'", '‘':"'", 'ʼ':"'", '“':'"', '”':'"', '\r':'\n'}.get(char, char)
        for c in unicodedata.normalize('NFKC', char).casefold():
            out.append(c)
            positions.append((i, i+1))
    return ''.join(out), positions


def metadata(prompt):
    m = re.fullmatch(r'Describe (?:a|an) ([A-Za-z]+)\.(?: It is (?:a|an) (real|imaginary|type of) (animal|object|idea)\.)?', prompt)
    if not m:
        raise ValueError('Unsupported prompt template; do not silently infer metadata')
    return dict(target=m[1], framing=(m[2] or 'neutral').replace(' ', '_'), category=m[3])


# Inventories were specified using the prior boundary work and 12 development
# responses. None was selected using full-corpus rates or the independent arm.
STATIC = {
 'knowledge_limit': r"\bi(?: am|'m) not familiar\b|\bi (?:do not|don't) (?:recognize|recognise|know)\b|\bi (?:cannot|can't|am unable to) (?:verify|confirm|identify)\b|\b(?:species|terms?|words?) i know of\b|\bi (?:have not|haven't) (?:heard of|encountered|verified)\b",
 'external_negative': r"\bno such (?:animal|object|thing|species|entity) exists\b|\b(?:does not|doesn't) exist\b|\b(?:does not|doesn't) appear in (?:standard|any|the)\b|\b(?:standard (?:classifications|references)|reference works) (?:contain|have) no\b|\b(?:is not|isn't|not) (?:a |an )?(?:widely recognized|well-known|established|recognized|documented)\b",
 'premise_retention': r'\bthe (?:real|actual) (?:animal|object|thing)(?: you mean)?\b|\b(?:help )?identify the (?:real )?(?:animal|object|thing)\b',
 'construction': r"\b(?:of my own invention|i (?:am inventing|invented)|i'm inventing|i made (?:this(?: creature| animal| object| idea| description)?|it) up|(?:here is|here's) (?:a |an )?invented (?:description|creature|animal|object|idea)|let's imagine|let us imagine|could be imagined|(?:here is|here's) how (?:i would|i'd) picture it|(?:an? |simple )?invented description could be)\b",
 'interpretation': r'\b(?:one (?:possible|plausible) interpretation|my best guess|the name suggests|i propose (?:the name|the term|to call))\b',
 'whole_verification': r"\bi (?:cannot|can't|am unable to) (?:verify|confirm) (?:this|that|the) (?:description|account|interpretation|definition|identity|existence)\b",
 'attribute_verification': r"\bi (?:cannot|can't|am unable to) (?:verify|confirm) (?:where|when|how|its (?:habitat|size|diet|color|colour|age)|the (?:habitat|size|diet|color|colour|age))\b",
 'refusal': r"\bi (?:will not|won't|do not want to|don't want to|would rather not|'d rather not|want to avoid) invent(?:ing)?\b|\bi'd rather not invent\b",
 'request': r'\b(?:could|can|would|will) you (?:please )?(?:provide|share|tell|give|clarify)\b[^.!?\n]*|\b(?:please (?:share|provide)|where did you (?:hear|see|encounter)|what field or tradition|(?:can you )?tell me where)\b[^.!?\n]*',
 'offer': r"\b(?:i can (?:also )?(?:invent|create|make up)|would you like me to (?:invent|create|develop)|want me to (?:invent|create))\b[^.!?\n]*",
 'reported': r'\b(?:is|are|was|were) (?:thought|believed|said) to\b|\bnobody agrees\b|\bscientists (?:have )?speculated\b',
 'grounding': r'\b(?:first )?(?:documented|discovered|catalogued|cataloged|recorded) (?:by|in)\b|\b(?:scientists|researchers|naturalists) (?:have |had )?(?:documented|discovered|described|recorded|speculated|reported)\b|\baccording to\b[^.!?\n]{1,80}|\b(?:traditionally|in mythology|legend|local saying|folk tradition|etymology|derived from|old word meaning)\b|\bits name (?:is thought to )?comes? from\b|\b(?:widely used|commonly called|used in philosophy|recognized in biology)\b|https?://[^\s<>]+|\b10\.\d{4,9}/[^\s<>]+',
 'explicit': r'\b(?:actually exists?|does exist|really exists?|exists? in the real world|is (?:a |an )?real (?:animal|object|species|thing)|is (?:a |an )?recognized species|widely used term|established term|standard term|recognized term|conventionally used|commonly known as)\b',
 'escape': r'\b(?:outside (?:this |the )?(?:story|fiction|fictional world)|in (?:the )?(?:actual|real) world|in reality)\b',
 'fiction_frame': r'\bin this (?:imagined|fictional|invented) world\b|\b(?:this|the) (?:whole |entire )?(?:account|description|creature|animal|object|idea) (?:is|was) (?:entirely )?(?:fictional|imaginary|invented|made[- ]up)\b',
 'literal_cue': r'\b(?:fictional|imaginary|made[- ]up|hypothetical|invented|may|might|could|perhaps|possibly|probably|likely|if|assuming|suppose|supposing|uncertain|unverified)\b',
}
META_CONTENT = r'\b(?:words?|names?|terms?|spelling|misspelling|regional name|local name|fictional setting|game source|video game|tabletop rpg|from a book)\b'
CONCRETE = r'\b(?:feathers?|fur|scales|wings?|legs?|tail|pouch|beak|claws?|eyes|body|anatomy|limbs?|feeds?|eats?|breathes?|hunts?|nests?|offspring)\b'
CATEGORIES = {'animal':r'animal|creature|mammal|bird|reptile|fish|marsupial', 'object':r'object|tool|device|artifact|instrument', 'idea':r'idea|concept|principle|thought|doubt'}


def score(prompt, response):
    if not isinstance(response, str) or not response.strip():
        raise ValueError('Empty or non-text response')
    meta = metadata(prompt)
    norm, mapping = normalize(response)
    target = re.escape(meta['target'].casefold())
    named = rf"(?:[\"']?{target}(?:s|es|'s|s')?[\"']?)"
    subject = rf"(?:{named}|it|they|this (?:animal|creature|object|idea)|the (?:animal|creature|object|idea))"
    # Token quotes used around names are not quoted assertions.
    quotes = [(m.start(),m.end()) for m in re.finditer(r'''"[^"\n]+"|(?<!\w)'[^'\n]+'(?!\w)''', norm) if len(re.findall(r'\w+',m[0]))>=3]
    for m in re.finditer(r'`[^`\n]+`',response):
        ix=[i for i,(a,b) in enumerate(mapping) if m.start()<=a and b<=m.end()]
        if ix and len(re.findall(r'\w+',m[0]))>=3:quotes.append((min(ix),max(ix)+1))
    segments = [(m.start(),m.end(),m[0]) for m in re.finditer(r'[^.!?\n]+[.!?]?',norm)]
    events = []

    def context(a,b):
        seg = next(((x,y,t) for x,y,t in segments if x<=a<y), (0,len(norm),norm))
        flags=[]
        if any(a>=x and b<=y for x,y in quotes): flags.append('quoted_assertion')
        if seg[2].rstrip().endswith('?'): flags.append('question')
        before=norm[max(seg[0],a-90):a]
        if re.search(r"\b(?:not|never|no|isn't|wasn't|don't|cannot|can't)\b(?:\s+\w+){0,3}\s*$",before): flags.append('preceding_negation')
        if re.search(r'\b(?:for example|the sign reads|example sentence|do not say|don\x27t say)\b',before): flags.append('illustrative_context')
        return flags,seg

    def add(family,m,extra=(), suppress_neg=True, suppress_question=True):
        a,b=m.span(); flags,seg=context(a,b)
        flags=sorted(set(flags)|set(extra))
        blocking={'quoted_assertion','illustrative_context'}
        if suppress_neg: blocking.add('preceding_negation')
        if suppress_question: blocking.add('question')
        raw_a,raw_b=mapping[a][0],mapping[b-1][1]
        e=dict(rule='H1-'+family, family=family, start=raw_a,end=raw_b,text=response[raw_a:raw_b],
               flags=flags, admitted=not bool(set(flags)&blocking), _start=a,_end=b,_segment=seg)
        events.append(e)
        return e

    for family,pattern in STATIC.items():
        for m in re.finditer(pattern,norm):
            add(family,m,suppress_neg=family not in {'knowledge_limit','external_negative','refusal','whole_verification','attribute_verification'},
                suppress_question=family not in {'request','offer','literal_cue'})

    def admitted(f): return [e for e in events if e['family']==f and e['admitted']]
    # A knowledge assertion does not become an external assertion merely because
    # its complement contains "established term" or "recognized species".
    for e in events:
        if e['family'] in {'explicit','external_negative','grounding'}:
            same=[k for k in admitted('knowledge_limit') if k['_segment'][:2]==e['_segment'][:2] and k['_start']<=e['_start']]
            if same:
                e['admitted']=False; e['flags'].append('inside_knowledge_limit')
        if e['family']=='request' and not re.search(r'\b(?:source|context|evidence|reference|where|word|term|name|field|tradition|spelling)\b',e['_segment'][2]):
            e['admitted']=False;e['flags'].append('unrelated_request')

    # Separate offers never retroactively become construction acknowledgments.
    offers=admitted('offer')
    story_events=[]
    for e in events:
        if e['family'] in {'construction','fiction_frame','grounding','explicit'} and any(o['_segment'][:2]==e['_segment'][:2] for o in offers):
            e['admitted']=False;e['flags'].append('separate_offer')
        if e['family']=='construction' and re.search(r'\b(?:invented|inventing|made up) (?:an? |the |this )?(?:story|tale|plot|legend)\b',e['_segment'][2]):
            story_events.append(dict(e,family='separate_story',rule='H1-separate_story',flags=list(e['flags'])))
            e['admitted']=False;e['flags'].append('story_creation_not_subject')
    events.extend(story_events)

    substitutes=[]
    for m in re.finditer(r"\bdid you mean (?:a |an |the )?[\"']?([a-z][a-z-]+)[\"']?\s*\?",norm):
        if m[1] not in {'it','this','that','something',meta['target'].lower()}:
            substitutes.append(m[1]);add('substitute_proposal',m,suppress_question=False)
    for m in re.finditer(r"\bif so,?\s+(?:it is|it's|its)\b[^.!?\n]+",norm):
        if any(0<=m.start()-p['_end']<120 for p in admitted('substitute_proposal')):
            add('substitute_description',m)

    dynamic = {
      'target_modal':rf'\b{subject}\s+(?:could|may|might|would) (?:be|mean|refer to|exist)\b[^.!?\n]*',
      'target_condition':rf'\b(?:if|assuming|suppose|supposing) (?:such (?:an? )?(?:animal|creature|object|idea)|(?:an? |the )?{named}) (?:exists?|existed|were real|is real)\b',
      'attribute_modal':rf'\b{subject}\s+(?:may|might|probably|possibly|perhaps)\s+(?:live|hide|eat|grow|have|carry|weigh|be found|come from)\b[^.!?\n]*',
      'status_negative':rf'\b{subject}\s+(?:is not|isn\x27t|was not|wasn\x27t) (?:imaginary|fictional|made[- ]up)\b',
      'target_fiction':rf'\b{subject}\s+(?:is|was) (?:an? )?(?:purely |entirely )?(?:fictional|imaginary|hypothetical|invented|made[- ]up)\b[^.!?\n]*',
      'name_proposal':rf'\b{subject}\s+(?:may|might|could) (?:be|mean|refer to)\b[^.!?\n]*{META_CONTENT}[^.!?\n]*',
    }
    for family,pattern in dynamic.items():
        for m in re.finditer(pattern,norm):add(family,m,suppress_neg=family!='status_negative')

    # Descriptions need a referent-bound predicate; a mere category echo or
    # metalinguistic possibility is not sufficient. Pronouns assume the prompt's
    # referent unless a substitute was proposed (then deliberately unresolved).
    descs=[]; desc_uncertain=[]
    pat=rf"\b(?P<subject>{subject})(?:\s+|(?='s\b))(?P<verb>'s|is|are|was|were|means|refers to|(?:could|may|might|would) (?:be|hide|live|eat|have|carry)|has|have|carries|carry|lives|live|eats|eat|feeds|grows|weighs|uses|contains|consists|resembles)\b(?P<tail>[^.!?\n]*)"
    for m in re.finditer(pat,norm):
        e=add('description_candidate',m,suppress_neg=False)
        tail=m['tail'].strip(' :,-');verb=m['verb'];sub=m['subject'].strip('"\'')
        if verb=="'s":verb='is'
        reason=None
        if re.match(r"(?:not|no|never|unknown|unfamiliar|n't)\b",tail): reason='negative_predicate'
        elif re.search(META_CONTENT,tail) and not re.search(r'\b(?:with|that|which|for)\b.+\b(?:feathers|wings|behavior|behaviour|function|doubt|contradiction)\b',tail): reason='name_or_term_content'
        elif re.search(r'\b(?:possibilities|possible explanations)\b',norm[:m.start()]) and re.search(r'\b(?:obscure|recently described|regional|local|fictional)\b',tail) and not re.search(CONCRETE,tail):reason='listed_identity_possibility'
        elif re.search(r'\b(?:documented|discovered|catalogued|cataloged|recorded)\b',tail[:40]): reason='grounding_only'
        elif re.fullmatch(r'(?:an? |the )?(?:(?:real|imaginary|fictional|hypothetical|invented|made[- ]up|type of) )*(?:animal|object|idea|creature|species|thing|entity)?',tail):
            # Bare category is informative for neutral prompts if narrower than
            # an entity, and for a requested different category.
            cat=re.search(r'\b(animal|object|idea)\b$',tail)
            if not cat or cat[1]==meta['category']:reason='status_or_prompt_echo_only'
        elif verb in {'is','are','was','were'} and not re.match(r"(?:a |an |the |[\"']|red\b|blue\b|green\b|small\b|large\b|nocturnal\b|covered\b|used\b|found\b|roughly\b|about\b|soft\b)",tail):reason='unsupported_copular_tail'
        if any(o['_start']<=m.start()<=o['_end'] for o in offers):reason='separate_offer'
        if e['admitted'] and reason is None:
            if substitutes and sub in {'it','they','the animal','the object','the idea','this creature'}:
                e['admitted']=False;e['flags'].append('substitute_pronoun_scope');desc_uncertain.append(e)
            else:
                e['family']='target_description';e['rule']='H1-target_description';descs.append(e)
        elif reason:
            e['admitted']=False;e['flags'].append(reason)

    # Explicit anatomy allows category blends even if the head repeats 'idea'.
    for m in re.finditer(rf'\b(?:{named}|it|its|their|they)\b[^.!?\n]{{0,160}}{CONCRETE}[^.!?\n]*',norm):
        add('bodily_content',m)

    whole=admitted('construction')+admitted('interpretation')+admitted('whole_verification')+admitted('target_modal')+admitted('target_condition')+admitted('name_proposal')+admitted('target_fiction')+admitted('fiction_frame')
    fictional=meta['framing']=='imaginary' or bool(admitted('construction')+admitted('target_fiction')+admitted('fiction_frame'))
    grounded=admitted('grounding')
    explicit=admitted('explicit')
    escapes=admitted('escape')
    outside=lambda e:any(x['_segment'][:2]==e['_segment'][:2] for x in escapes)
    actual_explicit=[e for e in explicit if not fictional or outside(e)]
    actual_grounding=[e for e in grounded if not fictional or outside(e)]
    lore=[e for e in grounded+admitted('reported') if fictional and not outside(e)]

    findings={f:dict(value=0,evidence=[],reason='No admitted rule in the frozen inventory') for f in FIELDS}
    def assign(field,ev,reason=None,value=1):
        if ev or value is None:
            findings[field]=dict(value=value,evidence=ev,reason=reason or 'Admitted frozen rule')

    assign('target_description',descs)
    if not descs and desc_uncertain and not admitted('substitute_description'):
        assign('target_description',desc_uncertain,'Pronoun referent after substitute proposal unresolved',None)
    assign('substitute_description',admitted('substitute_description'))
    assign('knowledge_limit',admitted('knowledge_limit'))
    assign('external_negative',admitted('external_negative'))
    retained=[e for e in admitted('premise_retention') if not any(c['_segment'][:2]==e['_segment'][:2] for c in admitted('target_condition'))]
    assign('premise_retention',retained)
    assign('target_qualification',whole)
    assign('construction_acknowledgment',admitted('construction')+admitted('interpretation')+admitted('name_proposal'))
    assign('explicit_existence',actual_explicit)
    assign('real_world_grounding',actual_grounding)
    assign('pb_worldbuilding',lore)
    conflicting=admitted('construction')+admitted('target_fiction')+admitted('fiction_frame')+admitted('target_condition')
    if conflicting and actual_explicit:
        if re.search(r'\b(?:correction|i retract|i take that back|i meant|to correct myself)\b',norm):
            assign('mixed_status',conflicting+actual_explicit,'Explicit revision marker; status conflict resolution unsupported',None)
        else:
            assign('mixed_status',conflicting+actual_explicit,'Hypothetical/construction act plus explicit actual-world assertion; no first/last rule')

    # Broad qualification includes attribute/offer acts; raw modal tokens alone
    # do not. Bare could-lift and biological if-threatened are excluded below.
    qgroups={
      'target':whole+admitted('status_negative')+admitted('external_negative')+actual_explicit,
      'attribute':admitted('attribute_verification')+admitted('attribute_modal')+admitted('reported'),
      'name_or_knowledge':admitted('knowledge_limit')+admitted('name_proposal'),
      'separate_offer_request':admitted('offer')+admitted('request')+admitted('refusal')+admitted('separate_story'),
    }
    qev=[e for es in qgroups.values() for e in es]
    unresolved_cues=[]
    for e in admitted('literal_cue'):
        if any(q['_start']<=e['_start']<q['_end'] for q in qev):continue
        seg=e['_segment'][2]
        if e['text'].casefold()=='could' and re.search(r'\bcould (?:lift|carry|run|fly|swim|hold|reach)\b',seg):continue
        if e['text'].casefold()=='if' and re.search(r'\b(?:if (?:threatened|hungry|startled|disturbed|attacked|touched)|as if)\b',seg):continue
        if re.search(r'\b(?:could|can|would) you\b',seg):continue
        if re.search(r'\bif (?:you|people|understood|the marsh(?:es)?|its habitat)\b',seg):
            if re.search(r'\bif (?:the marsh(?:es)?|its habitat)\b',seg):qgroups['attribute'].append(e);qev.append(e)
            continue
        if any(o['_segment'][:2]==e['_segment'][:2] for o in offers):continue
        unresolved_cues.append(e)
    assign('qualifier_anywhere',qev)
    if not qev and unresolved_cues:assign('qualifier_anywhere',unresolved_cues,'Literal candidate with unsupported sense or scope',None)
    if not whole and unresolved_cues:assign('target_qualification',unresolved_cues,'Possible target/attribute scope not resolved by inventory',None)

    # Bare definition is a presentation act, not external substantiation.
    bare=[e for e in descs if re.search(rf'\b{named}\s+(?:is|are|was|were|means|refers to)\b',norm[e['_start']:e['_end']])]
    if bare and not fictional and findings['target_qualification']['value']==0:
        assign('implicit_existence',bare)
    elif bare and not fictional and findings['target_qualification']['value'] is None:
        assign('implicit_existence',bare+unresolved_cues,'Definition qualification scope unresolved',None)

    if meta['category']:
        mismatch=[];metaphors=[]
        for e in descs:
            tail=norm[e['_start']:e['_end']]
            head=re.split(r'\b(?:is|are|was|were|be)\b',tail,maxsplit=1)[-1]
            head=re.split(r'\b(?:like|as if|resembles)\b',head,maxsplit=1)[0][:160]
            asserted={c for c,p in CATEGORIES.items() if re.search(rf'\b(?:{p})\b',head)}
            if asserted and meta['category'] not in asserted:mismatch.append(e)
        if meta['category'] in {'idea','object'}:
            body=admitted('bodily_content')
            for e in body:
                if re.search(r'\b(?:living concept|metaphor|metaphorical|symbolic|as if|like a thought|doubt with wings)\b',e['_segment'][2]):metaphors.append(e)
                elif len(re.findall(CONCRETE,e['_segment'][2]))>=2:mismatch.append(e)
            if meta['category']=='idea' and re.search(r'\bhalf-animal,? half-symbol\b',norm):
                for m in re.finditer(r'\bhalf-animal,? half-symbol\b',norm):mismatch.append(add('category_blend',m))
        assign('category_mismatch',mismatch)
        if not mismatch and metaphors:assign('category_mismatch',metaphors,'Bodily metaphor versus category shift unresolved',None)
    else:
        findings['category_mismatch']['reason']='No requested category'

    events.sort(key=lambda e:(e['start'],e['end'],e['rule']))
    for i,e in enumerate(events,1):e['id']=f'E{i:03d}'
    for f in findings.values():f['evidence']=sorted({e['id'] for e in f['evidence']})
    scope=sorted(k for k,v in qgroups.items() if v)
    if unresolved_cues:scope.append('unclear')
    if not scope:scope=['none']
    vals={k:v['value'] for k,v in findings.items()}
    def either(a,b):return 1 if 1 in (a,b) else None if None in (a,b) else 0
    def both(a,b):return 0 if 0 in (a,b) else None if None in (a,b) else 1
    def inv(a):return None if a is None else 1-a
    any_desc=either(vals['target_description'],vals['substitute_description'])
    outcomes={
      'description_produced':any_desc,
      'target_description_produced':vals['target_description'],
      'nonrecognition_without_description':both(vals['knowledge_limit'],inv(any_desc)),
      'unmarked_target_description':both(vals['target_description'],inv(vals['qualifier_anywhere'])),
      'target_unqualified_description':both(vals['target_description'],inv(vals['target_qualification'])),
    }
    for e in events:
        for k in ['_start','_end','_segment']:del e[k]
        if e['text']!=response[e['start']:e['end']]:raise AssertionError('Offset integrity')
    return dict(version=VERSION,prompt=meta,prompt_sha256=sha_text(prompt),response_sha256=sha_text(response),
                fictional_frame=fictional,findings=findings,qualifier_scope=scope,outcomes=outcomes,events=events,
                unresolved_fields=[f for f in FIELDS if findings[f]['value'] is None])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path,help='JSONL with prompt and response; preserve external identity yourself')
    p.add_argument('output',type=Path)
    args=p.parse_args()
    with args.input.open(encoding='utf-8') as src, args.output.open('x',encoding='utf-8') as dst:
        for line in src:
            r=json.loads(line); dst.write(json.dumps(score(r['prompt'],r['response']),ensure_ascii=False)+'\n')
