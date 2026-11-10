# The Artificial Bestiary 2: Borthortwonius

A continuation of [The Artificial Bestiary](https://github.com/quumble/the-artificial-bestiary): begin by repeating its core experiment for comparison, rebuild the evaluation, then use the findings to guide further experiments.

> "This is not a redo of the bestiary, this is the bestiary with wings."

## Decisions agreed on November 9, 2026

- **500 output tokens per request for both OpenAI and Anthropic.** This is the requested generation limit, not a word limit or a minimum response length. The eventual runner must document how each selected model accounts for reasoning within its output budget.
- **Preserve the core design.** Ask models to describe the original fabricated words under real, imaginary, and "type of" framings crossed with animal, object, and idea, plus a neutral condition.
- **Rebuild the evaluation from the ground up.** The earlier categories and results are evidence to learn from. They do not predetermine the new measurements.
- **Comparison first, exploration second.** Complete and preserve an initial comparison batch before using its results to select new probes.

The shared 500-token limit is an intentional change from the archived runner settings. This project repeats the core design with revised measurement and a standardized requested output budget. It should not be described as an exact reproduction of every historical setting.

## Current status

Study planning. No experiments have been run in this repository.

The [evaluation draft](docs/evaluation-draft.md#agreed-core-rules) now contains five agreed core rules:

- Explicit fiction signals count as acknowledgment of fiction.
- Qualification applies according to its scope; a whole-description disclaimer can occur at either end.
- Mixed answers retain both assertion and speculation indicators.
- Unsupported factual invention is distinguished from licensed fiction.
- Ambiguity and cut-off responses receive uncertain and incomplete flags, not automatic negative scores.

The [calibration log](docs/calibration-log.md) preserves the judgments, clarification, and explicit agreement.

**Scoring preference:** minimize the user's involvement in scoring individual responses and use mechanical measurements. After considering an initial two-indicator proposal, the user requested a broad candidate set. The [measurement catalog](docs/measurement-catalog.md) now proposes 32 families, from literal expression counts and cue placement to text structure and repeated wording. No final battery or inventory has been approved. There is no default human or LLM judge, and the surface measures must not be represented as an automatic confabulation detector.

The five agreed rules remain constraints on interpretation. The [measurement draft](docs/evaluation-draft.md) distinguishes those principles from what fixed code can directly measure. The protocol is not yet frozen or preregistered.

The following remain open:

- Model lineup and exact model identifiers.
- Spending cap.
- Which historical stimulus sets and repetition counts to include in the initial batch. The eight-word, 800-trial-per-model design is a proposal, not yet a decision.
- Final mechanical measures, expression inventories, preprocessing, software validation, outcomes, and analysis plan.
- Analysis denominators for incomplete or uncertain responses and model-specific generation constraints.

## Historical reference

Initial source inspection: [`quumble/the-artificial-bestiary` at `7fec51af5d28b743763225f4dd52ab29a4cb4d60`](https://github.com/quumble/the-artificial-bestiary/tree/7fec51af5d28b743763225f4dd52ab29a4cb4d60).

That repository contains the nine-word Sonnet pilot, eight-word retests, raw responses, and several stages of coding. Historical source defaults do not by themselves establish every setting used in the original runs. Further comparison must distinguish runner defaults, recorded settings, and unknown settings.
