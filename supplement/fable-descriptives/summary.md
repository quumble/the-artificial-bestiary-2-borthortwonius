# Fable descriptive supplement

**Post hoc. Not confirmatory.** These are the descriptive summaries listed in section 7 of `prereg/CLAUDE_PREREG.md`. The frozen analyzer did not produce them, so they were generated on November 12, 2026 by `supplement/fable_descriptives.py`, after the confirmatory results were known. The list of summaries was registered before collection. The code that makes them was not frozen.

- Scorer: `prereg/claude_scorer_v1_1.py`, unchanged. U, N and E here match the released `scores_v1.1.csv` on all 16,000 responses.
- U is a description form with no matched cue. N is nonrecognition with no description form. E is any description form. They are surface measures, not accuracy judgments.
- Brackets are unadjusted 95% word-bootstrap intervals (10,000 draws, words resampled within source group). No tests are run.
- Per-model intervals rest on 24 fresh or 8 known words and are wide. Absolute U rates are not comparable across providers.
- Full per-condition and per-category tables are in `descriptives.json`.

## 1. U, N and E by model and framing: Fresh words

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

## 1. U, N and E by model and framing: Previously published words

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

Fresh batch, except H4, which uses both. H4 and H5 are contrasts between model groups, so each model's contribution is shown: for H4 the known-minus-fresh difference in N, for H5 the level of U.

| Model | H1 E imaginary-real | H2 N type_of-real | H3 U animal-no_intent | H4 N known-fresh (intent-standardised; point only) | H5 U presupposition (level) | H6 N claude_made-gpt_made |
| --- | --- | --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | +0.91 [+0.86, +0.95] | +0.04 [-0.03, +0.11] | -0.05 [-0.09, -0.02] | +0.06 | 0.04 [0.02, 0.07] | +0.06 [-0.06, +0.19] |
| claude-haiku-4-5 | +0.86 [+0.78, +0.93] | -0.01 [-0.11, +0.08] | -0.01 [-0.10, +0.10] | +0.07 | 0.13 [0.09, 0.18] | +0.06 [-0.04, +0.18] |
| claude-sonnet-5-5 | +0.88 [+0.84, +0.91] | -0.06 [-0.12, -0.00] | +0.00 [+0.00, +0.00] | +0.01 | 0.00 [0.00, 0.00] | -0.04 [-0.10, +0.01] |
| claude-haiku-5-5 | +0.93 [+0.91, +0.95] | -0.06 [-0.10, -0.03] | +0.00 [+0.00, +0.00] | -0.02 | 0.00 [0.00, 0.00] | +0.03 [-0.01, +0.06] |
| gpt-5.4-mini | +0.58 [+0.53, +0.64] | -0.55 [-0.61, -0.50] | -0.01 [-0.07, +0.04] | +0.07 | 0.10 [0.07, 0.13] | -0.04 [-0.10, +0.02] |
| gpt-5.4-nano | +0.36 [+0.28, +0.45] | -0.14 [-0.21, -0.06] | -0.02 [-0.15, +0.11] | +0.11 | 0.21 [0.16, 0.27] | +0.05 [-0.07, +0.16] |
| gpt-6-sol | +0.96 [+0.93, +0.98] | -0.42 [-0.49, -0.34] | +0.00 [-0.09, +0.09] | +0.13 | 0.22 [0.19, 0.26] | -0.15 [-0.21, -0.08] |
| gpt-6-luna | +0.66 [+0.58, +0.75] | +0.14 [-0.03, +0.29] | -0.03 [-0.12, +0.06] | +0.08 | 0.12 [0.08, 0.16] | -0.13 [-0.26, -0.00] |

## 3. Definition and cue order, length, context requests and offers: fresh words

Order columns are shares of responses. "First cue" is the median position of the first cue as a fraction of the response, among responses with a cue.

