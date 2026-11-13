# Fable descriptive supplement

**Post hoc. Not confirmatory.** These are the descriptive summaries listed in section 7 of `prereg/CLAUDE_PREREG.md`. The frozen analyzer did not produce them, so they were generated on November 12, 2026 by `supplement/fable_descriptives.py`, after the confirmatory results were known. The list of summaries was registered before collection. The code that makes them was not frozen. Reporting revision 2 (2026-11-13) adds missing intervals and corrects resampling and exposure wording. See [the revision record](../REPORTING_REVISION.md).

- Scorer: `prereg/claude_scorer_v1_1.py`, unchanged. U, N and E here match the released `scores_v1.1.csv` on all 16,000 responses.
- U is a description form with no matched cue. N is nonrecognition with no description form. E is any description form. They are surface measures, not accuracy judgments.
- Brackets are unadjusted 95% word-bootstrap intervals (10,000 draws). Fresh words are resampled within their three source groups; known words within their two intent groups. A sampled word retains all its responses. Historical changes keep the old/new pair together. H4 combines known-minus-fresh differences with equal intent weights in every draw. No tests are run.
- Cue-position medians condition on responses with a matched cue; reality-wording rates condition on U. Word clusters with no qualifying response are retained in resampling. An asterisk marks intervals conditional on defined draws; the number of undefined draws is in the JSON. If the observed denominator is zero, the result is not estimable, not zero. Observed match counts are census totals of this corpus, not population estimates.
- Per-model intervals rest on 24 fresh or 8 known words and are wide. Absolute U rates are not comparable across providers.
- Full per-condition and per-category tables are in `descriptives.json`.

## 1. U, N and E by model and framing

### Fresh words

| Model | Framing | U | N | E |
| --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 [0.00, 0.00] | 0.99 [0.97, 1.00] | 0.00 [0.00, 0.00] |
| claude-sonnet-4-6 | real | 0.00 [0.00, 0.01] | 0.85 [0.80, 0.91] | 0.01 [0.00, 0.02] |
| claude-sonnet-4-6 | type_of | 0.07 [0.03, 0.13] | 0.89 [0.82, 0.96] | 0.10 [0.04, 0.17] |
| claude-sonnet-4-6 | imaginary | 0.45 [0.36, 0.54] | 0.08 [0.04, 0.13] | 0.91 [0.86, 0.96] |
| claude-haiku-4-5 | neutral | 0.00 [0.00, 0.00] | 0.98 [0.96, 1.00] | 0.01 [0.00, 0.03] |
| claude-haiku-4-5 | real | 0.09 [0.04, 0.16] | 0.74 [0.65, 0.82] | 0.14 [0.07, 0.23] |
| claude-haiku-4-5 | type_of | 0.17 [0.13, 0.22] | 0.72 [0.66, 0.79] | 0.28 [0.21, 0.34] |
| claude-haiku-4-5 | imaginary | 0.71 [0.65, 0.76] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| claude-sonnet-5-5 | neutral | 0.00 [0.00, 0.00] | 0.88 [0.79, 0.97] | 0.07 [0.02, 0.17] |
| claude-sonnet-5-5 | real | 0.00 [0.00, 0.00] | 0.87 [0.83, 0.91] | 0.12 [0.09, 0.16] |
| claude-sonnet-5-5 | type_of | 0.00 [0.00, 0.00] | 0.81 [0.76, 0.86] | 0.19 [0.14, 0.24] |
| claude-sonnet-5-5 | imaginary | 0.71 [0.65, 0.78] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| claude-haiku-5-5 | neutral | 0.00 [0.00, 0.00] | 0.95 [0.90, 0.99] | 0.05 [0.01, 0.10] |
| claude-haiku-5-5 | real | 0.00 [0.00, 0.00] | 0.93 [0.91, 0.95] | 0.07 [0.05, 0.09] |
| claude-haiku-5-5 | type_of | 0.00 [0.00, 0.00] | 0.87 [0.84, 0.90] | 0.13 [0.10, 0.16] |
| claude-haiku-5-5 | imaginary | 0.39 [0.30, 0.48] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| gpt-5.4-mini | neutral | 0.02 [0.00, 0.03] | 0.35 [0.23, 0.47] | 0.62 [0.50, 0.75] |
| gpt-5.4-mini | real | 0.07 [0.04, 0.10] | 0.56 [0.51, 0.62] | 0.36 [0.30, 0.41] |
| gpt-5.4-mini | type_of | 0.13 [0.08, 0.18] | 0.01 [0.00, 0.03] | 0.95 [0.92, 0.97] |
| gpt-5.4-mini | imaginary | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.94 [0.92, 0.96] |
| gpt-5.4-nano | neutral | 0.16 [0.07, 0.26] | 0.35 [0.26, 0.43] | 0.40 [0.28, 0.53] |
| gpt-5.4-nano | real | 0.26 [0.19, 0.32] | 0.28 [0.20, 0.38] | 0.62 [0.54, 0.71] |
| gpt-5.4-nano | type_of | 0.17 [0.11, 0.23] | 0.14 [0.09, 0.21] | 0.78 [0.70, 0.87] |
| gpt-5.4-nano | imaginary | 0.13 [0.09, 0.17] | 0.00 [0.00, 0.01] | 0.99 [0.97, 1.00] |
| gpt-6-sol | neutral | 0.13 [0.05, 0.23] | 0.79 [0.68, 0.90] | 0.17 [0.08, 0.28] |
| gpt-6-sol | real | 0.04 [0.02, 0.07] | 0.96 [0.93, 0.98] | 0.04 [0.02, 0.07] |
| gpt-6-sol | type_of | 0.41 [0.34, 0.47] | 0.54 [0.47, 0.61] | 0.45 [0.38, 0.52] |
| gpt-6-sol | imaginary | 0.69 [0.65, 0.73] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| gpt-6-luna | neutral | 0.07 [0.03, 0.13] | 0.68 [0.57, 0.79] | 0.26 [0.15, 0.38] |
| gpt-6-luna | real | 0.14 [0.10, 0.20] | 0.66 [0.57, 0.74] | 0.34 [0.25, 0.42] |
| gpt-6-luna | type_of | 0.09 [0.04, 0.17] | 0.79 [0.68, 0.89] | 0.20 [0.10, 0.31] |
| gpt-6-luna | imaginary | 0.74 [0.69, 0.80] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |

### Previously published words

| Model | Framing | U | N | E |
| --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 [0.00, 0.00] | 0.99 [0.96, 1.00] | 0.01 [0.00, 0.04] |
| claude-sonnet-4-6 | real | 0.00 [0.00, 0.00] | 0.97 [0.94, 1.00] | 0.00 [0.00, 0.00] |
| claude-sonnet-4-6 | type_of | 0.05 [0.01, 0.09] | 0.95 [0.90, 0.99] | 0.05 [0.01, 0.11] |
| claude-sonnet-4-6 | imaginary | 0.39 [0.28, 0.50] | 0.13 [0.03, 0.25] | 0.87 [0.75, 0.97] |
| claude-haiku-4-5 | neutral | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| claude-haiku-4-5 | real | 0.07 [0.01, 0.17] | 0.81 [0.70, 0.90] | 0.09 [0.03, 0.20] |
| claude-haiku-4-5 | type_of | 0.13 [0.06, 0.20] | 0.82 [0.74, 0.91] | 0.17 [0.09, 0.26] |
| claude-haiku-4-5 | imaginary | 0.72 [0.61, 0.80] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| claude-sonnet-5-5 | neutral | 0.00 [0.00, 0.00] | 0.97 [0.95, 1.00] | 0.03 [0.00, 0.05] |
| claude-sonnet-5-5 | real | 0.00 [0.00, 0.00] | 0.90 [0.87, 0.94] | 0.10 [0.06, 0.13] |
| claude-sonnet-5-5 | type_of | 0.00 [0.00, 0.00] | 0.74 [0.65, 0.82] | 0.25 [0.18, 0.35] |
| claude-sonnet-5-5 | imaginary | 0.75 [0.64, 0.85] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| claude-haiku-5-5 | neutral | 0.00 [0.00, 0.00] | 0.97 [0.95, 1.00] | 0.03 [0.00, 0.05] |
| claude-haiku-5-5 | real | 0.00 [0.00, 0.00] | 0.89 [0.85, 0.92] | 0.11 [0.08, 0.15] |
| claude-haiku-5-5 | type_of | 0.00 [0.00, 0.00] | 0.88 [0.85, 0.90] | 0.12 [0.10, 0.15] |
| claude-haiku-5-5 | imaginary | 0.30 [0.12, 0.53] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| gpt-5.4-mini | neutral | 0.03 [0.00, 0.05] | 0.33 [0.11, 0.55] | 0.66 [0.44, 0.86] |
| gpt-5.4-mini | real | 0.02 [0.00, 0.06] | 0.69 [0.61, 0.77] | 0.19 [0.14, 0.23] |
| gpt-5.4-mini | type_of | 0.07 [0.03, 0.11] | 0.07 [0.00, 0.19] | 0.86 [0.73, 0.95] |
| gpt-5.4-mini | imaginary | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.91 [0.88, 0.94] |
| gpt-5.4-nano | neutral | 0.10 [0.01, 0.21] | 0.45 [0.28, 0.64] | 0.39 [0.20, 0.59] |
| gpt-5.4-nano | real | 0.12 [0.09, 0.16] | 0.45 [0.36, 0.54] | 0.49 [0.40, 0.58] |
| gpt-5.4-nano | type_of | 0.05 [0.01, 0.09] | 0.24 [0.10, 0.42] | 0.67 [0.50, 0.83] |
| gpt-5.4-nano | imaginary | 0.09 [0.05, 0.13] | 0.00 [0.00, 0.01] | 0.97 [0.93, 0.99] |
| gpt-6-sol | neutral | 0.01 [0.00, 0.04] | 0.95 [0.85, 1.00] | 0.03 [0.00, 0.07] |
| gpt-6-sol | real | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| gpt-6-sol | type_of | 0.26 [0.19, 0.33] | 0.72 [0.65, 0.79] | 0.27 [0.20, 0.34] |
| gpt-6-sol | imaginary | 0.63 [0.50, 0.75] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |
| gpt-6-luna | neutral | 0.05 [0.00, 0.11] | 0.85 [0.68, 0.99] | 0.14 [0.00, 0.30] |
| gpt-6-luna | real | 0.13 [0.06, 0.21] | 0.72 [0.59, 0.82] | 0.28 [0.17, 0.41] |
| gpt-6-luna | type_of | 0.05 [0.00, 0.14] | 0.86 [0.65, 0.98] | 0.13 [0.02, 0.31] |
| gpt-6-luna | imaginary | 0.65 [0.53, 0.77] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |

## 2. Confirmatory contrasts, model by model

Fresh batch, except H4, which uses both. H4, H5 and H6 compare model groups, so each model's component is shown: for H4 the intent-standardised known-minus-fresh difference in N, for H5 the level of U, and for H6 the Claude-origin-minus-GPT-origin difference in N. These components are not separate confirmatory tests.

| Model | H1 E imaginary-real | H2 N type_of-real | H3 U animal-no_intent | H4 N known-fresh (intent-standardised) | H5 U presupposition (level) | H6 N claude_made-gpt_made |
| --- | --- | --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | +0.91 [+0.86, +0.95] | +0.04 [-0.03, +0.11] | -0.05 [-0.09, -0.02] | +0.06 [+0.02, +0.10] | 0.04 [0.02, 0.07] | +0.06 [-0.06, +0.19] |
| claude-haiku-4-5 | +0.86 [+0.78, +0.93] | -0.01 [-0.11, +0.08] | -0.01 [-0.10, +0.10] | +0.07 [-0.01, +0.16] | 0.13 [0.09, 0.18] | +0.06 [-0.04, +0.18] |
| claude-sonnet-5-5 | +0.88 [+0.84, +0.91] | -0.06 [-0.12, -0.00] | +0.00 [+0.00, +0.00] | +0.01 [-0.04, +0.08] | 0.00 [0.00, 0.00] | -0.04 [-0.10, +0.01] |
| claude-haiku-5-5 | +0.93 [+0.91, +0.95] | -0.06 [-0.10, -0.03] | +0.00 [+0.00, +0.00] | -0.02 [-0.04, +0.01] | 0.00 [0.00, 0.00] | +0.03 [-0.01, +0.06] |
| gpt-5.4-mini | +0.58 [+0.53, +0.64] | -0.55 [-0.61, -0.50] | -0.01 [-0.07, +0.04] | +0.07 [-0.02, +0.17] | 0.10 [0.07, 0.13] | -0.04 [-0.10, +0.02] |
| gpt-5.4-nano | +0.36 [+0.28, +0.45] | -0.14 [-0.21, -0.06] | -0.02 [-0.15, +0.10] | +0.11 [-0.02, +0.26] | 0.21 [0.16, 0.27] | +0.05 [-0.07, +0.16] |
| gpt-6-sol | +0.96 [+0.93, +0.98] | -0.42 [-0.49, -0.34] | +0.00 [-0.08, +0.08] | +0.13 [+0.07, +0.19] | 0.22 [0.19, 0.26] | -0.15 [-0.21, -0.08] |
| gpt-6-luna | +0.66 [+0.58, +0.75] | +0.14 [-0.03, +0.29] | -0.03 [-0.11, +0.06] | +0.08 [-0.05, +0.19] | 0.12 [0.08, 0.16] | -0.13 [-0.26, -0.00] |

