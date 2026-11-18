# Human audit of zoned v1.1: core 41 results

18 November 2026. Labels by the investigator, Bo Chesterton, on the
[streamlined page](labelling-page-quick.html), entered after the
[streamlining declaration](STREAMLINE.md) was pushed. Scored with the frozen
`audit.py` scorer against [`manifest-core41.json`](manifest-core41.json).
Analysis and write-up by Claude Opus 5.5. Exploratory; no hypothesis tests.

- Labels: [`human-labels-core41.json`](human-labels-core41.json), exactly as
  saved by the page. All 41 complete, 5 flagged unsure. About 30.5 minutes in
  total, with a median of 22 seconds per item.
- Scorer output: [`human-results-core41.json`](human-results-core41.json).
- The optional 55 controls were not labelled, so the full-96 score does not exist.

## v1.0 versus v1.1

Correct out of 41 (25 changed items + 16 controls). On every control, the two
versions give identical codes, so all of the difference comes from the 25 changed items.

| Outcome | v1.0 | v1.1 | v1.1 only right | v1.0 only right | Weighted paired difference, pp | Unsure-label bounds, pp |
|---|---:|---:|---:|---:|---:|---|
| E description | 29 | 37 | 10 | 2 | +0.25 | [+0.04, +0.37] |
| R any nonrecognition | 25 | 38 | 13 | 0 | +1.14 | [+1.14, +1.14] |
| N nonrecognition without description | 19 | 37 | 19 | 1 | +1.29 | [+1.17, +1.29] |
| U unmarked description | 37 | 41 | 4 | 0 | +0.16 | [+0.07, +0.16] |
| S substitution (separate) | 31 | 37 | 9 | 3 | +0.04 | [-0.18, +0.16] |

On the 25 changed items alone, the counts are E 14 → 22, R 10 → 23, N 4 → 22,
U 21 → 25 and S 15 → 21. The weighted differences are corpus-level: they are
small because only 1.61% of responses change between versions. Excluding the
five unsure labels leaves every main-outcome direction unchanged.

**Reading.** On this reader's labels, v1.1 improves all four main outcomes. The
largest gain is in nonrecognition, which comes from the contraction repair.
Substitution is not improved overall: three new false substitute calls offset
its gains.

## Where v1.1 still disagrees with the reader

- **The correction cue overfires (repair 4).** Item-079 offers "you might mean"
  alternatives, then gives a template for the target itself, and v1.1 calls it
  a substitute. Item-042 only offers to check for a misspelling and describes
  nothing, yet v1.1 also calls it a substitute. A correction cue alone should
  not decide the class when the described subject is the target, or when nothing is
  described.
- **One borderline case.** In item-069, a respelled target is mapped onto the
  red panda. The reader chose "what-if or offered example", flagged it unsure,
  and v1.1 calls it a substitute.
- **Substitutes the reader saw that v1.1 missed or mis-scored.** These are items 014 and 033.
- **Both versions miss two controls.** Items 072 and 096 are what-if
  descriptions from the GPT-5.4 endpoints.

These belong in a later version, tested on a fresh sample. Version 1.1 is unchanged.

## Limits

One informed reader, who knew from conversation that most v1.1 changes add
detected nonrecognition. The core set is 61% changed items. Absolute weighted
accuracy rests on one control per unchanged stratum and is imprecise. This is
agreement with one human pass, not validated accuracy.
