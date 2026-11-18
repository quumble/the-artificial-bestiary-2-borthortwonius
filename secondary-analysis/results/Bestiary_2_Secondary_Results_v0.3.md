For Bo Chesterton and Claude Fable \| Approved plan v0.3

**B and A completed. Coding audit selected, not yet coded. C deferred.**

## What was done

The two released archives were verified, their frozen source inventory was checked, and all 16,000 study records were linked to the original schedule and score rows with composite keys. A separate estimator reproduced all 14 original point estimates. The largest absolute difference was 1.11 × 10⁻¹⁶ on the proportion scale.

The audit sample was then locked and committed before any new B result was inspected: 12 development responses, 64 state-stratified audit responses and four separate targeted responses. B ran first, then A. No additional study requests, model judges or embedding-model calls were used.

## The main contribution

B distinguishes changes in whether a description is produced from changes in matched qualification cues. Those are different patterns, and a single four-state “inconsistency” score would conflate them.

A supplies separate estimates of repetition-related generation noise and word-bank resampling uncertainty. It does not identify an optimal sample size or establish that any original trials were unnecessary.

## Reading boundary

Every new result is exploratory and based on deliberately selected words and endpoints. The frozen scores measure surface features, not factual accuracy, private beliefs, deception or welfare. The original releases, scorers and inferential analyzers remain unchanged.

Plan commit: 275678f740b3d07d562f8a87a7d3d3aa37fbaf3e  
Audit lock: 004e7b82cbdd29819a5e699d082d46a3b8f53a50

Complete numerical results are supplied as CSV and JSON in the accompanying implementation package. This report is a reader guide, not an amendment to the governing plan.

# 1. Consistency is not one thing

## Description disagreement versus cue disagreement

Under fresh imaginary prompts, five endpoints produced a scored description on every observed response. Their binary description disagreement was zero, but their four-state disagreement was not. All of that four-state disagreement came from U versus Marked E: whether the scorer matched a qualification cue.

| Endpoint     | D_E % | Four-state % | U–Marked % | E–Other % |
|--------------|-------|--------------|------------|-----------|
| Haiku 4.5    | 0.00  | 34.72        | 34.72      | 0.00      |
| Haiku 5.5    | 0.00  | 30.00        | 30.00      | 0.00      |
| Sonnet 4.6   | 7.78  | 24.31        | 16.53      | 1.11      |
| Sonnet 5.5   | 0.00  | 35.83        | 35.83      | 0.00      |
| GPT-5.4 mini | 10.83 | 10.83        | 0.00       | 10.83     |
| GPT-5.4 nano | 2.50  | 16.81        | 14.17      | 2.08      |
| GPT-6 Luna   | 0.00  | 15.83        | 15.83      | 0.00      |
| GPT-6 Sol    | 0.00  | 12.78        | 12.78      | 0.00      |

The table shows unconditional pair fractions. Omitted E–N and N–Other components remain in the full B2 file. Imaginary prompts license invention; absence of a response-local cue is not itself an error.

## Pooled rates can conceal different patterns

GPT-6 Sol under fresh “type of” prompts had a 45.00% description rate, but only 13.61% within-prompt description disagreement (95% word-bootstrap interval 9.17–18.33%). Of 72 word/category cells, 51 had unanimous observed description labels and 21 were mixed. This is a property of the observed bank, not proof of deterministic behavior.

For GPT-5.4 mini under fresh imaginary prompts, its 10.83% description disagreement was entirely E versus Other, not E versus nonrecognition. “Other” is a scorer residual. The distinction motivates a coding-boundary audit rather than a claim that the model changed its belief about fiction.

## Rho remains a diagnostic

Across the two banks, rho is undefined in 14 endpoint/framing rows and exceeds one in six. These values are retained. Rho is not a percentage of variability explained, and a unanimous observed cell does not rule out rare exceptions.

Source: outputs/B/B1_summary.json and B2_decomposition.json.

# 2. B1: fresh words

