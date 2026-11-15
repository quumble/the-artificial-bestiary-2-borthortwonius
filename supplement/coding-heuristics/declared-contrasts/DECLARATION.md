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
