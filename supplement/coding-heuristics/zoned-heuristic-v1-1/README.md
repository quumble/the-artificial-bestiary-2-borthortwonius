# Zoned heuristic 1.1: repair candidate and human audit

**Status: frozen candidate; human validation pending.** This exploratory revision
was prepared with GPT assistance after the investigator's first 84-item human
pass. It preserves Claude Fable's original zoned v1 as a comparison. The old
human labels informed development and do not independently validate this version.

## Next action: the human pass

Download [audit/labelling-page.html](audit/labelling-page.html) and open the
downloaded file in a browser. It works offline. Read the full prompt and response,
answer the same recognition/description/marking questions as before, and use the
unsure flag where appropriate. The page saves progress locally and can export
or import a JSON backup. Return the completed JSON for scoring.

The page contains 96 responses: 25 whose tracked coding changed and 71 controls.
It supplies no model, word-source, scorer, previous-label, or sampling-stratum
metadata. The original response prose is preserved and may itself reveal clues.
Avoid opening `audit/manifest.json` or the code tables before completing the pass:
those are the reproducibility record and contain the concealed predictions.
No human or model labels have been supplied for this audit.

## What changed

The [method](METHOD.md) gives the exact rule boundaries. The four repairs address
contracted first-person nonrecognition, colon-introduced definitions, target-named
modal guesses about words, and explicit corrections to alternate spellings.
Alias assertions receive a diagnostic flag without changing their classification.
Fiction, hedge and grounding lexicons are unchanged; their detections can still
change when an upstream discourse zone changes.

The original 16,000 response keys and hashes match. **258 responses (1.61%)**
change on E, R, N, U, the substitute flag, or response type. **416 (2.60%)**
change on at least one exported field, including diagnostics.

| Main field | Changed rows | 0 → 1 | 1 → 0 |
|---|---:|---:|---:|
| E: target description | 71 | 1 | 70 |
| R: any nonrecognition | 191 | 191 | 0 |
| N: nonrecognition without target description | 233 | 232 | 1 |
| U: unmarked target description | 24 | 0 | 24 |

These are detection changes, not accuracy improvements. Complete codes,
per-row differences and execution hashes are in [results/](results/).
The original three arms, registered results and declared contrast estimates
remain unchanged. This candidate is not substituted into the existing report.

## Ordering and audit population

1. [Repair and sampling plan](PLAN.md) published in commit
   [`4f036d8`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/commit/4f036d882c09ec6bc1ad24f988911c74bfa5937e).
2. Code, tests, method and audit generator frozen in commit
   [`3d8b4c3`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/commit/3d8b4c35961fbdfb6ca88084dab3c63b9d4df03b),
   with [SHA-256 hashes](FREEZE.sha256), before corpus replay or audit selection.
3. Candidate replay and deterministic audit selection executed without revising
   the frozen code. Human judgments are the outstanding step.

The audit excludes 212 recorded development/holdout keys and 13 additional rows
identified by response hashes, including duplicate texts: 225 exclusions total.
The eligible population is 15,775. Sampling uses endpoint × bank × changed
status, with the predeclared allocation and fixed hash rankings. Six of the 32
possible strata are empty; all 26 populated strata are sampled. The selection
and order were not searched or redrawn. Audit ID: `zoned-v1.1-5b04578625efb3581f25`.

Earlier informal exposure and the historical audit64/targeted4/check32 keys were
not fully recoverable. This is disjointness from documented prior inspection,
not a claim that no prior assistant has ever seen any selected text.

After complete labels arrive, report raw and stratum-weighted E/R/N/U agreement
for both versions and their paired correctness difference. Substitution is
reported separately against the exclusive substitute class. Primary results
retain all labels; unsure-reference bounds and an unflagged-only conditional
sensitivity are included. No new hypothesis tests are declared.

## Reproduce

Python standard library only. Run from the repository root. Obtain
`bestiary-raw-snapshot.zip` from the
[raw-data release](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/raw-data-2026-11-11).
Its SHA-256 must be
`f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6`.
Always pass `--archive` / `--raw-archive` explicitly: the repository's `data.zip`
is a different ZIP package and is intentionally rejected by the checksum guard.

```bash
python supplement/coding-heuristics/zoned-heuristic-v1-1/run_corpus.py --archive ../bestiary-raw-snapshot.zip --freeze-commit 3d8b4c35961fbdfb6ca88084dab3c63b9d4df03b --out analysis/zoned-v1-1-replay
python supplement/coding-heuristics/zoned-heuristic-v1-1/audit.py prepare --raw-archive ../bestiary-raw-snapshot.zip --repaired-codes analysis/zoned-v1-1-replay/response_codes.csv --freeze-commit 3d8b4c35961fbdfb6ca88084dab3c63b9d4df03b --out analysis/zoned-v1-1-audit
```

Existing output directories are rejected. Both commands verify committed
freeze bytes; audit preparation also checks the corpus execution receipt.
No API requests or model generation are performed.

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s supplement/coding-heuristics/zoned-heuristic-v1-1 -v
node supplement/coding-heuristics/zoned-heuristic-v1-1/test_audit_ui.cjs
```

Validation: 107 existing tests, 51 candidate Python tests and the synthetic
JavaScript interaction harness pass. The latter covers conditional questions,
autosave, navigation, JSON export/import and invalid-import rejection. A real
browser layout check was unavailable because Chromium could not start in this
execution environment; no visual browser validation is claimed.

An independent programmatic check reproduced every code delta and transition,
the exclusion set, stratum allocations, selected keys and display order. It also
verified all 16,000 response hashes, the 96 selected prompt hashes, complete page
text equality and the absence of concealed metadata from the page payload.
All 16 tracked original-v1 files remain byte-identical to merged main.

To score returned labels (the score command rejects partial or invalid labels):

```bash
python supplement/coding-heuristics/zoned-heuristic-v1-1/audit.py validate --manifest supplement/coding-heuristics/zoned-heuristic-v1-1/audit/manifest.json --labels returned-labels.json
python supplement/coding-heuristics/zoned-heuristic-v1-1/audit.py score --manifest supplement/coding-heuristics/zoned-heuristic-v1-1/audit/manifest.json --labels returned-labels.json --out analysis/zoned-v1-1-human-results.json
```
