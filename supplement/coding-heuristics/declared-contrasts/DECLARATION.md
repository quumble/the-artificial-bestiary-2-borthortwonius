# Declared exploratory contrasts for the coding heuristics

Declared 15 November 2026, before any of the estimates below were computed
with intervals. Investigator: Bo Chesterton. Written by Claude Fable 5.2.

**Status.** Post hoc and exploratory. Nothing here is preregistered, and nothing
here replaces a registered result. No p-values and no multiplicity claims will
be reported: point estimates and 95% bootstrap intervals only. The intended use
is to decide which findings are worth carrying into a possible superseding
paper, where the same list would be rerun unchanged on a repaired instrument.

## What had already been seen when this was written

This list was not written blind. Before writing it, the author had seen, as
point estimates without intervals:

- Fresh-bank rates by framing for description, nonrecognition without
  description and unmarked description under all three instruments.
- The H1, H2, H3 and H5 shapes as plain rate differences under the context and
  mechanical arms (not under the zoned arm, and not with registered weights).
- Anthropic minus OpenAI on description and nonrecognition without description
  under all three, and endpoint-level rates on fresh real and type-of prompts.
- Zoned response-type shares by framing overall, and by endpoint on fresh real
  and type-of prompts (so item 1 below is partly seen).
- Overall counts for prompt echo (1,293 of 4,800), late marking (407 of 7,293)
  and grounding among real and type-of descriptions (292 of 2,324).

Not seen in any form: H4 and H6 shapes; anything by category; anything by
generation under the zoned arm; grounding, late marking or prompt echo by
endpoint; repetition consistency for the zoned arm.

## Instruments and data

- A: context heuristic 1.0.0. B: registered Fable v1.1 outcomes as exported by
  the mechanical arm. C: zoned heuristic 1.0.0. All frozen; all 16,000 responses.
- Known defects of C 1.0.0 stand, including the two found by the human pass.
- A returns null on some fields. A null is dropped from the cell it falls in;
  a cell with no resolved value is dropped and counted.

## Estimator

- Unit of analysis is the word. For each word and endpoint, average over the
  repetitions within a condition, then over the conditions named in the
  contrast with equal weight. Average endpoints in a group with equal weight.
- Within-word contrasts (framing, generation, provider, category) are the mean
  over words of the within-word difference, with the three fresh sources
  weighted equally. Known words are reported separately, their two intent
  strata weighted equally.
- Between-word contrasts (word source, bank) are differences of stratum means.
- Conditional rates are ratios of the weighted numerator rate to the weighted
  denominator rate. A zero denominator is reported as not estimable, never as
  zero, and bootstrap draws with a zero denominator are counted and reported.
- Intervals: 10,000 bootstrap draws resampling words within source stratum,
  seed 20261115, 95% percentile. The same draws are used for all three
  instruments, so differences between instruments carry their own interval.
- Endpoint groups as registered: historical = claude-sonnet-4-6,
  claude-haiku-4-5, gpt-5.4-mini, gpt-5.4-nano; current = claude-sonnet-5-5,
  claude-haiku-5-5, gpt-6-sol, gpt-6-luna.
- With 24 fresh and 8 known words the intervals will be wide. That width is
  the finding's real precision.

## Block 1: do the registered shapes survive the instrument?

Outcomes: E description, N nonrecognition without description, U unmarked
description, each under A, B and C. These are re-estimates in the registered
shapes using the estimator above. They are not the registered tests.

| Shape | Contrast |
|---|---|
| G1 | imaginary minus real, fresh words, all endpoints (E, N, U) |
| G2 | type-of minus real, fresh words, all endpoints (E, N, U) |
| H1 | E: imaginary minus real, fresh, all endpoints |
| H2 | N: type-of minus real, fresh, OpenAI endpoints |
| H3 | U: animal-intent minus no-intent words, fresh, real and type-of |
| H4 | N: (current minus historical), known minus fresh words, intent strata equal, real, type-of and neutral |
| H5 | U: current minus historical, fresh, real and type-of |
| H6 | N: (Anthropic minus OpenAI), Claude-origin minus GPT-origin words, fresh no-intent, real, type-of and neutral |

Reported for each: the estimate and interval under A, B and C, and the
pairwise differences between instruments with intervals. A shape "survives"
if all three agree in sign and their intervals exclude zero on the same side;
anything less is reported as instrument-dependent.

## Block 2: new questions, zoned codes

Primary tier (description and declining):

1. **How endpoints decline.** Among declines (DECLINE_PLAIN or
   DECLINE_WITH_POSSIBILITIES), the share with a possibility list. Fresh,
   neutral, real and type-of. Per endpoint; Anthropic minus OpenAI; current
   minus historical.
2. **Describe anyway.** Rate of DISCLAIM_AND_DESCRIBE. Fresh. Type-of minus
   real; current minus historical on real and type-of; per endpoint.
4. **Claimed provenance.** Among descriptions (E = 1), the share with a
   grounding claim. Fresh, real and type-of. Per endpoint; Anthropic minus
   OpenAI; real minus type-of. The imaginary frame is reported as a reference.
6. **Category.** Description rate, idea minus animal and object minus animal.
   Fresh, real and type-of. All endpoints, and by provider. Also under B.
7. **Consistency across repetitions.** For each word, endpoint and condition,
   the share of repetition pairs with the same response type, and the same
   describe/not-describe call. Per endpoint, fresh and known separately. The
   describe/not-describe version also under A and B.

Secondary tier (depends on marking, where two readers agreed at kappa 0.69):

3. **Given a description, how bare is it?** Among descriptions, the shares
   bare, hedged, framed, and disclaimed. Fresh, real and type-of. Bare share:
   Anthropic minus OpenAI; current minus historical.