E = description-form rate. D_E = describe/no-description pair disagreement. D_EN = description/nonrecognition pair fraction. Intervals are unadjusted 95% whole-word bootstrap intervals. Rho is unitless.

| Endpoint     | Frame     | E %    | D_E % | D_E interval | D_EN % | rho   |
|--------------|-----------|--------|-------|--------------|--------|-------|
| Haiku 4.5    | Neutral   | 0.83   | 1.67  | 0.00–5.00    | 1.67   | 1.008 |
| Haiku 4.5    | Real      | 14.44  | 15.83 | 10.28–21.39  | 13.61  | 0.641 |
| Haiku 4.5    | Type of   | 27.50  | 7.78  | 4.44–11.39   | 7.78   | 0.195 |
| Haiku 4.5    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Haiku 5.5    | Neutral   | 5.00   | 8.33  | 1.67–15.83   | 8.33   | 0.877 |
| Haiku 5.5    | Real      | 6.94   | 13.06 | 9.44–16.39   | 13.06  | 1.010 |
| Haiku 5.5    | Type of   | 13.06  | 22.22 | 17.50–26.67  | 22.08  | 0.979 |
| Haiku 5.5    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Sonnet 4.6   | Neutral   | 0.00   | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Sonnet 4.6   | Real      | 0.83   | 1.67  | 0.00–3.33    | 1.53   | 1.008 |
| Sonnet 4.6   | Type of   | 10.28  | 6.94  | 2.78–11.39   | 6.94   | 0.377 |
| Sonnet 4.6   | Imaginary | 91.39  | 7.78  | 4.17–11.67   | 6.67   | 0.494 |
| Sonnet 5.5   | Neutral   | 7.50   | 6.67  | 1.67–13.33   | 6.67   | 0.480 |
| Sonnet 5.5   | Real      | 12.22  | 19.72 | 14.17–24.72  | 19.17  | 0.919 |
| Sonnet 5.5   | Type of   | 18.89  | 27.78 | 21.67–33.89  | 27.36  | 0.907 |
| Sonnet 5.5   | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| GPT-5.4 mini | Neutral   | 62.50  | 31.67 | 22.50–40.83  | 31.67  | 0.676 |
| GPT-5.4 mini | Real      | 35.56  | 35.00 | 28.61–41.11  | 30.14  | 0.764 |
| GPT-5.4 mini | Type of   | 94.72  | 8.33  | 5.28–11.40   | 1.94   | 0.833 |
| GPT-5.4 mini | Imaginary | 93.89  | 10.83 | 6.94–14.72   | 0.00   | 0.944 |
| GPT-5.4 nano | Neutral   | 40.00  | 36.67 | 26.67–46.67  | 24.58  | 0.764 |
| GPT-5.4 nano | Real      | 62.50  | 37.50 | 31.67–42.78  | 27.22  | 0.800 |
| GPT-5.4 nano | Type of   | 78.33  | 24.44 | 16.11–33.33  | 15.83  | 0.720 |
| GPT-5.4 nano | Imaginary | 98.61  | 2.50  | 0.00–5.56    | 0.42   | 0.913 |
| GPT-6 Luna   | Neutral   | 25.83  | 25.83 | 16.67–35.00  | 22.92  | 0.674 |
| GPT-6 Luna   | Real      | 33.61  | 31.11 | 23.89–38.33  | 30.56  | 0.697 |
| GPT-6 Luna   | Type of   | 19.72  | 12.50 | 7.78–17.23   | 11.81  | 0.395 |
| GPT-6 Luna   | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| GPT-6 Sol    | Neutral   | 17.50  | 17.50 | 9.17–26.67   | 15.00  | 0.606 |
| GPT-6 Sol    | Real      | 4.17   | 5.56  | 2.50–8.89    | 5.28   | 0.696 |
| GPT-6 Sol    | Type of   | 45.00  | 13.61 | 9.17–18.33   | 11.81  | 0.275 |
| GPT-6 Sol    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |

