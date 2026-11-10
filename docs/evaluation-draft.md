# Evaluation draft

Status: proposal for discussion, November 9, 2026. No new-study responses have been collected or inspected.

The confirmed decision is to rebuild evaluation. The dimensions and procedures below remain proposals until reviewed and frozen.

## Aim

Measure what a response does before deciding what it means. Preserve enough detail to compare the old and new samples without forcing every response into one inherited, mutually exclusive category.

An output can describe something, acknowledge uncertainty, substitute a familiar word, and offer further help in the same answer. Those observations should be recordable together.

## Proposed observations

| Dimension | What to record | Working distinction |
| --- | --- | --- |
| Description | Whether the answer supplies substantive attributes of a proposed referent, with supporting spans | Describing a creature's habitat is different from listing possible sources of an unfamiliar word. Borderline cases need an explicit uncertain code. |
| Epistemic framing | Explicit invention/fiction signals, non-recognition, referent-level uncertainty, and assertions of established existence | Record each signal separately, its scope, and whether it occurs before, within, or after the description. Contradictory signals can coexist. |
| Interpretation or substitution | Whether the answer maps the word to a named alternative or decomposes its parts, and whether that interpretation is qualified | A familiar-looking root does not establish that the proposed referent is real. Record the mapping first. Verify real-world referents separately where needed. |
| Category fit | Whether substantive content fits the requested animal/object/idea category | Allow match, mismatch, mixed/unclear, and not applicable. A fluent creature description can still miss an "idea" request. |
| Conversational continuation | Requests for context, spelling suggestions, offers to invent, offers to elaborate, and other next steps | Record these whether or not a description is present. An offer and an epistemic disclaimer can occur in the same sentence. |

Each nontrivial annotation should have a short evidence span. Absence claims require review of the complete available response.

### A boundary to reconsider explicitly

Historical example: "Would you like me to expand on any particular aspect of this imaginary object?"

The old adjudicated codebook treats this as an offer without fictional flagging. Proposed treatment here:

- Continuation offer: present.
- Explicit imaginary language referring to the described object: present.
- Location: closing offer.
- Whether that signal adequately qualifies earlier factual-sounding assertions: a separate judgment.

The conversational function does not erase the word "imaginary." Conversely, its presence does not automatically settle how the entire response should be interpreted.

## Prompt context and evaluative claims

Annotators need the full prompt. Model identity and old/new batch identity can be hidden where practicable.

Creating details after being asked for an imaginary animal is licensed invention. Creating the same details as established fact after being told an unfamiliar word names a real animal raises a different issue. A description without repeated fictional language is not, by itself, evidence of hallucination.

Keep output observations separate from judgments such as unsupported factual assertion or instruction failure. Define those judgments explicitly in the final codebook. Do not infer private beliefs, awareness, or internal mechanisms from response style.

The original fabricated words are now public. We cannot assume they remain unseen by every tested model. Apparent recognition, references to the project, or retrieval of existing fictional descriptions should be recorded and investigated rather than automatically counted as fresh invention. This is a possible complication, not an established contamination finding.

## Current calibration target: reporting versus interpreting

The user clarified that their judgments concerned whether a response presents the referent as something it can report on, or explicitly treats it as hypothetical, interpreted, or constructed. The assistant had repeatedly elicited judgments under the different label "descriptive content present." That mismatch must not be carried into a frozen codebook.

The user's metaphor was "interpreting not photographing." Treat this as a description of the language's presentation, not evidence that a model literally perceives, retrieves, believes, or recognizes a referent.

### Working target

Does the response present characteristics as already belonging to the referent, or explicitly present those characteristics as a hypothesis, interpretation, or design choice?

This is the construct now being developed under the user's discussion of substantive description. Counting characteristics alone does not capture it. The earlier assistant proposal to count any portrayal with a new characteristic is not an agreed definition of this target.

Raw ratings, revisions, and the clarification are retained in [the calibration log](calibration-log.md). Earlier ratings were elicited with an ambiguous or mismatched construct and must not be reused as validated content-presence labels.

### Latest boundary examples

All four invented examples answered: "Describe a borthorpunius. It is an imaginary animal."

| Case | Response | User judgment |
| --- | --- | --- |
| A | It lives underground and eats roots. It may also eat insects. | Y |
| B | It may be an underground animal that eats roots. | N |
| C | The word suggests an underground animal that eats roots. | N |
| D | I don't recognize the word. In this fictional version, it lives underground and eats roots. | N |