5. **Prompt echo.** Unmarked description in the imaginary frame with and
   without counting the prompt's own word "imaginary" as a mark. Fresh. Per
   endpoint, and the difference.
8. **Late marking.** Among descriptions with any mark, the share marked only
   after the description starts. Fresh, imaginary and non-imaginary
   separately. Per provider; Anthropic minus OpenAI.

The U outcome in Block 1 also belongs to the secondary tier.

## Deferred

Anything about substitute descriptions, until an instrument version that
catches substitution by respelling. Anything touching the secondary-analysis
branch (Studies A and B), which has not yet been examined for this work.

## Changes

Any change to this list after results are seen will be added below with its
date and reason, and the affected results marked.
### November 15, 2026 implementation clarification before new estimates

This clarification was written before computing the newly declared estimates
or intervals. It resolves implementation details and the interpretation rule;
it does not add hypotheses or change the frozen instruments. Previously seen
results remain disclosed above. These analyses remain post hoc and exploratory.

**Weights and repeated conditions.** Average resolved repetitions within each
condition, then the named conditions equally, then endpoints equally, then
words within their source stratum. Real plus type-of comprises six equally
weighted conditions. Neutral plus real plus type-of comprises seven equally
weighted conditions, so neutral receives one-seventh of the condition weight.
Repetition consistency uses all ten conditions. Ordinary pooled fresh results
weight the three sources equally. Known-bank results weight the two intent
strata equally. H3 compares the Bo stratum with the equally weighted Claude
and GPT strata. H4 standardizes both banks to equal intent weights: fresh
weights are one-half Bo, one-quarter Claude and one-quarter GPT; known weights
are one-half per intent stratum. H6 compares the Claude-origin and GPT-origin
provider differences. H1 is the same calculation as G1/E and is reported as
an alias, not additional evidence.

**Unavailable values and paired support.** Omit null repetitions from their
cell. Omit and count a cell with no resolved values; average equally over the
remaining selected conditions and endpoints at each nesting level. For a
within-word contrast, use only words for which every participating term in
that instrument, bank and source stratum is defined. Average over those same
words on both sides. Preserve the fixed source weights; if a required stratum
has no usable words, report the estimate as not estimable. Report unresolved
responses, omitted cells and retained words. Instrument comparisons are
differences between each instrument's own declared estimator using shared
bootstrap draws. They do not impose an additional common-response subset.
Differences involving A can therefore reflect both coding and its
available-case support.

**Bootstrap.** Use 10,000 draws at seed 20261115, with NumPy's PCG64 generator
and linear percentile interpolation. Resample words independently within the
three fresh source strata and two known intent strata, using a recorded,
fixed ordering of strata and word names. Retain all conditions, endpoints and
repetitions of each sampled word and retain multiplicity when it is sampled
more than once. Use the same draw indices for all instruments, estimates and
instrument differences. Recompute each estimator, including conditional
ratios, within every draw. Count and report undefined draws, including zero
conditional denominators and absent usable support in a required stratum;
calculate intervals from finite draws and report their number. When any draw
is undefined, flag the interval as conditional on estimable draws. An estimate
with no finite draws has no interval. These unadjusted 95% intervals describe
word-resampling variation within the selected strata for the fixed endpoints
and frozen detectors. They do not include detector error or support
population-wide model or stimulus generalization.

**Conditional outcomes.** Calculate each conditional rate as the ratio of its
weighted numerator rate to its weighted denominator rate. Do not average
word-specific or endpoint-specific conditional ratios. For provider or
generation contrasts, first calculate each group's ratio and then subtract.
Possibility-list shares use the two decline response types as the denominator.
Grounding shares use E = 1 as the denominator and E = 1 with a grounding claim
as the numerator. Bare, hedged, framed and disclaimed shares use the four
exclusive description response types over E = 1. Prompt-echo estimates are
unconditional unmarked-description rates over fresh imaginary responses;
their difference is discounting echo minus counting it. Component rates
needed to interpret a declared contrast are reported alongside it. The
imaginary grounding reference is pooled across endpoints.

**Late marking.** Use E = 1 and a frozen `marking_position` other than `none`
as the denominator, and E = 1 with `marking_position == "after"` as the
numerator. The frozen positional measure covers fiction, construction,
interpretation and nonrecognition cues. It excludes attribute hedges and
implicit hypothetical framing. Non-imaginary includes neutral, real and
type-of conditions with the seven-condition weighting specified above.

**Repetition consistency.** Within each word, endpoint and condition, count
unordered distinct repetition pairs. The agreement proportion is the sum of
`n_k * (n_k - 1) / 2` over response categories, divided by `n * (n - 1) / 2`.
For A's binary description outcome, omit null values and require at least two
resolved repetitions; report resolved-pair coverage. Average the resulting
cell proportions using the declared condition, word and source weights.
Do not pool pair counts across cells, which would give more weight to cells
with more resolved repetitions. Response-type consistency is calculated for
C; binary description consistency is calculated for A, B and C.

**Interpretation rule.** Replace the statement that anything short of all
three intervals excluding zero is "instrument-dependent." Report a
`direction_robust` result when all three estimates have intervals entirely
above zero or all entirely below zero; otherwise report
`direction_unresolved`. Also report whether point-estimate directions are
mixed. Separately report each paired instrument difference and whether its
exploratory interval excludes zero. Common direction can coexist with
differences in magnitude. An unresolved common direction does not establish
an instrument effect, and an interval containing zero does not establish
equivalence. No p-values, multiplicity-controlled decisions or confirmatory
claims are introduced.
