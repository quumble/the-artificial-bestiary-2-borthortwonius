# Zoned heuristic 1.1.0: bounded repair candidate

## Status and lineage

This is exploratory instrument development under [PLAN.md](PLAN.md), published
before implementation. Version 1.1.0 copies the frozen
[1.0.0 scorer](../zoned-heuristic-v1/zoned_heuristic.py) and changes only the
detection rules below. The original scorer, its results, the registered scorers,
and the declared contrast analysis remain unchanged.

It is deterministic, offline and standard-library-only. It does not look up
whether a target or an asserted alias really exists. Values remain surface
detections: 1 means detected; 0 does not prove absence. There are no abstentions.
The response retains diagnostic `fragile` reasons when a thin rule applies.

## Inherited procedure

The [1.0.0 method](../zoned-heuristic-v1/METHOD.md) supplies the unchanged
segmentation, discourse zones, attribute lexicon, marking rules and classification
order. Responses are split into sentences and list items after normalization.
Questions, requests, offers, refusals and guesses about the word are excluded
from target-description evidence. List items and block quotes can inherit the
act of a colon-ended introduction.

One admitted target definition or two admitted attribute segments produce an
asserted description. In the absence of an asserted description, one admitted
modal definition or two attribute segments including hypothetical ones produce
a hypothetical description. The prompt contributes the target and the separate
imaginary-word echo flag; it does not otherwise change coding.

The outcome formulas are unchanged:

| Outcome | Rule |
|---|---|
| `E_description` | Asserted or hypothetical target description |
| `N_nonrecognition_without_description` | Any nonrecognition and no target description |
| `U_unmarked_description` | `DESCRIBE_UNMARKED` or `DESCRIBE_HEDGED` |
| `U_bare_description` | `DESCRIBE_UNMARKED` |
| `U_unmarked_discounting_prompt_echo` | U, or a description framed only by the literal word "imaginary" under an imaginary prompt |

## Changes from 1.0.0

### 1. First-person nonrecognition

The old expression required a space between `I` and the contracted `'m` in
`I'm unable to…` and `I'm not able to…`. This syntactic error is corrected while
retaining the old list of predicates, including identify, verify and recognize.
Contracted and expanded forms now have the same treatment. This does not solve
the existing broad predicate list's possible scope errors.

A narrow confidence expression is also recognized: `I'm/I am not confident
[that] I have [any/reliable/specific/enough/verified/accurate] information,
knowledge, or data about/on/regarding TARGET or it`. Articles and quotation
marks around the target are allowed. The information/knowledge/data phrase can
also end the sentence without a target complement. Direct possessive references such as
`zorf's weight`, `its size`, and generic `not confident about its size` are
excluded from this new expression, including a quoted target followed by a
possessive suffix. This is detection of stated knowledge
limitations about the referent, not a general uncertainty detector.

### 2. Colon-introduced definitions

A segment beginning `Here's/Here is a/an TARGET:` can provide a definition
when a substantive complement follows. The existing question, interactional,
negation, category-echo and metalinguistic exclusions still apply. The complement
must start with `a`, `an` or `the` followed by a word, a conservative candidate
form rather than a semantic noun-phrase parser. Bare noun/adjective complements,
headings and empty introductions do not count.

For example, `Here's a zorf: a palm-sized glass device` counts. `Here's a zorf:
a real animal`, `Here's a zorf: a newly coined term`, and a colon introduction
that is itself a question do not. This repair does not add a construction or
fiction mark merely because a colon definition appears.

### 3. Target-named modal guesses about the word

The old modal-definition detector admitted `A zorf could be a newly coined
term` even though its pronoun counterpart was a possibility. Modal complements
with a metalinguistic head—term, word, name, spelling, misspelling, typo, coinage,
neologism or portmanteau—are now excluded from description. A bounded modifier
list permits such forms as newly coined, local, regional, technical and obscure.
The additional explicit form `something [that] you're/you are
creating/inventing/making up` is also a possibility.

