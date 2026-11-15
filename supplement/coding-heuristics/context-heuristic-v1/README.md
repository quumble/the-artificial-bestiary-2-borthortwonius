# Bestiary 2: our frozen contextual heuristic

**Repository + conversation arm · version 1.0.0 · exploratory**

Start with `METHOD.md` for the procedure and `codebook.json` for the exact
category definitions. `heuristic.py` contains all detection rules. It is offline,
deterministic, and uses only Python's standard library. No API keys are needed.

The distinguishing choices are scope-sensitive qualification, target/substitute
separation, personal knowledge versus external claims, fictional lore versus
real-world grounding, and preserving incompatible status acts. Every detection
or unresolved decision links to literal evidence and rule identifiers.

**0 means not detected, not proven absent.** Null means a recognized unresolved
case. This is a testable mechanical heuristic, not a validated semantic oracle.

Run from this directory with Python 3.12 or later (also usable on Windows):

```text
python -m unittest discover -v
python run_corpus.py --raw-archive PATH_TO/bestiary-raw-snapshot.zip --out new-results
python verify.py --raw-archive PATH_TO/bestiary-raw-snapshot.zip --out new-results
```

The raw archive is the original release asset:
https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/raw-data-2026-11-11

Its exact SHA-256 is pinned in `run_corpus.py`. The source archive is intentionally
not duplicated in this package. Existing output directories are refused.

The delivered ZIP includes `results/`:

| File | Contents |
|---|---|
| response_codes.jsonl | 16,000 composite-keyed rows, 14 fields and five derived outcomes |
| evidence.jsonl | Rule decisions, reasons and exact evidence excerpts/offsets |
| detection_summary.json | Bank, framing and endpoint summaries with unresolved counts |
| exploratory_contrasts.json | New descriptive framing differences, with null-assignment sensitivity |
| cell_consistency.jsonl | 2,560 repeated-response cells |
| consistency_summary.json | Within-cell pair agreement and coverage |
| execution.json | Input/output hashes and completed-run receipt |

`VALIDATION.json` records export verification. `FREEZE.json` fixes this version
before its corpus application. `PROVENANCE.json` records the arm, inputs and the
exact brief given to temporary chat. The 42 test methods include multiple boundary
and metamorphic subcases; passing them is not a held-out accuracy claim.

The original scorers, primary analyses and secondary A/B outputs remain intact.
This package adds features and descriptive exports. It does not replace the
original inferential analyses. The temporary-chat artifact has not been read.
Nothing in this package has been pushed to GitHub during its preparation.

When the other ZIP is available, the next step is a definition crosswalk and
agreement analysis, not another round of hand-coding every response.