## 3. Definition and cue order, length, context requests and offers: fresh words

Order columns are shares of responses, using an unnegated exact-target definition match. E can also be triggered by attribute matches, so "cue only" need not mean E = 0. "First cue" is the median first-cue character position divided by normalised response length, among responses with a cue. All summaries below include word-bootstrap intervals.

| Model | Framing | Def. first | Cue first | Def. only | Cue only | Neither |
| --- | --- | --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| claude-sonnet-4-6 | real | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.01] | 0.88 [0.83, 0.93] | 0.11 [0.07, 0.16] |
| claude-sonnet-4-6 | type_of | 0.03 [0.01, 0.04] | 0.00 [0.00, 0.00] | 0.07 [0.03, 0.13] | 0.90 [0.83, 0.96] | 0.00 [0.00, 0.00] |
| claude-sonnet-4-6 | imaginary | 0.41 [0.34, 0.49] | 0.05 [0.01, 0.09] | 0.45 [0.36, 0.54] | 0.09 [0.04, 0.14] | 0.00 [0.00, 0.00] |
| claude-haiku-4-5 | neutral | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| claude-haiku-4-5 | real | 0.01 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.08 [0.03, 0.13] | 0.81 [0.73, 0.88] | 0.11 [0.08, 0.13] |
| claude-haiku-4-5 | type_of | 0.08 [0.06, 0.10] | 0.00 [0.00, 0.01] | 0.17 [0.13, 0.21] | 0.74 [0.68, 0.80] | 0.01 [0.00, 0.03] |
| claude-haiku-4-5 | imaginary | 0.29 [0.24, 0.35] | 0.00 [0.00, 0.00] | 0.70 [0.65, 0.76] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] |
| claude-sonnet-5-5 | neutral | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.98 [0.96, 1.00] | 0.01 [0.00, 0.03] |
| claude-sonnet-5-5 | real | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| claude-sonnet-5-5 | type_of | 0.00 [0.00, 0.00] | 0.07 [0.04, 0.11] | 0.00 [0.00, 0.00] | 0.93 [0.89, 0.96] | 0.00 [0.00, 0.00] |
| claude-sonnet-5-5 | imaginary | 0.29 [0.23, 0.35] | 0.00 [0.00, 0.00] | 0.71 [0.65, 0.78] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |
| claude-haiku-5-5 | neutral | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] |
| claude-haiku-5-5 | real | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] | 0.99 [0.99, 1.00] | 0.00 [0.00, 0.01] |
| claude-haiku-5-5 | type_of | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] | 1.00 [0.99, 1.00] | 0.00 [0.00, 0.00] |
| claude-haiku-5-5 | imaginary | 0.55 [0.47, 0.62] | 0.06 [0.03, 0.09] | 0.39 [0.30, 0.48] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |
| gpt-5.4-mini | neutral | 0.25 [0.15, 0.36] | 0.27 [0.16, 0.38] | 0.01 [0.00, 0.03] | 0.45 [0.33, 0.57] | 0.03 [0.00, 0.07] |
| gpt-5.4-mini | real | 0.13 [0.09, 0.17] | 0.14 [0.11, 0.17] | 0.07 [0.04, 0.10] | 0.63 [0.58, 0.69] | 0.04 [0.02, 0.05] |
| gpt-5.4-mini | type_of | 0.51 [0.45, 0.57] | 0.27 [0.19, 0.34] | 0.13 [0.08, 0.18] | 0.09 [0.06, 0.12] | 0.00 [0.00, 0.00] |
| gpt-5.4-mini | imaginary | 0.74 [0.68, 0.81] | 0.12 [0.08, 0.16] | 0.00 [0.00, 0.00] | 0.14 [0.10, 0.18] | 0.00 [0.00, 0.00] |
| gpt-5.4-nano | neutral | 0.08 [0.03, 0.16] | 0.10 [0.05, 0.16] | 0.12 [0.05, 0.22] | 0.49 [0.38, 0.60] | 0.20 [0.11, 0.31] |
| gpt-5.4-nano | real | 0.14 [0.09, 0.20] | 0.10 [0.07, 0.13] | 0.18 [0.12, 0.24] | 0.45 [0.35, 0.56] | 0.13 [0.07, 0.20] |
| gpt-5.4-nano | type_of | 0.39 [0.29, 0.49] | 0.18 [0.12, 0.24] | 0.15 [0.09, 0.22] | 0.24 [0.16, 0.33] | 0.05 [0.01, 0.10] |
| gpt-5.4-nano | imaginary | 0.78 [0.71, 0.85] | 0.04 [0.01, 0.07] | 0.12 [0.08, 0.16] | 0.05 [0.02, 0.09] | 0.01 [0.00, 0.02] |
| gpt-6-sol | neutral | 0.04 [0.01, 0.08] | 0.00 [0.00, 0.00] | 0.13 [0.05, 0.23] | 0.79 [0.68, 0.90] | 0.03 [0.00, 0.07] |
| gpt-6-sol | real | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.04 [0.02, 0.06] | 0.96 [0.93, 0.98] | 0.01 [0.00, 0.01] |
| gpt-6-sol | type_of | 0.04 [0.02, 0.07] | 0.00 [0.00, 0.00] | 0.41 [0.34, 0.47] | 0.54 [0.47, 0.61] | 0.01 [0.00, 0.02] |
| gpt-6-sol | imaginary | 0.31 [0.27, 0.35] | 0.00 [0.00, 0.00] | 0.69 [0.65, 0.73] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| gpt-6-luna | neutral | 0.17 [0.09, 0.24] | 0.01 [0.00, 0.03] | 0.07 [0.03, 0.13] | 0.71 [0.61, 0.81] | 0.04 [0.01, 0.08] |
| gpt-6-luna | real | 0.19 [0.14, 0.25] | 0.00 [0.00, 0.00] | 0.14 [0.10, 0.19] | 0.66 [0.57, 0.74] | 0.01 [0.00, 0.01] |
| gpt-6-luna | type_of | 0.09 [0.04, 0.15] | 0.01 [0.00, 0.01] | 0.09 [0.03, 0.17] | 0.80 [0.69, 0.90] | 0.01 [0.00, 0.01] |
| gpt-6-luna | imaginary | 0.26 [0.20, 0.31] | 0.00 [0.00, 0.00] | 0.74 [0.69, 0.80] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

