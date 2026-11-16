# Declared exploratory results from the three frozen coding instruments

**November 15, 2026. Investigator: Bo Chesterton. Analysis implementation and report: GPT assistance.**

The principal framing patterns persist across the three instruments, while
their estimated sizes often change substantially. The known-versus-fresh
interaction changes sign across instruments. Marking-dependent findings are
especially sensitive to the definition used. These results support retaining
the broad framing account and reporting measurement sensitivity explicitly.

This is a post-publication exploratory supplement. It uses the existing
16,000 response codes and leaves the registered analyses and frozen scorers
unchanged. It does not repair or validate a new scorer version. The
[declaration](DECLARATION.md) and its separately committed
[pre-computation clarification](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/commit/a73a37f539f3dd99e84f256f7bdf8d2713838120)
specify the estimators. All 225 reporting rows, including component rates and
paired instrument differences, are in the [complete tables](results/tables.md)
and [machine-readable estimates](results/estimates.json).

## What was compared

| Arm | Instrument used here |
| --- | --- |
| A | GPT context heuristic 1.0.0 |
| B | Registered Fable v1.1 E, N and U outcomes exported by the mechanical arm |
| C | Zoned heuristic 1.0.0 |

E denotes detected description; N denotes nonrecognition without description;
U denotes each instrument's mapped unmarked-description outcome. These are
related operational definitions, not interchangeable semantic judgments.
In C, U includes hedged descriptions, while the separate bare-description
class does not. Imaginary prompts license invention, so an unmarked
description in that frame is not automatically an unsupported factual claim.

The bootstrap resamples whole words within the three fresh source strata and
two known intent strata, using 10,000 shared draws. Most new contrasts use the
24 fresh words; H4 also uses the eight previously published words. Endpoints
are fixed. Intervals are unadjusted 95% percentile intervals and exclude
uncertainty from detector error. The three arms analyze the same observations
and are not independent replications.

## Framing patterns persist, with different magnitudes

Differences below are percentage points. Brackets are the exploratory 95%
word-bootstrap intervals. H1 is exactly G1/E and is not counted twice.

| Contrast and outcome | A | B | C |
| --- | ---: | ---: | ---: |
| Imaginary minus real, E (G1/H1) | 58.16 [55.62, 60.66] | 76.70 [74.31, 79.20] | 80.87 [78.72, 83.12] |
| Imaginary minus real, N (G1) | -35.76 [-37.78, -33.92] | -72.05 [-75.03, -69.03] | -74.41 [-77.12, -71.77] |
| Imaginary minus real, U (G1) | 31.22 [28.48, 34.08] | 40.17 [37.33, 43.19] | 40.31 [37.33, 43.37] |
| Type-of minus real, E (G2) | 13.03 [9.46, 16.54] | 17.15 [13.06, 21.63] | 18.65 [14.83, 22.64] |
| Type-of minus real, N (G2) | -5.56 [-8.68, -2.67] | -13.44 [-18.09, -9.06] | -14.17 [-18.33, -10.24] |
| Type-of minus real, U (G2) | 4.94 [2.70, 7.17] | 5.49 [2.71, 8.30] | 7.67 [4.31, 11.18] |
| Type-of minus real, N, OpenAI endpoints (H2) | -14.10 [-17.71, -10.56] | -24.38 [-29.93, -19.03] | -24.86 [-30.49, -19.51] |
| Animal-intent minus no-intent, U (H3) | -0.79 [-3.29, 1.67] | -1.56 [-5.05, 1.88] | -1.85 [-5.76, 2.03] |
| Current-minus-historical N gap, known minus fresh (H4) | 4.64 [0.33, 9.00] | -2.66 [-8.44, 2.97] | -1.65 [-6.67, 2.95] |
| Current minus historical, U (H5) | -1.88 [-4.30, 0.56] | -3.47 [-5.83, -0.94] | -7.19 [-9.86, -4.37] |
| Anthropic-minus-OpenAI N gap, Claude-origin minus GPT-origin (H6) | 5.63 [-0.27, 11.43] | 9.38 [4.02, 14.46] | 7.68 [3.84, 11.70] |

The seven framing-related rows have intervals on the same side of zero in
all three arms. This is a descriptive common-direction result, not seven
new confirmatory successes. Their magnitudes can still differ: the
imaginary-minus-real E contrast is 22.71 points larger under C than A, with
the paired C-minus-A interval [20.62, 24.79].

H3 remains uncertain in every arm and supplies no support for the predicted
positive animal-intent difference. H4 is the clearest sign-changing example:
A is positive, B and C are negative, and the paired A-minus-C difference is
6.29 points [1.67, 10.76]. This warrants a measurement-sensitivity statement;
it does not establish exposure to the previously published words.

H5 is negative in all three arms, but the common-direction rule is not met
because A's interval includes zero. C is more negative than B by 3.72 points
[2.78, 4.76]. H6 is positive in all arms, but A's interval includes zero and
none of the paired instrument-difference intervals excludes zero. Uncertainty
in A does not by itself establish instrument dependence in H6. These
exploratory intervals do not revise the original Holm-adjusted test decisions.

## New questions about response behavior

The following summaries cover all eight declared question families. Full
endpoint and component tables remain available, including uncertain contrasts.