All eight endpoints and four framings are shown. NA means not estimable, not zero. Endpoint settings differ, so these are not rankings of truthfulness, safety or intrinsic stochasticity. The full tables include rho intervals, support flags, wording measures and source-specific diagnostics.

Source: outputs/B/B1_summary.csv. Fresh: 24 words, five repetitions per cell. Previously published: eight words, ten repetitions per cell.

# 2. B1: previously published words

E = description-form rate. D_E = describe/no-description pair disagreement. D_EN = description/nonrecognition pair fraction. Intervals are unadjusted 95% whole-word bootstrap intervals. Rho is unitless.

| Endpoint     | Frame     | E %    | D_E % | D_E interval | D_EN % | rho   |
|--------------|-----------|--------|-------|--------------|--------|-------|
| Haiku 4.5    | Neutral   | 0.00   | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Haiku 4.5    | Real      | 9.17   | 10.19 | 5.00–15.93   | 9.54   | 0.612 |
| Haiku 4.5    | Type of   | 17.50  | 10.19 | 6.02–14.44   | 10.19  | 0.353 |
| Haiku 4.5    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Haiku 5.5    | Neutral   | 2.50   | 5.00  | 0.00–10.00   | 5.00   | 1.026 |
| Haiku 5.5    | Real      | 11.25  | 18.61 | 14.44–23.61  | 18.61  | 0.932 |
| Haiku 5.5    | Type of   | 12.50  | 19.81 | 16.30–22.96  | 19.81  | 0.906 |
| Haiku 5.5    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Sonnet 4.6   | Neutral   | 1.25   | 2.50  | 0.00–7.50    | 2.50   | 1.013 |
| Sonnet 4.6   | Real      | 0.00   | 0.00  | 0.00–0.00    | 0.00   | NA    |
| Sonnet 4.6   | Type of   | 5.42   | 6.39  | 1.94–12.50   | 6.39   | 0.624 |
| Sonnet 4.6   | Imaginary | 87.08  | 8.43  | 2.96–13.89   | 8.43   | 0.375 |
| Sonnet 5.5   | Neutral   | 2.50   | 5.00  | 0.00–10.00   | 5.00   | 1.026 |
| Sonnet 5.5   | Real      | 9.58   | 16.94 | 11.11–22.78  | 16.94  | 0.978 |
| Sonnet 5.5   | Type of   | 25.42  | 31.39 | 26.76–36.67  | 31.20  | 0.828 |
| Sonnet 5.5   | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| GPT-5.4 mini | Neutral   | 66.25  | 26.94 | 15.83–40.28  | 25.28  | 0.603 |
| GPT-5.4 mini | Real      | 19.17  | 24.07 | 19.72–28.52  | 19.54  | 0.777 |
| GPT-5.4 mini | Type of   | 85.83  | 14.63 | 7.13–22.59   | 5.46   | 0.602 |
| GPT-5.4 mini | Imaginary | 91.25  | 14.35 | 10.00–18.43  | 1.39   | 0.899 |
| GPT-5.4 nano | Neutral   | 38.75  | 33.06 | 18.61–47.22  | 23.89  | 0.696 |
| GPT-5.4 nano | Real      | 49.17  | 40.00 | 31.94–46.94  | 35.46  | 0.800 |
| GPT-5.4 nano | Type of   | 67.08  | 20.09 | 10.56–29.26  | 13.24  | 0.455 |
| GPT-5.4 nano | Imaginary | 96.67  | 5.56  | 1.67–10.83   | 0.83   | 0.862 |
| GPT-6 Luna   | Neutral   | 13.75  | 10.28 | 0.00–20.56   | 10.28  | 0.433 |
| GPT-6 Luna   | Real      | 27.92  | 23.98 | 15.37–33.15  | 23.98  | 0.596 |
| GPT-6 Luna   | Type of   | 12.92  | 10.28 | 3.61–18.06   | 8.33   | 0.457 |
| GPT-6 Luna   | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |
| GPT-6 Sol    | Neutral   | 2.50   | 4.44  | 0.00–13.33   | 3.33   | 0.912 |
| GPT-6 Sol    | Real      | 0.00   | 0.00  | 0.00–0.00    | 0.00   | NA    |
| GPT-6 Sol    | Type of   | 27.08  | 3.61  | 0.83–7.50    | 2.96   | 0.091 |
| GPT-6 Sol    | Imaginary | 100.00 | 0.00  | 0.00–0.00    | 0.00   | NA    |

