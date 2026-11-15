# Bestiary 2: zoned heuristic 1.0.0 (third arm)

Prepared for Bo Chesterton · Analyst: Claude Fable 5.2 · 15 November 2026 · exploratory, not preregistered

A deterministic, offline, standard-library coding layer for the 16,000 responses of
*Artificial Bestiary 2: Borthortwonius*. It was written after reading two earlier arms
(the repository-only "mechanical coding heuristic" and the repository-plus-conversation
"context heuristic") and after comparing their outputs. It is not blind and does not
claim to be. Everything has already been run; nothing here needs running to be used.

## The one idea

Decide what each sentence is doing before counting anything in it.

Both earlier arms stumble on the same kind of response: a refusal that lists what the
word might be ("It might be a regional term", "It could be a misspelling"). One arm
reads those lines as descriptions of the thing; the other sometimes reads attribute
phrases inside them the same way. Here every sentence or list item is first assigned
to a zone: nonrecognition, refusal to invent, possibility list, request, offer, or
descriptive content. Description is only read from descriptive zones. Marks such as
"fictional" only count where they frame content, not inside an offer to invent.
List items and block quotes inherit the zone of the line that introduced them.

## What you get per response

- **response_type**, one of eight exclusive classes:
  DESCRIBE_UNMARKED, DESCRIBE_HEDGED, DESCRIBE_FRAMED, DISCLAIM_AND_DESCRIBE,
  DESCRIBE_SUBSTITUTE, DECLINE_WITH_POSSIBILITIES, DECLINE_PLAIN, NO_DESCRIPTION_OTHER
- **16 fields** (description asserted / hypothetical, personal and external
  nonrecognition, refusal to invent, possibility list, request, offer, four kinds of
  mark, grounding claim, substitute description, prompt-echo flag)
- **5 outcomes**: E, N and U in the registered shapes, plus a stricter U (bare) and a
  looser U (ignoring a bare echo of the prompt's "imaginary")
- **marking_position**: whether marks come before, after or on both sides of the
  first descriptive sentence
- **fragile**: reasons the call rests on a thin rule. There is no null; 11.1% of
  responses carry at least one fragile reason.

See METHOD.md for definitions, rule order, development record and known defects.

## What it found (all 16,000)

| Response type | n | share |
|---|---:|---:|
| DECLINE_WITH_POSSIBILITIES | 6,124 | 38.3% |
| DESCRIBE_FRAMED | 2,924 | 18.3% |
| DECLINE_PLAIN | 1,953 | 12.2% |
| DESCRIBE_HEDGED | 1,805 | 11.3% |
| DESCRIBE_UNMARKED | 1,485 | 9.3% |
| DISCLAIM_AND_DESCRIBE | 1,079 | 6.7% |
| NO_DESCRIPTION_OTHER | 485 | 3.0% |
| DESCRIBE_SUBSTITUTE | 145 | 0.9% |

Fresh bank, by framing (this arm):

| Framing | Description | Nonrecognition, no description | Unmarked | Bare unmarked | Unmarked ignoring prompt echo |
|---|---:|---:|---:|---:|---:|
| neutral | 0.19 | 0.76 | 0.05 | 0.04 | 0.05 |
| real | 0.17 | 0.76 | 0.08 | 0.07 | 0.08 |
| type of | 0.36 | 0.62 | 0.16 | 0.09 | 0.16 |
| imaginary | 0.98 | 0.02 | 0.49 | 0.18 | 0.75 |

## How it sits against the other two

Response-level agreement (Cohen's kappa, all responses; A = context heuristic,
B = registered scorers as wrapped by the mechanical arm, C = this arm):

| Construct | A vs B | A vs C | B vs C |
|---|---:|---:|---:|
| Description produced | 0.63 | 0.64 | 0.89 |
| Any nonrecognition | 0.60 | 0.60 | 0.94 |
| Nonrecognition without description | 0.44 | 0.45 | 0.89 |
| Unmarked description | 0.70 | 0.70 | 0.91 |

This arm was built by a different mechanism from the registered scorers and lands
close to them. On description it sides with B in 2,531 of the 2,996 A/B
disagreements. The Anthropic-minus-OpenAI description gap on fresh real and type-of
prompts is -0.07 under A, -0.34 under B and -0.39 here.

## Blind check

Before scoring the corpus I froze the code, drew 84 held-out responses (enriched for
A/B disagreement, none from the development sample), and labelled them from text
alone, without any instrument's output. Raw correct out of 84, with
population-weighted accuracy in brackets:

| Construct | A | B | C |
|---|---:|---:|---:|
| Description produced | 49 (0.80) | 76 (0.94) | 82 (0.99) |
| Any nonrecognition | 58 (0.73) | 79 (0.94) | 78 (0.94) |
| Nonrecognition without description | 51 (0.70) | 74 (0.91) | 79 (0.97) |
| Unmarked description | 71 of 79 (0.95) | 80 (0.96) | 81 (0.96) |

Read this with four cautions. The reader was Claude Fable 5.2, the same model that
wrote this heuristic, so reader and instrument share a notion of "description". The
sample is small. I had already seen how A and B disagree before designing C. And I
read the first 600 characters of each response, checking tails for six.
A human pass over `holdout_keys.json` is the real test; the labels are in
`holdout_labels.json` to be overwritten.

## What this arm adds beyond agreeing with B

- Splits B's single nonrecognition class into declining with a list of what the word
  might be (6,124) and declining plainly (1,953).
- Removes 443 responses from B's "description plus nonrecognition" class that are
  refusals with attribute phrases in them.
- Splits unmarked description into bare (1,485) and attribute-hedged (1,805).
- Shows how much of the imaginary-frame marking is the prompt's own word: 1,293 of
  4,800 imaginary-framed responses are marked only by "imaginary". Discounting that,
  unmarked description in the imaginary frame rises from 0.49 to 0.75.
- Separates describing a different word (145) from describing the target.
- Records where marks sit: of 7,293 responses with a description, 407 are marked
  only after the description starts.

## Files

| File | Contents |
|---|---|
| zoned_heuristic.py | All rules (frozen; hash in FREEZE.sha256) |
| run_corpus.py | Runner used to produce results/ |
| test_zoned.py | 18 regression tests on synthetic text |
| results/response_codes.csv | One row per response, composite key, all fields |
| results/evidence.jsonl | Per response: every zoned segment and its zones |
| results/rates_by_*.csv | Plain rates by bank/framing, bank/model/framing, word cell |
| comparison/three_way.json | Pairwise agreement, holdout scores, contrasts under A, B, C |
| dev_keys.json, holdout_keys.json, holdout_labels.json | Development and held-out samples |

The response texts are not included; they stay in the study's own release.