| Model | Framing | First cue | Words, mean | Words, median | Context request | Offer |
| --- | --- | --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.04 [0.03, 0.04] | 88.4 [82.8, 94.4] | 82.5 [78.0, 88.5] | 0.99 [0.97, 1.00] | 0.20 [0.11, 0.30] |
| claude-sonnet-4-6 | real | 0.03 [0.03, 0.05] | 98.0 [95.0, 101.3] | 98.0 [96.0, 101.0] | 0.99 [0.96, 1.00] | 0.07 [0.04, 0.11] |
| claude-sonnet-4-6 | type_of | 0.05 [0.02, 0.08] | 126.9 [119.7, 134.4] | 118.5 [112.5, 124.5] | 0.87 [0.80, 0.94] | 0.39 [0.33, 0.45] |
| claude-sonnet-4-6 | imaginary | 0.03 [0.03, 0.04] | 197.4 [190.9, 203.3] | 206.0 [203.0, 208.0] | 0.12 [0.07, 0.17] | 0.44 [0.35, 0.53] |
| claude-haiku-4-5 | neutral | 0.02 [0.01, 0.02] | 98.3 [94.7, 102.1] | 99.0 [94.0, 104.5] | 1.00 [1.00, 1.00] | 0.73 [0.64, 0.82] |
| claude-haiku-4-5 | real | 0.01 [0.01, 0.02] | 116.6 [111.7, 122.1] | 112.0 [109.0, 116.0] | 0.90 [0.82, 0.97] | 0.55 [0.48, 0.63] |
| claude-haiku-4-5 | type_of | 0.02 [0.02, 0.02] | 132.8 [128.9, 136.6] | 121.0 [119.5, 125.0] | 0.75 [0.69, 0.81] | 0.56 [0.52, 0.60] |
| claude-haiku-4-5 | imaginary | 0.65 [0.10, 0.77] | 194.3 [193.0, 195.7] | 195.0 [193.5, 196.0] | 0.00 [0.00, 0.01] | 0.11 [0.08, 0.13] |
| claude-sonnet-5-5 | neutral | 0.04 [0.04, 0.05] | 160.0 [155.7, 164.4] | 159.0 [157.0, 163.0] | 0.96 [0.90, 1.00] | 0.91 [0.86, 0.95] |
| claude-sonnet-5-5 | real | 0.01 [0.00, 0.04] | 184.7 [182.2, 187.1] | 184.0 [181.0, 187.0] | 0.99 [0.98, 1.00] | 0.84 [0.79, 0.88] |
| claude-sonnet-5-5 | type_of | 0.04 [0.04, 0.04] | 185.4 [183.7, 187.1] | 185.0 [183.0, 186.0] | 0.91 [0.87, 0.94] | 0.95 [0.93, 0.97] |
| claude-sonnet-5-5 | imaginary | 0.07 [0.06, 0.31] | 295.1 [289.8, 300.4] | 290.0 [285.0, 294.0] | 0.01 [0.00, 0.03] | 0.34 [0.29, 0.38] |
| claude-haiku-5-5 | neutral | 0.01 [0.01, 0.01] | 124.0 [117.7, 130.1] | 125.0 [117.5, 134.0] | 0.98 [0.96, 1.00] | 0.92 [0.86, 0.97] |
| claude-haiku-5-5 | real | 0.00 [0.00, 0.00] | 139.7 [136.4, 143.0] | 141.0 [135.5, 146.0] | 1.00 [1.00, 1.00] | 0.76 [0.71, 0.82] |
| claude-haiku-5-5 | type_of | 0.00 [0.00, 0.01] | 125.5 [122.9, 128.2] | 121.0 [117.0, 124.5] | 0.99 [0.98, 1.00] | 0.96 [0.94, 0.97] |
| claude-haiku-5-5 | imaginary | 0.02 [0.02, 0.02] | 244.9 [238.8, 251.1] | 244.5 [236.0, 252.0] | 0.04 [0.01, 0.06] | 0.34 [0.26, 0.44] |
| gpt-5.4-mini | neutral | 0.02 [0.02, 0.03] | 111.2 [99.9, 122.2] | 113.0 [96.0, 128.0] | 0.13 [0.05, 0.23] | 0.66 [0.56, 0.75] |
| gpt-5.4-mini | real | 0.03 [0.02, 0.03] | 104.7 [101.6, 108.0] | 93.5 [91.0, 96.0] | 0.51 [0.46, 0.57] | 0.75 [0.71, 0.80] |
| gpt-5.4-mini | type_of | 0.02 [0.02, 0.03] | 142.1 [137.4, 146.7] | 139.0 [133.0, 144.5] | 0.01 [0.00, 0.01] | 0.47 [0.42, 0.51] |
| gpt-5.4-mini | imaginary | 0.02 [0.02, 0.02] | 172.0 [168.6, 175.3] | 167.0 [164.0, 172.5] | 0.01 [0.00, 0.01] | 0.42 [0.39, 0.46] |
| gpt-5.4-nano | neutral | 0.02 [0.01, 0.03] | 105.6 [97.7, 113.8] | 101.5 [94.0, 110.0] | 0.75 [0.64, 0.85] | 0.42 [0.31, 0.53] |
| gpt-5.4-nano | real | 0.03 [0.02, 0.05] | 140.2 [128.5, 152.8] | 131.5 [120.0, 144.5] | 0.67 [0.59, 0.75] | 0.42 [0.37, 0.47] |
| gpt-5.4-nano | type_of | 0.03 [0.02, 0.03] | 137.6 [127.0, 150.3] | 135.0 [128.0, 145.0] | 0.64 [0.56, 0.72] | 0.27 [0.22, 0.33] |
| gpt-5.4-nano | imaginary | 0.01 [0.01, 0.01] | 265.0 [252.4, 278.2] | 265.0 [249.0, 278.5] | 0.03 [0.02, 0.05] | 0.26 [0.22, 0.30] |
| gpt-6-sol | neutral | 0.04 [0.03, 0.04] | 23.3 [21.4, 25.2] | 20.5 [19.0, 25.0] | 0.30 [0.17, 0.44] | 0.14 [0.06, 0.23] |
| gpt-6-sol | real | 0.02 [0.02, 0.02] | 30.4 [29.7, 31.1] | 30.0 [30.0, 30.5] | 0.83 [0.78, 0.89] | 0.03 [0.02, 0.05] |
| gpt-6-sol | type_of | 0.03 [0.02, 0.03] | 32.2 [30.6, 34.2] | 30.0 [29.0, 32.0] | 0.28 [0.24, 0.33] | 0.16 [0.11, 0.22] |
| gpt-6-sol | imaginary | 0.07 [0.06, 0.08] | 53.4 [52.0, 55.1] | 53.0 [52.0, 54.0] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |
| gpt-6-luna | neutral | 0.05 [0.03, 0.05] | 35.8 [32.5, 39.5] | 33.5 [28.5, 38.0] | 0.57 [0.43, 0.71] | 0.17 [0.10, 0.27] |
| gpt-6-luna | real | 0.02 [0.02, 0.03] | 46.3 [44.3, 48.5] | 42.0 [41.0, 43.0] | 0.67 [0.59, 0.76] | 0.42 [0.34, 0.50] |
| gpt-6-luna | type_of | 0.03 [0.02, 0.03] | 45.0 [42.7, 47.4] | 42.0 [41.0, 43.5] | 0.66 [0.56, 0.76] | 0.46 [0.36, 0.55] |
| gpt-6-luna | imaginary | 0.04 [0.04, 0.05] | 86.5 [83.7, 89.3] | 89.5 [87.0, 92.0] | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |

The known-batch version of this table is in `descriptives.json`.

## 4. Reality-assertion wording in unmarked descriptions under real framings

The conditional rate uses U responses as its denominator. Sparse U can leave very few contributing words; a collapsed bootstrap interval then describes the observed support and does not establish population-level precision.

| Batch | Model | Real-framed trials | Unmarked descriptions | Words with U | With reality wording | Reality wording given U |
| --- | --- | --- | --- | --- | --- | --- |
| fresh | claude-sonnet-4-6 | 360 | 1 | 1 | 0 | 0.00 [0.00, 0.00]* |
| fresh | claude-haiku-4-5 | 360 | 34 | 11 | 1 | 0.03 [0.00, 0.12] |
| fresh | claude-sonnet-5-5 | 360 | 0 | 0 | 0 | not estimable |
| fresh | claude-haiku-5-5 | 360 | 0 | 0 | 0 | not estimable |
| fresh | gpt-5.4-mini | 360 | 24 | 14 | 12 | 0.50 [0.36, 0.68] |
| fresh | gpt-5.4-nano | 360 | 92 | 21 | 64 | 0.70 [0.60, 0.79] |
| fresh | gpt-6-sol | 360 | 15 | 7 | 0 | 0.00 [0.00, 0.00] |
| fresh | gpt-6-luna | 360 | 52 | 17 | 12 | 0.23 [0.13, 0.37] |
| known | claude-sonnet-4-6 | 240 | 0 | 0 | 0 | not estimable |
| known | claude-haiku-4-5 | 240 | 16 | 3 | 2 | 0.12 [0.00, 0.15]* |
| known | claude-sonnet-5-5 | 240 | 0 | 0 | 0 | not estimable |
| known | claude-haiku-5-5 | 240 | 0 | 0 | 0 | not estimable |
| known | gpt-5.4-mini | 240 | 5 | 1 | 4 | 0.80 [0.80, 0.80]* |
| known | gpt-5.4-nano | 240 | 30 | 7 | 19 | 0.63 [0.60, 0.68] |
| known | gpt-6-sol | 240 | 0 | 0 | 0 | not estimable |
| known | gpt-6-luna | 240 | 31 | 5 | 8 | 0.26 [0.10, 0.46] |