| Model | Framing | Def. first | Cue first | Def. only | Cue only | Neither | First cue | Words, mean | Words, median | Context request | Offer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.04 | 88 | 82 | 0.99 [0.97, 1.00] | 0.20 [0.11, 0.30] |
| claude-sonnet-4-6 | real | 0.00 | 0.00 | 0.00 | 0.88 | 0.11 | 0.03 | 98 | 98 | 0.99 [0.96, 1.00] | 0.07 [0.04, 0.11] |
| claude-sonnet-4-6 | type_of | 0.03 | 0.00 | 0.07 | 0.90 | 0.00 | 0.05 | 127 | 118 | 0.87 [0.80, 0.93] | 0.39 [0.33, 0.45] |
| claude-sonnet-4-6 | imaginary | 0.41 | 0.05 | 0.45 | 0.09 | 0.00 | 0.03 | 197 | 206 | 0.12 [0.08, 0.17] | 0.44 [0.35, 0.53] |
| claude-haiku-4-5 | neutral | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.02 | 98 | 99 | 1.00 [1.00, 1.00] | 0.73 [0.64, 0.82] |
| claude-haiku-4-5 | real | 0.01 | 0.00 | 0.08 | 0.81 | 0.11 | 0.01 | 117 | 112 | 0.90 [0.82, 0.97] | 0.55 [0.48, 0.63] |
| claude-haiku-4-5 | type_of | 0.08 | 0.00 | 0.17 | 0.74 | 0.01 | 0.02 | 133 | 121 | 0.75 [0.69, 0.81] | 0.56 [0.52, 0.60] |
| claude-haiku-4-5 | imaginary | 0.29 | 0.00 | 0.70 | 0.00 | 0.00 | 0.65 | 194 | 195 | 0.00 [0.00, 0.01] | 0.11 [0.08, 0.14] |
| claude-sonnet-5-5 | neutral | 0.00 | 0.01 | 0.00 | 0.98 | 0.01 | 0.04 | 160 | 159 | 0.96 [0.90, 1.00] | 0.91 [0.86, 0.95] |
| claude-sonnet-5-5 | real | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.01 | 185 | 184 | 0.99 [0.98, 1.00] | 0.84 [0.79, 0.88] |
| claude-sonnet-5-5 | type_of | 0.00 | 0.07 | 0.00 | 0.93 | 0.00 | 0.04 | 185 | 185 | 0.91 [0.87, 0.94] | 0.95 [0.93, 0.97] |
| claude-sonnet-5-5 | imaginary | 0.29 | 0.00 | 0.71 | 0.00 | 0.00 | 0.07 | 295 | 290 | 0.01 [0.00, 0.03] | 0.34 [0.29, 0.38] |
| claude-haiku-5-5 | neutral | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.01 | 124 | 125 | 0.98 [0.96, 1.00] | 0.92 [0.87, 0.97] |
| claude-haiku-5-5 | real | 0.00 | 0.00 | 0.00 | 0.99 | 0.00 | 0.00 | 140 | 141 | 1.00 [1.00, 1.00] | 0.76 [0.71, 0.82] |
| claude-haiku-5-5 | type_of | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 126 | 121 | 0.99 [0.98, 1.00] | 0.96 [0.94, 0.97] |
| claude-haiku-5-5 | imaginary | 0.55 | 0.06 | 0.39 | 0.00 | 0.00 | 0.02 | 245 | 244 | 0.04 [0.01, 0.06] | 0.34 [0.26, 0.44] |
| gpt-5.4-mini | neutral | 0.25 | 0.27 | 0.01 | 0.45 | 0.03 | 0.02 | 111 | 113 | 0.13 [0.05, 0.23] | 0.66 [0.56, 0.75] |
| gpt-5.4-mini | real | 0.13 | 0.14 | 0.07 | 0.63 | 0.04 | 0.03 | 105 | 94 | 0.51 [0.46, 0.57] | 0.75 [0.70, 0.80] |
| gpt-5.4-mini | type_of | 0.51 | 0.27 | 0.13 | 0.09 | 0.00 | 0.02 | 142 | 139 | 0.01 [0.00, 0.01] | 0.47 [0.42, 0.52] |
| gpt-5.4-mini | imaginary | 0.74 | 0.12 | 0.00 | 0.14 | 0.00 | 0.02 | 172 | 167 | 0.01 [0.00, 0.01] | 0.42 [0.39, 0.46] |
| gpt-5.4-nano | neutral | 0.08 | 0.10 | 0.12 | 0.49 | 0.20 | 0.02 | 106 | 102 | 0.75 [0.64, 0.85] | 0.42 [0.31, 0.53] |
| gpt-5.4-nano | real | 0.14 | 0.10 | 0.18 | 0.45 | 0.13 | 0.03 | 140 | 132 | 0.67 [0.59, 0.75] | 0.42 [0.37, 0.47] |
| gpt-5.4-nano | type_of | 0.39 | 0.18 | 0.15 | 0.24 | 0.05 | 0.03 | 138 | 135 | 0.64 [0.56, 0.72] | 0.27 [0.22, 0.33] |
| gpt-5.4-nano | imaginary | 0.78 | 0.04 | 0.12 | 0.05 | 0.01 | 0.01 | 265 | 265 | 0.03 [0.02, 0.05] | 0.26 [0.22, 0.30] |
| gpt-6-sol | neutral | 0.04 | 0.00 | 0.13 | 0.79 | 0.03 | 0.04 | 23 | 20 | 0.30 [0.17, 0.43] | 0.14 [0.06, 0.23] |
| gpt-6-sol | real | 0.00 | 0.00 | 0.04 | 0.96 | 0.01 | 0.02 | 30 | 30 | 0.83 [0.78, 0.89] | 0.03 [0.02, 0.05] |
| gpt-6-sol | type_of | 0.04 | 0.00 | 0.41 | 0.54 | 0.01 | 0.03 | 32 | 30 | 0.28 [0.24, 0.33] | 0.16 [0.10, 0.22] |
| gpt-6-sol | imaginary | 0.31 | 0.00 | 0.69 | 0.00 | 0.00 | 0.07 | 53 | 53 | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |
| gpt-6-luna | neutral | 0.17 | 0.01 | 0.07 | 0.71 | 0.04 | 0.05 | 36 | 34 | 0.57 [0.44, 0.71] | 0.17 [0.09, 0.27] |
| gpt-6-luna | real | 0.19 | 0.00 | 0.14 | 0.66 | 0.01 | 0.02 | 46 | 42 | 0.67 [0.59, 0.76] | 0.42 [0.34, 0.50] |
| gpt-6-luna | type_of | 0.09 | 0.01 | 0.09 | 0.80 | 0.01 | 0.03 | 45 | 42 | 0.66 [0.55, 0.76] | 0.46 [0.37, 0.55] |
| gpt-6-luna | imaginary | 0.26 | 0.00 | 0.74 | 0.00 | 0.00 | 0.04 | 86 | 90 | 0.00 [0.00, 0.01] | 0.00 [0.00, 0.00] |