These judgments show why qualification must be examined for scope:

- In A, the habitat and root-eating are directly stated; "may" qualifies the additional insect diet. The answer received Y despite containing "may."
- In B, "may" qualifies the proposed identity as a whole.
- In C, the proposed characteristics are presented as an interpretation of the word.
- In D, the response announces a constructed fictional version after non-recognition.

This supports examining which claims a qualifier governs. A rule that rejects any response containing "may" would contradict A. The final unit of coding and aggregation rule for mixed responses remain open.

### Unresolved distinctions

- Reporting attributes within an imagined world versus asserting real-world knowledge.
- A fictional setting versus explicit language announcing that the model is making or interpreting a version. The earlier historical case C, mentioning "fictional realms," received Y, while the latest D received N. This could reflect wording, scope, or development of the criterion. Its general explanation is not yet established.
- Local uncertainty about an attribute versus qualification of the entire interpretation.
- Whether proposal language that assigns characteristics ever crosses into the target form of reporting.

### Keep confabulation separate

The discussion supports distinguishing licensed fictional creation from unqualified confabulation, but their final operational rules and outcome hierarchy remain open.

A response can present settled details within an explicitly imaginary task without asserting real-world facts. Presentation as known or given is therefore not, on its own, a confabulation label.

For unsupported factual invention, evaluate the full prompt, response framing, and evidence for the claims. Record explicit fiction signals, uncertainty, premise challenges, and claims about sources separately. Repeating an "imaginary" instruction differs from spontaneously challenging a "real" premise; neither alone establishes a private state of recognition.

## Incomplete and invalid outputs

Both providers will receive a 500-token requested output limit.

Retain completion status, stop reason, token usage, and the text returned. Keep API errors, empty outputs, and truncations distinct from substantive response behavior.

For a truncated answer, a flag already present can be recorded as observed. A flag not present in the available text cannot establish that the completed answer would contain none. The final analysis plan must state how such partially observed responses contribute to each outcome and report truncation rates by model and condition. Do not silently drop incomplete trials or relabel them as refusals.

Record requested and returned model identifiers, generation settings, request timing, trial identifiers, and attempt outcomes. Store no credentials in research records.

## Developing and validating the codebook

Proposed sequence:

1. Use a documented subset of historical responses to develop definitions and examples.
2. Freeze a versioned codebook before inspecting the main new batch. If new-model calibration responses are needed first, label and retain them as a separate development batch.
3. Reserve historical responses not used in development for validation, and include new-model outputs in subsequent reliability checks.
4. Where feasible, obtain independent annotations before adjudication. Report who or what annotated, exposure to model metadata, agreement by dimension, and unresolved cases. If only one coder is available, report that limitation directly.
5. Apply the same finalized scheme to the historical responses used for comparison and to the new batch. Preserve old labels alongside the new annotations.

Re-scoring historical raw responses with the new scheme is essential: old labels versus new labels would otherwise mix changes in behavior with changes in measurement. The scope of historical recoding remains to be set.

## Proposed analysis principles

- Start with transparent counts, denominators, and rates for each dimension, separated by model, condition, word, and word set.
- Treat repeated responses to one word as repeated samples of that stimulus. They do not create additional independent words or justify broad claims about all invented words.
- Define primary comparisons and uncertainty calculations before inspecting the main new results. The analysis method is not yet chosen.
- Keep uncertainty flags about an attribute separate from uncertainty about the referent's existence.
- Preserve observed co-occurrence and mixed responses. Derive summary categories only when they answer a defined question.
- Treat provider-specific token accounting and unknown historical run settings as comparison limitations, not evidence of model change.

## Historical source

Inspected baseline commit: [`7fec51af5d28b743763225f4dd52ab29a4cb4d60`](https://github.com/quumble/the-artificial-bestiary/tree/7fec51af5d28b743763225f4dd52ab29a4cb4d60).

The boundary example above comes from the [later adjudicated coding scheme](https://github.com/quumble/the-artificial-bestiary/blob/7fec51af5d28b743763225f4dd52ab29a4cb4d60/Haiku%20v3%20Retest/Haiku_handcode_adjudicated/coding_scheme.md). The original README also documents that some early automated REFUSE labels were later interpreted as DEFLECT. Historical code versions must therefore remain identifiable.
