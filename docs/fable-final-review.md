# Final review handoff for Claude Fable

Prepared by GPT/Codex on November 11, 2026, 12:29 EST (17:29 UTC), before study collection. Reviewed upstream baseline: `41dccfcacbf7e6bd1e3bb3d0398afc942e2a5835`. The investigator authorized the implementation fixes and reserved Claude's remaining scientific choices for Fable's final review. No provider API calls or actual study-response inspection occurred in this pass.

## Settled with the investigator

- Fresh bank: eight Bo animal-intent words, eight Claude no-intent words and eight GPT Temporary Chat no-intent words. Final private file and hash are still pending.
- GPT fresh primary estimates weight each source exactly one-third. The original 50/25/25 weighting remains a descriptive sensitivity using the same source-stratified bootstrap draws. The eight primary contrasts and their correction stay unchanged.
- Direct known/fresh comparisons retain common 50/50 intent weighting. Equal thirds for the fresh headline does not automatically change each of Claude's independent tests.
- Both analysts' families remain separately labelled and corrected. No additional models, repetitions or outcomes were added.

The [timestamped GPT amendment](gpt-proposal/PREREGISTRATION_GPT.md#amendment-1-balanced-word-sources-and-analysis-weights) preserves the original body and records these changes.

## Implementation corrections completed

1. **Collector stops:** changed identity wins over a simultaneous reasoning flag; every valid-or-issue closure checks the 5% rule once 200 such slots have closed; replay restores interrupted stop decisions after a restart. Already in-flight attempts are retained. Retry-exhausted slots remain separate from the issue-rate denominator.
2. **Claude analysis gates:** both batches must be closed before any response is read; the combined protocol, frozen manifest, source hashes and runtime must match. Analysis uses the attempt-ledger export and audits planned metadata, request settings, served identifiers, issues and duplicate terminal attempts.
3. **Planned eligibility:** Claude's word bank and model completion denominator now come from the frozen schedule. Completely missing words remain planned. For example, 700 eligible fresh slots are 700/1,200, not 700/700 after ten words disappear.
4. **GPT weighting:** primary estimates, paired bootstrap, bounds, sensitivities and within-batch endpoint comparisons all use the amended source weights. Historical comparisons explicitly use the common intent weights.

Claude's six statistical tests, numeric eligibility thresholds and both scorers remain as previously implemented. The original Claude preregistration and Amendment 1 have not been edited by GPT. See [validation](validation.md) for the final suite result and scope.

## Choices for Fable before freeze

### 1. Source weighting after missing words

For a Claude test averaging all fresh words, equal word weights imply equal thirds only while all three source groups retain equal counts. Current code averages the eligible words. Decide whether to retain that estimand or preserve one-third per source after exclusions, and state the rule for a source with no eligible words. This choice can require changes to the estimator and resampling, not merely a prose edit. H3's two-arm intent contrast, H6's two-source interaction and H4's intent standardization should each keep an explicit definition.

### 2. Late-stopped models

Amendment 1 section 5 both sets a 60% eligible-slot threshold and says a stopped model falls out of its group. A model stopped late can still exceed 60%. Current code implements the numeric threshold. Choose whether a late stop also forces exclusion. A new stop-based exclusion needs exported stop status and a matching test before freeze.

### 3. Holm family when a test is unavailable

Current `holm()` removes `p=None` tests. If one of six tests is untestable, the correction uses five. Amendment 1 says correction across six tests. Decide and document the intended rule. GPT recommends retaining the fixed six-hypothesis family, using a non-rejection placeholder such as p=1 for adjustment while reporting the unavailable result as untested. The current function and its test were left unchanged for Fable's decision.

### 4. Exact stopping denominator

Confirm the implemented definition: issues divided by valid-plus-issue closed slots within a batch, checked once that denominator reaches 200. Retry-exhausted slots are separately reported missing observations and do not enter this fraction. The GPT amendment states this explicitly. Any alternative should be recorded and implemented before collection.

## Analyzer commitment

The old registered SHA-256 for `analyze_claude.py` is:

```text
43b549940dae692f1db3242988b27060824eeb46b452616fe16b388883902e28
```

The corrected analyzer at this handoff has SHA-256:

```text
6a4e3623fe30b122e9cb1177d349d5b59ccf7ac5ee66aace8c5e719979e1865f
```

Review the code, make any chosen changes, then compute the final hash and update the existing commitment in `prereg/CLAUDE_PREREG_AMENDMENT_1.md`. Do not copy the handoff hash if the analyzer changes again. The combined freeze now rejects a missing or stale registered analyzer hash. This checks the already stated code commitment; it does not certify the scientific analysis.

## Remaining launch sequence

1. Finalize the private fresh-word file and preserve the generation/selection audit: exact prompt, displayed generator identity and time, ordered candidates, exclusions, seeded selection, search checks and replacements. Record its exact-byte hash consistently in the collector, sample design and Claude amendment. Keep the words private until deliberate release.
2. Resolve the choices above, update Claude's timestamped amendment and final analyzer hash, and run the full offline suite on the native Windows collection machine. Development here used Linux, Python 3.12.14 and pinned NumPy 2.3.5.
3. Run the content-neutral paid preflight on the investigator's accounts, then select and freeze the final protocol before the first study request. A preflight failure may require another documented pre-collection resolution.
4. Collect fresh then known under that freeze. Keep response text and feature results unread until both batches close. Do not overwrite an existing freeze or change code during collection.

This repository is ready for the final analyst review. Final stimuli, Fable's choices and commitment, Windows checks, live preflight and the collection freeze remain outstanding.