## 5. Exposure strings

Responses containing "bestiary" or "chesterton", any case: **92 of 16000**.

| Batch | Model | Term | Responses |
| --- | --- | --- | --- |
| fresh | claude-haiku-5-5 | bestiary | 1 |
| fresh | claude-sonnet-5-5 | bestiary | 4 |
| fresh | gpt-5.4-mini | bestiary | 49 |
| fresh | gpt-5.4-nano | bestiary | 5 |
| known | claude-haiku-4-5 | bestiary | 1 |
| known | claude-haiku-5-5 | bestiary | 4 |
| known | claude-sonnet-5-5 | bestiary | 3 |
| known | gpt-5.4-mini | bestiary | 20 |
| known | gpt-5.4-nano | bestiary | 5 |

Section 10 of the [precollection amendment](../../prereg/CLAUDE_PREREG_AMENDMENT_1.md) already replaced the original preregistration's direct-exposure interpretation: these strings flag responses for contextual review and do not by themselves establish exposure. 59 of the 92 hits occur on fresh words. Fresh-word prompts do not rule out a model's prior exposure to the original study. No response contains "chesterton". Every hit is listed with surrounding text in `descriptives.json`. Fable's post hoc contextual reading of the original supplement classified all hits as generic uses of "bestiary" (for example, an offer to write "a fantasy bestiary entry"), with no explicit reference to the original study. That contextual assessment is not an independently validated annotation. The reviewed matches do not establish exposure; neither this search nor the fresh/known comparison establishes its absence.

