# Fable descriptive reporting revision

Revision 2, November 13, 2026. This is a post hoc reporting correction to the supplement introduced in commit `61622596cb92e7d70d8a713ca00e33ddf67a375f` and merged as PR #3. The original supplement remains available in that commit. Neither supplement version is confirmatory. The raw responses, frozen scorers, registered protocols, confirmatory analyzers, and original release archives are unchanged.

## Corrections

- **Missing uncertainty estimates:** added 95% word-bootstrap intervals for the per-model H4 components, definition/cue-order proportions, first-cue position medians, and response-length medians. Mean response-length intervals, already present in the original JSON, now appear in the summary. Added conditional reality-wording rates with intervals alongside the observed counts.
- **Resampling:** fresh words remain in their three source strata in every bootstrap, including both no-intent sources in H3 and H4. The eight previously published words remain in their two intent strata, including the paired original-versus-current stability comparison. H4 gives each intent stratum one-half weight in every draw. The original H3 interval pooled the two no-intent sources, and the historical interval pooled all eight words; its blanket within-source description was therefore too broad. The revised intervals use a consistent method and remain unadjusted, descriptive intervals.
- **Conditional summaries:** first-cue position conditions on responses with a matched cue; reality wording given U conditions on U responses. Complete word clusters, including those without qualifying responses, are resampled. Intervals use defined draws, and the JSON reports `undefined_draws`. A zero observed denominator is `null`/not estimable, never a zero rate. Sparse conditional rates can have collapsed intervals because the empirical support is narrow; this is not evidence of population precision. Corpus string-match counts are observed totals, not population estimates.
- **Exposure interpretation:** the summary now cites section 10 of the precollection amendment, which already withdrew the original preregistration's automatic exposure inference. Fresh-word prompts cannot rule out prior exposure to the original study. Fable's original contextual reading of the 92 string matches is attributed as a post hoc assessment, not independent annotation. Those matches do not establish exposure, and the search does not establish its absence.
- **Reporting status:** the README now distinguishes available Fable descriptives from the pooled GPT 50-word and 100-word prefix sensitivities that remain unestimable under the registered complete-panel rule. Per-model H4, H5, and H6 entries are explicitly components of model-group comparisons, not new confirmatory tests.

All previously reported point estimates and corpus counts are preserved except one rounding correction: the Haiku 5.5 H4 component changes from -0.0151 to -0.0152 (a 0.01-percentage-point display difference), because the equal-intent mean is now rounded only after combining unrounded stratum estimates. No original confirmatory estimate, interval, p-value, or conclusion is revised. Supplement intervals can change because of the corrected strata and the sequence of bootstrap draws.

## JSON format

`schema_version` is now 2. Entries under `form[].order`, `form[].first_cue_frac_median`, and `form[].words_median` are estimate/interval objects instead of bare numbers. Conditional summaries include `undefined_draws`. The H4 key no longer says `point only`. `reality_wording.table` adds `unmarked_words` and `reality_given_unmarked`. The revision and bootstrap metadata identify these changes. Consumers of the original JSON should update these field accesses.

## Reproduction

Use the original [raw-data release](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/raw-data-2026-11-11) and [analysis release](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/analysis-v1-2026-11-11). Extract the raw snapshot and use its `data` directory. Extract the analysis archive to obtain `analysis/claude/scores_v1.1.csv`. Check out the original Bestiary repository at commit `7fec51af5d28b743763225f4dd52ab29a4cb4d60` for the historical comparison. From this repository's root:

```bash
python supplement/fable_descriptives.py \
  --data /path/to/raw-snapshot/data \
  --orig /path/to/the-artificial-bestiary \
  --released-scores /path/to/analysis/claude/scores_v1.1.csv
```

The historical comparison reads `Retest_nonanimal_nonsense/Results/retest.jsonl`, `Haiku v3 Retest/Results/haiku_results.jsonl`, and `GPT_Retest_1600_nanomini/gpt_full_800_nano_mini_results.csv`. The fixed bootstrap seed is `20261112`, with 10,000 draws. This revision was regenerated using Python 3.12.14 and NumPy 2.3.5; the collection runtime remains as recorded in the original freeze manifest.

| Input | SHA-256 |
| --- | --- |
| Original raw snapshot archive | `f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6` |
| `data/attempts.jsonl` | `70856ceba363fe94b76fae9dbc0bd30ae0035e01470a128046c57424eba96a98` |
| Unchanged `prereg/claude_scorer_v1_1.py` | `7cebfa2c4e4524ec6a48fd3097485fce758edce20fd4b5773fe466e1ead4f967` |

## Validation

- Before editing, independently regenerated the original supplement from the raw responses and historical sources: its entire parsed JSON matched the committed original exactly.
- Regenerated the revised supplement from all 16,000 study responses. U/N/E match the original released score CSV on every response.
- Checked rates, model contrasts, order shares, medians, historical point estimates, exposure matches, and corpus counts against the original supplement. Only the documented H4 rounding difference changes a previously reported point estimate.
- All 69 repository tests pass, including seven new statistical regression tests for source-stratum preservation, equal intent weights, whole-word median resampling, paired ratios, and empty conditional denominators.

These checks validate this reporting revision. They do not add independent semantic labels or turn mechanical features into validated factual-error measurements.