The known-batch version of this table is in `descriptives.json`.

## 4. Reality-assertion wording in unmarked descriptions under real framings

| Batch | Model | Real-framed trials | Unmarked descriptions | With reality wording |
| --- | --- | --- | --- | --- |
| fresh | claude-sonnet-4-6 | 360 | 1 | 0 |
| fresh | claude-haiku-4-5 | 360 | 34 | 1 |
| fresh | claude-sonnet-5-5 | 360 | 0 | 0 |
| fresh | claude-haiku-5-5 | 360 | 0 | 0 |
| fresh | gpt-5.4-mini | 360 | 24 | 12 |
| fresh | gpt-5.4-nano | 360 | 92 | 64 |
| fresh | gpt-6-sol | 360 | 15 | 0 |
| fresh | gpt-6-luna | 360 | 52 | 12 |
| known | claude-sonnet-4-6 | 240 | 0 | 0 |
| known | claude-haiku-4-5 | 240 | 16 | 2 |
| known | claude-sonnet-5-5 | 240 | 0 | 0 |
| known | claude-haiku-5-5 | 240 | 0 | 0 |
| known | gpt-5.4-mini | 240 | 5 | 4 |
| known | gpt-5.4-nano | 240 | 30 | 19 |
| known | gpt-6-sol | 240 | 0 | 0 |
| known | gpt-6-luna | 240 | 31 | 8 |

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

The preregistration said any hit would be direct evidence of exposure. That was wrong about "bestiary", which is an ordinary word for a book of creatures. 59 of the 92 hits are on fresh words, which were unpublished and cannot reflect exposure to the original study. No response contains "chesterton". Every hit is listed with its surrounding text in `descriptives.json`. On my reading of all of them, after the fact, each uses the word generically (for example, an offer to write "a fantasy bestiary entry") and none refers to the original study. These hits are not evidence of exposure.

## 6. Historical models: known batch against the original study