## 6. Historical models: known batch against the original study

Same eight words, same scorer, ten responses per word and condition in each run. The original runs used lower output caps (400 Anthropic, 700 OpenAI) and earlier dates. This is a stability check, not a controlled comparison. Change is known batch minus original, with a paired interval over the eight words, stratified by intent.

| Model | Framing | U: original → now (change) | N: original → now (change) | E: original → now (change) |
| --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 1.00 → 0.99 (-0.01 [-0.04, +0.00]) | 0.00 → 0.01 (+0.01 [+0.00, +0.04]) |
| claude-sonnet-4-6 | real | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.96 → 0.97 (+0.01 [-0.01, +0.04]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) |
| claude-sonnet-4-6 | type_of | 0.00 → 0.05 (+0.05 [+0.01, +0.09]) | 1.00 → 0.95 (-0.05 [-0.11, -0.01]) | 0.00 → 0.05 (+0.05 [+0.01, +0.11]) |
| claude-sonnet-4-6 | imaginary | 0.42 → 0.39 (-0.03 [-0.08, +0.03]) | 0.12 → 0.13 (+0.01 [-0.02, +0.05]) | 0.87 → 0.87 (+0.00 [-0.05, +0.04]) |
| claude-haiku-4-5 | neutral | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.97 → 1.00 (+0.03 [+0.00, +0.07]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) |
| claude-haiku-4-5 | real | 0.07 → 0.07 (+0.00 [-0.01, +0.01]) | 0.76 → 0.81 (+0.05 [+0.03, +0.07]) | 0.12 → 0.09 (-0.03 [-0.07, +0.01]) |
| claude-haiku-4-5 | type_of | 0.10 → 0.13 (+0.03 [+0.00, +0.07]) | 0.82 → 0.82 (+0.00 [-0.03, +0.04]) | 0.18 → 0.17 (-0.00 [-0.04, +0.03]) |
| claude-haiku-4-5 | imaginary | 0.70 → 0.72 (+0.02 [-0.04, +0.07]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 1.00 → 1.00 (+0.00 [+0.00, +0.00]) |
| gpt-5.4-mini | neutral | 0.01 → 0.03 (+0.01 [+0.00, +0.04]) | 0.34 → 0.33 (-0.01 [-0.10, +0.07]) | 0.62 → 0.66 (+0.04 [-0.07, +0.14]) |
| gpt-5.4-mini | real | 0.01 → 0.02 (+0.01 [-0.01, +0.04]) | 0.63 → 0.69 (+0.06 [-0.06, +0.18]) | 0.23 → 0.19 (-0.04 [-0.12, +0.03]) |
| gpt-5.4-mini | type_of | 0.07 → 0.07 (-0.00 [-0.05, +0.04]) | 0.03 → 0.07 (+0.03 [+0.00, +0.10]) | 0.87 → 0.86 (-0.01 [-0.05, +0.04]) |
| gpt-5.4-mini | imaginary | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.00 → 0.01 (+0.00 [+0.00, +0.01]) | 0.93 → 0.91 (-0.02 [-0.07, +0.02]) |
| gpt-5.4-nano | neutral | 0.14 → 0.10 (-0.04 [-0.15, +0.11]) | 0.39 → 0.45 (+0.06 [-0.12, +0.24]) | 0.46 → 0.39 (-0.07 [-0.26, +0.10]) |
| gpt-5.4-nano | real | 0.13 → 0.12 (-0.00 [-0.06, +0.06]) | 0.47 → 0.45 (-0.02 [-0.09, +0.05]) | 0.47 → 0.49 (+0.03 [-0.05, +0.10]) |
| gpt-5.4-nano | type_of | 0.09 → 0.05 (-0.04 [-0.08, +0.00]) | 0.25 → 0.24 (-0.02 [-0.06, +0.03]) | 0.65 → 0.67 (+0.03 [-0.03, +0.08]) |
| gpt-5.4-nano | imaginary | 0.09 → 0.09 (+0.00 [-0.05, +0.05]) | 0.00 → 0.00 (+0.00 [-0.01, +0.01]) | 0.97 → 0.97 (-0.00 [-0.04, +0.03]) |
