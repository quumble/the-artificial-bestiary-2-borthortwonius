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

The [evaluation draft](docs/evaluation-draft.md) proposes independent observations and rules for handling ambiguous responses. It is a working proposal, not a frozen codebook or a preregistration.

The following remain open:

- Model lineup and exact model identifiers.
- Spending cap.
- Which historical stimulus sets and repetition counts to include in the initial batch. The eight-word, 800-trial-per-model design is a proposal, not yet a decision.
- Final annotation rules, validation procedure, outcomes, and analysis plan.
- Treatment of incomplete responses and any model-specific generation constraints.

## Historical reference

Initial source inspection: [`quumble/the-artificial-bestiary` at `7fec51af5d28b743763225f4dd52ab29a4cb4d60`](https://github.com/quumble/the-artificial-bestiary/tree/7fec51af5d28b743763225f4dd52ab29a4cb4d60).

That repository contains the nine-word Sonnet pilot, eight-word retests, raw responses, and several stages of coding. Historical source defaults do not by themselves establish every setting used in the original runs. Further comparison must distinguish runner defaults, recorded settings, and unknown settings.
