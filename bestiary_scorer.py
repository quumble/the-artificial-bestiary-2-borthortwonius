"""Literal GPT v1 feature battery. No semantic classifier or external requests."""
from collections import Counter
import math
from pathlib import Path
import json
import re
import unicodedata

VERSION = "gpt-bestiary-2-v1.0"
INVENTORY_PATH = Path(__file__).parent/"docs/gpt-proposal/inventories-gpt-v1.json"
LEX = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*|\d+(?:[.,]\d+)*")
NUMERIC = re.compile(r"\d+(?:[.,]\d+)*\Z")
NEGATION = set("no not never neither nor without isn't aren't wasn't weren't don't doesn't didn't can't cannot couldn't won't wouldn't".split())
LEXICAL = ["M%02d" % i for i in [1,2,3,4,5,6,7,8,10,21,30,32]]


def normalize(raw):
    text, mapping, i = [], [], 0
    while i < len(raw):
        end = i+2 if raw[i:i+2] == "\r\n" else i+1
        part = "\n" if raw[i] == "\r" else raw[i]
        part = unicodedata.normalize("NFKC", part).casefold()
        part = part.translate(str.maketrans({"\u2018": "'", "\u2019": "'", "\u02bc": "'"}))
        text.extend(part)
        mapping.extend([(i, end)]*len(part))
        i = end
    return "".join(text), mapping


def token_values(text):
    return WORD.findall(normalize(text)[0])


def quoted_ranges(raw):
    spans, offset = [], 0
    for line in raw.splitlines(keepends=True):
        for delimiter in ('"', '`'):
            points = [i for i, char in enumerate(line) if char == delimiter]
            spans += [(offset+a+1, offset+b) for a, b in zip(points[::2], points[1::2])]
        pos = 0
        while True:
            a = line.find("\u201c", pos)
            b = line.find("\u201d", a+1) if a >= 0 else -1
            if a < 0 or b < 0:
                break
            spans.append((offset+a+1, offset+b))
            pos = b+1
        offset += len(line)
    return spans


def greedy(candidates):
    selected, occupied = [], set()
    for candidate in sorted(candidates, key=lambda m: (m["start"], -(m["end"]-m["start"]), m["entry"])):
        positions = set(range(candidate["start"], candidate["end"]))
        if not positions & occupied:
            selected.append(candidate)
            occupied |= positions
    return selected


class Text:
    def __init__(self, raw):
        self.raw = raw
        self.normalized, self.mapping = normalize(raw)
        self.tokens, self.segments = [], []
        start = 0
        for boundary in list(re.finditer(r"\n|[.?!]+(?=\s|$)", self.normalized)) + [None]:
            end = boundary.end() if boundary else len(self.normalized)
            segment = self.normalized[start:end]
            if segment.strip():
                sid = len(self.segments)
                indices = []
                for match in WORD.finditer(segment):
                    a, b = start+match.start(), start+match.end()
                    indices.append(len(self.tokens))
                    self.tokens.append(dict(value=match.group(), normalized_start=a, normalized_end=b,
                                            raw_start=self.mapping[a][0], raw_end=self.mapping[b-1][1], segment=sid))
                self.segments.append(indices)
            start = end
        self.values = [t["value"] for t in self.tokens]
        self.positions = {}
        for index,value in enumerate(self.values):
            self.positions.setdefault(value,[]).append(index)
        self.quotes = quoted_ranges(raw)

    def match(self, family, entries, subfamily=None):
        candidates = []
        for entry in entries:
            sequence = token_values(entry)
            n = len(sequence)
            if not n:
                continue
            for start in self.positions.get(sequence[0],[]):
                end = start+n
                if end <= len(self.tokens) and self.values[start:end] == sequence and self.tokens[start]["segment"] == self.tokens[end-1]["segment"]:
                    candidates.append(self.span(family, entry, start, end, subfamily))
        return candidates

    def span(self, family, entry, start, end, subfamily=None):
        first, last = self.tokens[start], self.tokens[end-1]
        raw_start, raw_end = first["raw_start"], last["raw_end"]
        nearby = [t["value"] for t in self.tokens[max(0,start-3):end] if t["segment"] == first["segment"]]
        return dict(family=family, subfamily=subfamily, entry=entry, start=start, end=end, segment=first["segment"],
                    normalized_span=[first["normalized_start"], last["normalized_end"]], raw_span=[raw_start,raw_end],
                    raw_text=self.raw[raw_start:raw_end], local_negation=bool(NEGATION.intersection(nearby)),
                    quotation_overlap=any(a < raw_end and b > raw_start for a,b in self.quotes))