All eight endpoints and four framings are shown. NA means not estimable, not zero. Endpoint settings differ, so these are not rankings of truthfulness, safety or intrinsic stochasticity. The full tables include rho intervals, support flags, wording measures and source-specific diagnostics.

Source: outputs/B/B1_summary.csv. Fresh: 24 words, five repetitions per cell. Previously published: eight words, ten repetitions per cell.

# 3. A1: separate uncertainty scales

All values below are percentage points except the last column. The word-bootstrap standard error and generation-noise standard deviation are separate calculations, not a proven decomposition. “Depth 1” means one fresh response per cell, plus two published responses for H4.

<table>
<colgroup>
<col style="width: 27%" />
<col style="width: 11%" />
<col style="width: 12%" />
<col style="width: 14%" />
<col style="width: 15%" />
<col style="width: 16%" />
</colgroup>
<thead>
<tr class="header">
<th>Estimand</th>
<th>Effect</th>
<th>Word SE</th>
<th>Gen SD: 1</th>
<th>Gen SD: full</th>
<th>Unanimous<br />
weight %</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>M01_imaginary-real</td>
<td>+16.39</td>
<td>2.48</td>
<td>1.96</td>
<td>0.88</td>
<td>55.9</td>
</tr>
<tr class="even">
<td>M01_type_of-real</td>
<td>+32.47</td>
<td>1.74</td>
<td>1.98</td>
<td>0.89</td>
<td>55.0</td>
</tr>
<tr class="odd">
<td>M02_imaginary-real</td>
<td>-26.11</td>
<td>1.34</td>
<td>2.08</td>
<td>0.93</td>
<td>49.8</td>
</tr>
<tr class="even">
<td>M02_type_of-real</td>
<td>+0.45</td>
<td>0.98</td>
<td>1.70</td>
<td>0.76</td>
<td>66.6</td>
</tr>
<tr class="odd">
<td>M03_imaginary-real</td>
<td>-56.25</td>
<td>1.24</td>
<td>1.57</td>
<td>0.70</td>
<td>70.7</td>
</tr>
<tr class="even">
<td>M03_type_of-real</td>
<td>-5.83</td>
<td>1.59</td>
<td>2.00</td>
<td>0.90</td>
<td>52.7</td>
</tr>
<tr class="odd">
<td>M09_imaginary-real</td>
<td>+74.20</td>
<td>1.56</td>
<td>1.44</td>
<td>0.64</td>
<td>75.6</td>
</tr>
<tr class="even">
<td>M09_type_of-real</td>
<td>+13.78</td>
<td>2.20</td>
<td>1.75</td>
<td>0.78</td>
<td>63.6</td>
</tr>
<tr class="odd">
<td>H1</td>
<td>+76.70</td>
<td>1.27</td>
<td>1.40</td>
<td>0.63</td>
<td>76.3</td>
</tr>
<tr class="even">
<td>H2</td>
<td>-24.38</td>
<td>2.77</td>
<td>2.60</td>
<td>1.16</td>
<td>60.6</td>
</tr>
<tr class="odd">
<td>H3</td>
<td>-1.56</td>
<td>1.77</td>
<td>1.45</td>
<td>0.65</td>
<td>78.1</td>
</tr>
<tr class="even">
<td>H4</td>
<td>-2.66</td>
<td>2.94</td>
<td>2.61</td>
<td>1.17</td>
<td>58.6</td>
</tr>
<tr class="odd">
<td>H5</td>
<td>-3.47</td>
<td>1.23</td>
<td>1.35</td>
<td>0.60</td>
<td>78.2</td>
</tr>
<tr class="even">
<td>H6</td>
<td>+9.38</td>
<td>2.60</td>
<td>4.10</td>
<td>1.84</td>
<td>60.9</td>
</tr>
</tbody>
</table>