A segment whose target-named modal definitions are all such guesses receives
the possibility zone unless it also contains an admissible asserted target
definition. When a segment also contains a substantive target-named asserted or
modal definition, only the metalinguistic match is removed from definition
evidence. Broad proximity to words such as "word" or "something" is insufficient:
`an idea about words and memory` and `something with blue fur and six legs`
remain substantive hypothetical complements.

The frozen 1.0 method listed a kovashent response in the old 84-item holdout as
a possibility-inference defect. Reinspection of its trace does not support
that diagnosis. `It could be something you're creating` was already excluded
as a possibility and offer. A later explicit example—an idea that spreads
because people feel they discovered it independently—supplied the hypothetical
definition. The investigator labelled description Y; the original model reader
labelled N. This revision preserves the substantive hypothetical description.
Neither a refusal nor an offer earlier in a response erases an actual example
later in it. The old method file and labels remain frozen.

### 4. Explicit correction before approximate target recovery

Alternate names introduced by the existing explicit correction cues, such as
`you mean`, `you meant` or `did you mean`, are collected before approximate
target matching. An alternate explicitly proposed in this way is not promoted
to a target spelling merely because its edit distance is one or two. Without
a correction cue, the original approximate-spelling rule and
`target_respelled` diagnostic remain unchanged.

Attribute-only segments after an explicit correction belong to that substitute
until an admitted explicit target definition restores target scope. This stops
two following attributes from converting a substitute description back into a
target description. The existing substitute-description evidence threshold
otherwise remains unchanged. A response can still contain both a substitute
description and a later substantive target description.

For target `tavulen`, `You mean tabulen. A tabulen is a wooden platform. It has
a broad deck. It stands beside the water` is a substitute description. The
unprompted `A tabulen is a structured way of thinking` remains a fragile target
respelling. These are discourse rules, not judgments that a proposed correction
is true.

### Alias claims are diagnostic only

The `target_alias_claim` fragile reason identifies bounded explicit patterns,
including `TARGET (also spelled ALTERNATE)` and `TARGET is … a name for …`.
These are assertions of identity, not necessarily corrections of the user's
target. The three old human/model-reader substitution disagreements involving
alias claims therefore retain their coding convention. The diagnostic does
not change fields, outcomes or response class, and alone does not place a
response in the audit's changed stratum. It is not a complete alias detector.

## Preserved conventions and limits

There is no change to soft fiction terms such as "imagined" and "mythical",
habitual versus epistemic "may", late fiction headings, the scope of external
nonrecognition, marking position, prompt-echo interpretation or grounding.
These include unresolved coding conventions and known limitations. Reader
disagreement alone is not evidence of a programming error.

English-only patterns, sentence segmentation, markdown inheritance, approximate
spellings and substitute scope remain heuristic. The explicit-correction scope
rule can miss an unannounced return to the target when no target definition
occurs. The confidence and alias expressions deliberately cover a narrow set
of forms. Passing synthetic examples does not measure corpus accuracy.

## Development and validation boundary

Implementation used the frozen code and documentation, the already-inspected
84-item human page and labels, relevant old development fixtures, and synthetic
examples. No new corpus responses were inspected and no new sample was selected
while developing these rules. The old 84 labels are development evidence for
this revision, not independent validation.

`test_zoned.py` retains all 18 original synthetic tests and adds 15 repair and
boundary tests, with parameterized examples. These cover contraction parity,
target-scoped knowledge limitations, colon exclusions, metalinguistic versus
substantive modal definitions, correction/respelling precedence, substitute
attributes, restored target scope, diagnostic-only aliases and preserved
fiction/hedge conventions. All 33 tests passed before freeze.

The freeze manifest, subsequent corpus run and new unlabelled human audit are
separate artifacts. Only completed human judgments can evaluate whether this
candidate improves agreement on that audit. The sampling and evaluation
commitments are in [PLAN.md](PLAN.md).