def score(raw, target, prompt):
    if raw is None or not isinstance(raw, str) or not raw.strip():
        return dict(version=VERSION, usable=False, features={f"M{i:02}": None for i in range(1,33)}, matches=[])
    text, features, matches = Text(raw), {}, []
    words, w = text.values, len(text.tokens)
    all_matches = {}
    def summarize(items):
        return dict(any=int(bool(items)), count=len(items), density=100*len(items)/w if w else None,
                    local_negation_count=sum(m["local_negation"] for m in items),
                    quotation_overlap_count=sum(m["quotation_overlap"] for m in items),
                    entries=dict(Counter(m["entry"] for m in items)))
    def add(family, entries):
        groups = entries if isinstance(entries, dict) else {"all": entries}
        candidates, components = [], {}
        for subfamily, inventory in groups.items():
            found = text.match(family, inventory, subfamily)
            candidates.extend(found)
            components[subfamily] = summarize(greedy(found))
        selected = greedy(candidates)
        all_matches[family] = selected
        features[family] = dict(summarize(selected), components=components)
        matches.extend(selected)
    for family in LEXICAL:
        add(family, LEX[family])
    target_tokens = token_values(target)
    if len(target_tokens) != 1:
        raise ValueError("Target must tokenize to exactly one word.")
    target_token = target_tokens[0]
    add("M09", [target_token+" "+suffix for suffix in LEX["M09_suffixes"]])
    cues = sorted({(m["start"],m["end"]): m for f in ["M01","M02","M03","M04"] for m in all_matches[f]}.values(), key=lambda m:m["start"])
    cue_groups = {f:all_matches[f] for f in ["M01","M02","M03","M04"]}
    cue_groups["C"] = cues
    features["M11"], features["M12"] = {}, {}
    for family, found in cue_groups.items():
        first = found[0] if found else None
        features["M11"][family] = dict(raw_offset=first["raw_span"][0] if first else None,
            word_index=first["start"] if first else None, relative_position=first["start"]/w if first else None,
            no_match_observed=int(not found))
        window = math.ceil(.2*w)
        features["M12"][family] = dict(first_segment=int(any(m["segment"]==0 for m in found)),
            last_segment=int(any(m["segment"]==len(text.segments)-1 for m in found)),
            first_window=int(any(m["start"]<window for m in found)), last_window=int(any(m["start"]>=w-window for m in found)))
    definition = all_matches["M09"]
    if definition and cues:
        a,b = definition[0]["start"], cues[0]["start"]
        state = "definition_first" if a<b else "cue_first" if b<a else "tie"
    else:
        state = "definition_only" if definition else "cue_only" if cues else "neither"
    features["M13"] = dict(state=state, definition_before_any_observed_cue=int(state in {"definition_first","definition_only"}))
    vectors = []
    families = ["M09","M10","M01","M02","M03","M04"]
    for sid in range(len(text.segments)):
        vectors.append([int(any(m["segment"]==sid for m in all_matches[f])) for f in families])
    descriptive = [v for v in vectors if any(v[:2])]
    for key, count in [("M14",sum(not any(v[2:]) for v in descriptive)),("M15",sum(any(v[2:]) for v in descriptive))]:
        features[key] = dict(count=count, fraction_all=count/len(vectors), fraction_descriptive=count/len(descriptive) if descriptive else None)
    features["M15"]["by_family"] = {f:sum(v[j] for v in descriptive) for j,f in enumerate(families) if j>=2}
    sequence = {}
    for j,f in enumerate(families):
        values = [v[j] for v in vectors]
        transitions = Counter(f"{a}{b}" for a,b in zip(values,values[1:]))
        maximum = {}
        for value in [0,1]:
            run, longest = 0,0
            for current in values:
                run = run+1 if current==value else 0
                longest = max(longest,run)
            maximum[str(value)] = longest
        sequence[f] = dict(transitions={s:transitions[s] for s in ["00","01","10","11"]}, max_run=maximum)
    features["M16"] = dict(vectors=vectors, summary=sequence)
    features["M17"] = dict(raw_characters=len(raw), words=w)
    features["M18"] = dict(segments=len(vectors), mean_words=w/len(vectors), max_words=max(map(len,text.segments)))
    lines = raw.splitlines()
    features["M19"] = dict(headings=sum(bool(re.match(r"^ {0,3}#{1,6}\s+\S",line)) for line in lines),
        unordered_items=sum(bool(re.match(r"^\s*[-+*]\s+\S",line)) for line in lines),
        ordered_items=sum(bool(re.match(r"^\s*\d+[.)]\s+\S",line)) for line in lines),
        paragraphs=sum(bool(line.strip()) and (i==0 or not lines[i-1].strip()) for i,line in enumerate(lines)))
    features["M20"] = dict(count=raw.count("?"), raw_positions=[i for i,c in enumerate(raw) if c=="?"])
    prompt_tokens = set(token_values(prompt))
    p = prompt_tokens-set(LEX["M22_function_words"])-{target_token}
    features["M22"] = dict(target_mentions=words.count(target_token), prompt_content_overlap=len(p & set(words))/len(p) if p else None)
    numbers = set(LEX["M23_number_words"])
    numeric = lambda word: bool(NUMERIC.fullmatch(word))
    features["M23"] = dict(numeric_tokens=sum(numeric(word) for word in words),
        number_words=sum(word in numbers for word in words),
        number_unit_pairs=sum((numeric(a) or a in numbers) and b in LEX["M23_units"] and text.tokens[i]["segment"]==text.tokens[i+1]["segment"] for i,(a,b) in enumerate(zip(words,words[1:]))))
    sources = {}
    for name, pattern in [("urls",r"https?://[^\s<>]+"),("dois",r"\b10\.\d{4,9}/[^\s<>]+"),
                          ("author_year",r"\([a-z]+(?: et al\.)?,?\s+(?:19|20)\d{2}[a-z]?\)")]:
        sources[name] = []
        for found in re.finditer(pattern,text.normalized):
            end = found.end()
            if name != "author_year":
                while end>found.start() and text.normalized[end-1] in ".,;:!?)]}":
                    end -= 1
            a,b = text.mapping[found.start()][0], text.mapping[end-1][1]
            sources[name].append(dict(raw_span=[a,b],raw_text=raw[a:b]))
    attribution = greedy(text.match("M24",LEX["M24_attribution"]))
    matches.extend(attribution)
    features["M24"] = dict(sources=sources,counts={name:len(items) for name,items in sources.items()},attribution=summarize(attribution))
    features["M25"] = {}
    for n in [3,5]:
        ngrams = [tuple(words[i:i+n]) for i in range(max(0,w-n+1))]
        total,distinct = len(ngrams),len(set(ngrams))
        features["M25"][str(n)] = dict(total=total,distinct=distinct,excess=total-distinct,fraction=(total-distinct)/total if total else None)
    for family in ["M26","M27","M28"]:
        features[family] = None  # defined over multiple responses, computed by group_features
    features["M29"] = {}
    for length in [50,100]:
        features["M29"][str(length)] = {str(n):len({tuple(words[i:i+n]) for i in range(length-n+1)})/(length-n+1) if w>=length else None for n in [2,3]}
    candidates, components = [], {}
    for subfamily, entries in LEX["M31"].items():
        found = [m for m in text.match("M31",entries,subfamily) if all(words[i] not in prompt_tokens|{target_token} for i in range(m["start"],m["end"]))]
        candidates.extend(found)
        components[subfamily] = summarize(greedy(found))
    selected = greedy(candidates)
    features["M31"] = dict(summarize(selected),components=components)
    matches.extend(selected)
    return dict(version=VERSION,usable=True,features=features,matches=sorted(matches,key=lambda m:(m["start"],m["family"],m["entry"])))