## What these numbers support

At collected depth, estimated generation-noise SD ranges from 0.60 to 1.84 points. The separate word-bootstrap SE ranges from 0.98 to 2.94 points. This supplies a scale for repetition sensitivity without claiming what fraction of a confidence interval repetitions could remove.

## What is built into the calculation

The 1/√r decrease is imposed by the formula. It is not an empirically discovered learning curve. Observed unanimous cells contribute zero plug-in generation variance. Their absolute coefficient-weight share is shown because five or ten identical labels do not establish zero underlying uncertainty.

The nested-subset deviation also becomes zero when all observations are retained, because the subset is then the full reference. That endpoint is not independent replication or evidence of adequate sample size.

Source: outputs/A/A1_summary.csv and A1_depth_grid.csv. H1–H6 retain their original directions and weights. No new p-values were computed.

# 4. A2: breadth versus repetition depth

Each allocation below costs 1,920 fresh-bank study calls across all eight endpoints and ten conditions. Entries are word-subset SD / estimated generation SD, in percentage points. H4 is excluded because it combines banks.

| Estimand           | 24 words × 1 | 12 words × 2 | 6 words × 4 |
|--------------------|--------------|--------------|-------------|
| M01_imaginary-real | 0.00 / 1.96  | 2.60 / 1.96  | 4.89 / 1.96 |
| M01_type_of-real   | 0.00 / 1.98  | 1.90 / 1.98  | 3.40 / 1.98 |
| M02_imaginary-real | 0.00 / 2.08  | 1.47 / 2.08  | 2.38 / 2.08 |
| M02_type_of-real   | 0.00 / 1.70  | 1.06 / 1.70  | 1.86 / 1.70 |
| M03_imaginary-real | 0.00 / 1.57  | 1.36 / 1.57  | 2.29 / 1.57 |
| M03_type_of-real   | 0.00 / 2.00  | 1.70 / 2.00  | 3.03 / 2.00 |
| M09_imaginary-real | 0.00 / 1.44  | 1.65 / 1.44  | 2.83 / 1.44 |
| M09_type_of-real   | 0.00 / 1.75  | 2.35 / 1.75  | 4.25 / 1.75 |
| H1                 | 0.00 / 1.40  | 1.32 / 1.40  | 2.39 / 1.40 |
| H2                 | 0.00 / 2.60  | 2.91 / 2.60  | 5.41 / 2.60 |
| H3                 | 0.00 / 1.45  | 1.92 / 1.44  | 3.45 / 1.46 |
| H5                 | 0.00 / 1.35  | 1.29 / 1.34  | 2.27 / 1.35 |
| H6                 | 0.00 / 4.10  | 2.91 / 4.10  | 4.93 / 4.10 |

## Interpretation

Reducing the number of sampled words introduces variation across subsets of the collected bank. At all 24 words, that particular source of subset variation is mechanically zero. It does not mean uncertainty about other possible words has disappeared.

Generation-noise scales are similar at these equal call budgets. Much of that behavior follows from the estimator’s weights and the inverse-repetition formula. The table is a retrospective allocation diagnostic, not an experimentally established optimum.

The full output retains all four word counts, all five repetition depths and all 13 fresh-bank estimands: 260 rows. Nothing is selected for reporting because it produces a more favorable conclusion.

Eight original preflight calls are separate fixed overhead. No token or dollar savings are reconstructed.

Source: outputs/A/A2_word_depth_grid.csv. Word subsets: 1,000 per q. This analysis cannot estimate the value of genuinely uncollected words.

