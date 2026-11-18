# Streamlined labelling for the zoned v1.1 audit

Declared 18 November 2026, before any label for audit
`zoned-v1.1-5b04578625efb3581f25` was supplied. Investigator: Bo Chesterton.
Written by Claude Opus 5.5 at the investigator's request. Exploratory instrument
development, like the [parent plan](../PLAN.md); no hypothesis tests are added.

## Why

The investigator found the frozen 96-item page too slow to work through. The
earlier 84-item pass asked the same three questions on a one-key page and took
about 29 minutes. This amendment changes the interface and adds a smaller core
set. It changes nothing about what is being measured.

## What changes

1. **Interface only.** Same three questions, same wording and hints, same
   answer codes (nonrecognition Y/N; description Y/H/S/N; mark Y/E/N, with E
   offered only on imaginary prompts), same label schema and audit ID. Each
   answer is one key, laid out as on the 84-item page: F no, J yes, K and D for
   the extra choices. U toggles the unsure flag; Backspace undoes. The made-up
   word is highlighted, taken from the prompt text. The per-item notes box is
   dropped, so notes export as empty strings; the parent plan's optional notes
   are not carried forward. Answers persist in browser storage and, when the
   page is opened as a published artifact, in that artifact's own store so
   Claude can read them. A copy-to-clipboard export is always available.
   Labels already entered on the frozen page can be pasted in.

2. **A core set of 41.** It consists of all 25 changed items, plus one control from each of
   the 16 populated unchanged strata. The control is the selected item with the
   lowest selection rank, which is the same frozen hash rank the parent plan
   used to choose them. The rule was fixed from stratum names and selection
   ranks alone. No response text or instrument output was read to choose it.
   The 41 come first, in the frozen display order. The other 55 follow,
   optional, also in frozen order.

3. **Scoring.** The frozen `audit.py` scorer is used unchanged. If only the core is
   labelled, it is applied to [`manifest-core41.json`](manifest-core41.json),
   which holds the same items, predictions and populations, with stratum
   selection counts and N_h/n_h weights set to the core. If all 96 are
   labelled, the parent manifest is scored as originally declared and that
   result is primary; the core score is then reported alongside.

## What the subset does and does not change

- **The v1.1 minus v1.0 comparison is unaffected.** On every unchanged item the
  two versions return identical E, R, N, U and substitution codes. The weights
  also sum to the eligible population either way. So the paired correctness
  difference, weighted or counted, is identical whether the same labels are
  scored over 41 or 96. `test_quick.py` checks this with synthetic labels.
- **Absolute accuracy for each version is much less precise.** It rests on one
  control per unchanged stratum instead of three to eleven, so each control
  carries a weight of up to 1,186 responses. The unsure-exclusion sensitivity
  also has a different denominator.
- **Composition differs.** Changed items are 25 of 41 (61%) in the core,
  against 25 of 96 (26%) on the full page. The investigator knows from
  conversation that most v1.1 changes add detected nonrecognition. He does
  not know which items changed or in which direction. The page carries no
  stratum, prediction or canonical key, and its order within the core is the
  frozen order.

Everything else in the parent plan stands: the v1.1 code, the 96-item sample,
its exclusions and order, the parent manifest and page (kept byte-identical),
and the evaluation rules.

## Files

| File | Contents |
|---|---|
| `quick.py` | Builds the core manifest and page from the frozen manifest and page; scores with the frozen scorer |
| `quick-template.html` | The one-key page template |
| `labelling-page-quick.html` | The built page: all 96 responses, core 41 first |
| `manifest-core41.json` | The core manifest, same audit ID as the parent |
| `test_quick.py` | Rebuild, composition, concealment and paired-difference checks |

## Reproduce

From this folder, standard library only:

```text
python quick.py build
python -m unittest -v test_quick
python quick.py score --labels returned-labels.json --set core --out core-results.json
python quick.py score --labels returned-labels.json --set all --out full-results.json
```

`build` verifies every response and prompt hash in the frozen page against the
frozen manifest before writing. `score --set all` rejects anything short of 96
labels, as the frozen scorer does.