### Primary descriptive tier

**Q1, how endpoints decline.** Among declines on neutral, real and type-of
prompts, the possibility-list share is 49.42 points higher for the selected
Anthropic endpoints than the selected OpenAI endpoints [46.61, 52.26]. There
is substantial endpoint variation: GPT-6 Sol is at 10.48%, GPT-6 Luna at
80.94%, and the two current Claude endpoints exceed 99%. The pooled
current-minus-historical difference is -2.55 points [-5.11, 0.35]. These are
properties of the selected endpoints and the frozen response-type detector.

**Q2, disclaim and describe.** The current-minus-historical difference on real
and type-of prompts is -7.33 points [-9.27, -5.24]. The pooled type-of-minus-real
difference is 1.56 points [0.00, 3.12], with opposing endpoint patterns. The
endpoint table is necessary to interpret that small pooled difference.

**Q4, claimed grounding.** Among detected descriptions, grounding claims are
30.68 points more prevalent under real than type-of prompts [25.31, 35.58].
The component rates are 34.75% and 4.07%. These condition on different subsets
of responses that produced descriptions. The provider gap is uncertain at
2.70 points [-4.92, 10.02]. Detected grounding language is not verified
provenance or proof of an unsupported factual assertion.

**Q6, category.** Idea prompts produce more description detections than animal
prompts on real and type-of framings: +9.74 points [6.61, 12.92] under B and
+15.26 [12.14, 18.49] under C. Both provider groups have positive idea-minus-animal
intervals under both instruments. The pooled object-minus-animal estimates
are -1.72 [-3.91, 0.47] under B and 0.05 [-2.34, 2.45] under C.

**Q7, repetition consistency.** Under C, fresh-bank binary description-call
agreement ranges from 77.17% to 99.83% across endpoints. Agreement on the full
response type ranges from 41.00% to 84.00%. The finer response-type distinction
can vary even when describe/not-describe is stable. These are within-cell
repetition-pair agreements, not scorer accuracy or inter-rater agreement.
The complete tables include all three arms' binary agreement and separate
fresh and known banks.

### Secondary marking-dependent tier

**Q3, how bare descriptions are.** Among C's detected descriptions on real and
type-of prompts, 29.47% are bare, 16.44% hedged, 26.39% framed, and 27.70%
disclaimed. The conditional bare share is 22.91 points higher for current
than historical endpoints [15.84, 30.53]. This coexists with lower unconditional
U in H5: the denominators differ, and U also includes hedged descriptions.
It is not evidence that current endpoints make more bare claims overall.

**Q5, prompt-word echo.** Discounting the prompt's literal word "imaginary"
as the sole framing mark changes endpoint U rates by 9.44 to 63.61 points.
For GPT-5.4 nano the rate moves from 15.00% to 78.61%, a change of 63.61 points
[57.78, 69.17]. This is a sensitivity to the scoring convention. It does not
demonstrate that the endpoint failed to recognize the imaginary instruction.

**Q8, late marking.** Among descriptions with a positioned mark, late-only
marking is more frequent for the selected Anthropic endpoints: the provider
gap is 20.57 points [16.14, 25.20] under imaginary prompts and 28.11
[17.59, 39.00] under non-imaginary prompts. This uses the frozen positional
measure's fiction, construction, interpretation and nonrecognition cues.
Attribute hedges and implicit hypothetical framing are outside that measure.

## Missing values and the sparse grounding estimate

A has 11 unresolved E values, five unresolved N values, and 1,531 unresolved
U values across the 16,000 responses. The declared analysis omits unresolved
repetitions and empty cells, records that support, and keeps fixed source
weights. For example, A's fresh imaginary U component omits 564 unresolved
responses and nine empty cells. Its rates are available-case estimates;
paired instrument differences involving A reflect that support as well as
differences in coding. Every component's counts are retained in the JSON.

**Haiku 5.5's conditional grounding estimate has only one qualifying
description among 720 fresh real/type-of responses.** No grounding claim was
detected in that description. In 3,399 of 10,000 bootstrap draws, the
description denominator is zero. The reported [0, 0] interval uses only the
6,601 defined draws and is explicitly flagged as conditional. It supplies no
confident evidence of absence. Every other reported interval has all 10,000
draws defined. More generally, resampling an all-zero observed count cannot
establish a zero population rate.

## Verification and next use

The comparison reconstruction matches all 477 fields of the historical
three-way output and all 73 fields of the human-pass score output exactly.
It also independently reproduces the human-versus-model reader agreement
and the 26/34 marking agreement. The repository test suite passes all
107 tests, including 38 added tests for this workflow. A separate direct
implementation checks nine selected point estimates and both interval
endpoints to within 2e-14, covering framing, H4, H6, a conditional provider
gap, and repetition consistency. A second run from another working directory
reproduced the estimates, specifications, interpretation summaries, complete
tables, and historical-comparison receipt byte for byte. The
[workflow instructions](README.md) include all three verification and
analysis commands.

The next measurement step is a separately versioned, bounded repair of the
zoned scorer, followed by a fresh held-out audit and the same declared
analysis list. Preserve these frozen-version results as the comparison
baseline. The secondary-analysis branch and manuscript revision remain
separate work; neither was changed by this implementation.