# 5. Temporal and numerical checks

Request-start timestamps were available. Fresh cells compare the earliest two and latest two observations, omitting the middle one. Published cells compare five versus five. These are descriptive comparisons, not a calibrated drift test.

| Estimand           | Early − late, pp | Noise SD, pp |
|--------------------|------------------|--------------|
| M01_imaginary-real | -1.042           | 1.958        |
| M01_type_of-real   | +2.517           | 1.981        |
| M02_imaginary-real | +2.170           | 2.078        |
| M02_type_of-real   | +1.649           | 1.696        |
| M03_imaginary-real | -0.434           | 1.574        |
| M03_type_of-real   | +3.299           | 2.001        |
| M09_imaginary-real | -0.868           | 1.442        |
| M09_type_of-real   | +0.087           | 1.753        |
| H1                 | -0.781           | 1.400        |
| H2                 | +3.299           | 2.601        |
| H3                 | -3.906           | 1.451        |
| H4                 | -3.136           | 2.466        |
| H5                 | +0.174           | 1.348        |
| H6                 | -3.795           | 4.104        |

H3 shows an early-minus-late difference of −3.91 points against a 1.45-point estimated noise scale. That pattern is disclosed, but this plan supplies neither a threshold nor a multiple-comparison procedure for diagnosing drift.

## Checks completed

Twenty synthetic/regression tests passed. All 14 original point estimates matched the released targets within 10⁻¹⁰. A separate direct enumeration of response pairs from the released Fable CSV reproduced E rate, D_E and D_EN in all 64 B1 rows; the largest absolute difference was 2.22 × 10⁻¹⁶.

The fixed 500-subset checks were retained without seed shopping. The largest absolute approximate Monte Carlo SD diagnostic was 2.456. Full-data nested deviation is zero analytically; simulated residual SD was at most 7.01 × 10⁻¹⁵ on the proportion scale.

**These are integrity and calculation checks, not independent semantic validation of the scorers.**

Sources: outputs/gate_14.csv, independent_verification.json, A1_temporal.csv, A1_depth_grid.csv and test_log.txt.

# 6. Audit handoff and provenance

## The next human step

Work through the 12-response development packet first. Use it to settle a short codebook. The 64 audit responses and four targeted responses were already selected, with no overlap, and must not be replaced after seeing the results. Codebook decisions should be locked before coding the held-aside audit.

Judge the exact prompt and response together. An imaginary prompt already licenses invention: declarative creative prose is not automatically an unsupported factual claim just because the answer does not repeat “imaginary.” Separately note whether the response itself makes its interpretive or hypothetical status explicit.

The targeted four-response set is a separate diagnostic, not part of a pooled accuracy estimate. The audit is investigator-led and partially masked. It does not establish inter-rater reliability, an independent gold standard or an error rate for the full corpus.

## Execution record

| Stage                     | UTC completion      |
|---------------------------|---------------------|
| Input gate and audit lock | 2026-11-14 21:22:54 |
| B: response consistency   | 2026-11-14 21:23:22 |
| A: information efficiency | 2026-11-14 21:23:50 |

The same analysis-code hash appears in every phase receipt. Execution used Python 3.13.5 and NumPy 2.3.5 on Linux, separately from the original frozen Windows analysis. The original runtime checks were not weakened.

## Package contents

secondary.py and test_secondary.py; complete A/B CSV and JSON tables; cell-level counts and estimand coefficients; numerical-check results; audit commitment; phase receipts, seeds and checksums; descriptive figures; README and implementation log. Raw archives and the unblinding key are not bundled.

## What remains uncompleted

Human coding, codebook lock and any semantic scorer sensitivity remain pending. C has not been run. The paper and its original confirmatory results have not been rewritten to include these new findings.

Primary sources: checksum-identified raw and analysis releases dated November 11, 2026; v0.3 plan at commit 275678f; audit commitment at 004e7b8. Complete provenance is in the implementation package.