def trigram_set(raw, target=None):
    words = token_values(raw)
    if target is not None:
        target = token_values(target)[0]
        words = ["<TARGET>" if w==target else w for w in words]
    return {tuple(words[i:i+3]) for i in range(len(words)-2)}


def jaccard(a,b):
    return len(a & b)/len(a | b) if a and b else None


def cell_features(responses):
    usable = [r for r in responses if isinstance(r,str) and r.strip()]
    k = len(usable)
    out = {"usable_responses":k,"M26":None,"M27":None}
    if k<2:
        return out
    duplicate = {}
    for name,strings in [("raw",usable),("normalized",[" ".join(normalize(r)[0].split()) for r in usable])]:
        counts = Counter(strings)
        duplicate[name] = dict(excess_fraction=(k-len(counts))/k, identical_pair_fraction=sum(n*(n-1)/2 for n in counts.values())/(k*(k-1)/2))
    sets = [trigram_set(r) for r in usable]
    values = [jaccard(a,b) for i,a in enumerate(sets) for b in sets[i+1:]]
    eligible = [v for v in values if v is not None]
    out.update(M26=duplicate,M27=dict(mean=sum(eligible)/len(eligible) if eligible else None,eligible_pairs=len(eligible),eligible_responses=sum(bool(s) for s in sets)))
    return out


def reuse_features(word_responses):
    """Input word -> {word_set, responses}; each word pair receives equal weight."""
    prepared = {word:[trigram_set(r,word) for r in item["responses"] if isinstance(r,str) and r.strip()] for word,item in word_responses.items()}
    words = sorted(prepared)
    groups = {"within_animal_intent":[],"within_no_intent":[],"between_sets":[]}
    per_word = {w:[] for w in words}
    pairs = []
    for i,a in enumerate(words):
        for b in words[i+1:]:
            vals = [jaccard(x,y) for x in prepared[a] for y in prepared[b]]
            vals = [v for v in vals if v is not None]
            mean = sum(vals)/len(vals) if vals else None
            sa,sb = word_responses[a]["word_set"],word_responses[b]["word_set"]
            kind = "between_sets" if sa!=sb else "within_animal_intent" if sa.endswith("animal-intent") else "within_no_intent"
            pairs.append(dict(word_a=a,word_b=b,mean=mean,eligible_pairs=len(vals),group=kind))
            if mean is not None:
                groups[kind].append(mean)
                per_word[a].append(mean)
                per_word[b].append(mean)
    return dict(word_pairs=pairs,groups={k:dict(mean=sum(v)/len(v) if v else None,eligible_word_pairs=len(v)) for k,v in groups.items()},
                per_word={w:sum(v)/len(v) if v else None for w,v in per_word.items()})