Same eight words, same scorer, ten responses per word and condition in each run. The original runs used lower output caps (400 Anthropic, 700 OpenAI) and earlier dates. This is a stability check, not a controlled comparison. Change is known batch minus original, with an interval over the eight words.

| Model | Framing | U: original → now (change) | N: original → now (change) | E: original → now (change) |
| --- | --- | --- | --- | --- |
| claude-sonnet-4-6 | neutral | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 1.00 → 0.99 (-0.01 [-0.04, +0.00]) | 0.00 → 0.01 (+0.01 [+0.00, +0.04]) |
| claude-sonnet-4-6 | real | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.96 → 0.97 (+0.01 [-0.01, +0.04]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) |
| claude-sonnet-4-6 | type_of | 0.00 → 0.05 (+0.05 [+0.01, +0.09]) | 1.00 → 0.95 (-0.05 [-0.11, -0.01]) | 0.00 → 0.05 (+0.05 [+0.01, +0.11]) |
| claude-sonnet-4-6 | imaginary | 0.42 → 0.39 (-0.03 [-0.08, +0.03]) | 0.12 → 0.13 (+0.01 [-0.02, +0.06]) | 0.87 → 0.87 (+0.00 [-0.05, +0.04]) |
| claude-haiku-4-5 | neutral | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.97 → 1.00 (+0.03 [+0.00, +0.07]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) |
| claude-haiku-4-5 | real | 0.07 → 0.07 (+0.00 [-0.01, +0.01]) | 0.76 → 0.81 (+0.05 [+0.03, +0.07]) | 0.12 → 0.09 (-0.03 [-0.08, +0.01]) |
| claude-haiku-4-5 | type_of | 0.10 → 0.13 (+0.03 [-0.00, +0.07]) | 0.82 → 0.82 (+0.00 [-0.04, +0.05]) | 0.18 → 0.17 (-0.00 [-0.05, +0.04]) |
| claude-haiku-4-5 | imaginary | 0.70 → 0.72 (+0.02 [-0.06, +0.08]) | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 1.00 → 1.00 (+0.00 [+0.00, +0.00]) |
| gpt-5.4-mini | neutral | 0.01 → 0.03 (+0.01 [+0.00, +0.04]) | 0.34 → 0.33 (-0.01 [-0.11, +0.10]) | 0.62 → 0.66 (+0.04 [-0.09, +0.15]) |
| gpt-5.4-mini | real | 0.01 → 0.02 (+0.01 [-0.01, +0.04]) | 0.63 → 0.69 (+0.06 [-0.10, +0.19]) | 0.23 → 0.19 (-0.04 [-0.12, +0.05]) |
| gpt-5.4-mini | type_of | 0.07 → 0.07 (-0.00 [-0.05, +0.04]) | 0.03 → 0.07 (+0.03 [+0.00, +0.10]) | 0.87 → 0.86 (-0.01 [-0.05, +0.04]) |
| gpt-5.4-mini | imaginary | 0.00 → 0.00 (+0.00 [+0.00, +0.00]) | 0.00 → 0.01 (+0.00 [+0.00, +0.01]) | 0.93 → 0.91 (-0.02 [-0.07, +0.03]) |
| gpt-5.4-nano | neutral | 0.14 → 0.10 (-0.04 [-0.17, +0.11]) | 0.39 → 0.45 (+0.06 [-0.12, +0.26]) | 0.46 → 0.39 (-0.07 [-0.26, +0.10]) |
| gpt-5.4-nano | real | 0.13 → 0.12 (-0.00 [-0.06, +0.06]) | 0.47 → 0.45 (-0.02 [-0.09, +0.05]) | 0.47 → 0.49 (+0.03 [-0.05, +0.10]) |
| gpt-5.4-nano | type_of | 0.09 → 0.05 (-0.04 [-0.09, +0.00]) | 0.25 → 0.24 (-0.02 [-0.06, +0.04]) | 0.65 → 0.67 (+0.03 [-0.04, +0.09]) |
| gpt-5.4-nano | imaginary | 0.09 → 0.09 (+0.00 [-0.05, +0.05]) | 0.00 → 0.00 (+0.00 [-0.01, +0.01]) | 0.97 → 0.97 (-0.00 [-0.05, +0.03]) |
