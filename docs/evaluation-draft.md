# Evaluation and measurement draft

Status: the user prefers fewer mechanically scored measurements and minimal involvement in scoring individual responses. The five interpretive rules below are agreed. The two proposed mechanical measures, their inventories, and the analysis plan are not yet frozen. No new-study responses have been collected or inspected.

## Agreed scoring direction

The user wants to keep their own judgment out of routine response scoring as much as possible, regarding their involvement as a potential variable. They prefer fewer measurements done mechanically over many measurements done by hand.

The operational proposal is fixed, auditable, deterministic code. Routine human annotation is no longer the default plan. The user can continue to set research questions and approve measurement definitions without assigning production labels.

The prior calibration remains part of study-design history, not an independent validation set or a final answer key. Rule design still involves choices by the user and assistant; deterministic scoring makes those choices explicit and consistently applied rather than removing all judgment.

An LLM judge would introduce another source of semantic judgments. It is not part of the current proposal.

## Proposed primary measures: two phrase-based indicators

These are proposals, not yet approved inventories.

| Candidate measure | Mechanical operation | What it would support |
| --- | --- | --- |
| Listed fiction-expression presence | Detect whether a response contains any expression in a frozen fiction/invention inventory. Illustrative candidates include "fictional," "imaginary," and "invented." | Comparisons of how often those listed expressions occur across models and prompt conditions. |
| Listed qualification-expression presence | Detect whether a response contains any expression in a frozen uncertainty/non-recognition inventory. Illustrative candidates include "might," "may," "could," "I don't recognize," and "not familiar." | Comparisons of how often those listed expressions occur across models and prompt conditions. |

Retain exact matched text and locations for audit. The inventory, normalization, boundary matching, and treatment of quoted text must be specified before scoring the main batch.

These are surface-expression measurements. An occurrence is not automatically a genuine disclaimer, an uncertainty claim about the referent, or a successful correction of a false premise. A phrase can occur inside a quotation, a negation, a question, or a statement about something else. A model can also qualify content with wording absent from the inventory.

The measure names and reports must therefore describe the actual operation. Do not relabel literal-expression presence as "recognized fictionality" or "semantic uncertainty," and do not treat absence of a listed expression as proof of confidence, factual knowledge, or confabulation.

The broad confabulation distinction remains conceptually important, but a valid automatic confabulation rate is not delivered by these two indicators. That limitation is explicit, not an invitation to silently restore hand coding.

## Supporting metadata

Keep response word count, token usage, completion status, stop reason, errors, model identifiers, prompt condition, stimulus identity, and attempt provenance. Length and completion information help assess the opportunity to produce a listed phrase and the effect of the 500-token limit. They are supporting information, not an expanding set of primary hypotheses.

The existing free-text prompts remain the basis of the comparison. Do not add self-classification questions or force a structured answer format merely to make scoring easier; that would change the experimental task.

## Proposed deterministic workflow

1. Freeze a versioned specification of the selected inventories, text preprocessing, word counting, boundary rules, and missing-data handling before inspecting the main new batch.
2. Run the same scoring code and inventory on the historical responses chosen for comparison and the new responses.
3. Store each feature value with its exact matches and scorer version. Keep raw responses unchanged.
4. Aggregate by model and prompt condition, retaining word and word-set distinctions. Repeated answers to one word do not create additional independent words.
5. Keep later changes to the scorer identifiable as revised analyses; do not silently replace the original scores.

A zero means no listed match in the observed text. On an incomplete answer it does not establish that no matching expression would have appeared later. Completion flags must remain visible, and the final analysis must pre-specify denominators and how incomplete outputs contribute to each result.

## Agreed core rules

The user explicitly agreed to all five rules below. These supersede conflicting provisional interpretations in the calibration discussion. Earlier raw judgments remain unchanged in [the calibration log](calibration-log.md).

### 1. Fiction signals

"Native to fictional realms" counts as acknowledging fiction, just as "this is fictional" does.

Record this as an observable signal in the language. It does not establish a model's private recognition or beliefs. Fiction acknowledgment and the presence of descriptive characteristics are separate observations.

### 2. Scope of qualification

"This description is invented" qualifies the whole description, whether it appears at the beginning or end.

"It may eat insects" qualifies only that trait.

Apply qualification according to what it refers to. Placement alone does not determine scope. If scope cannot be resolved confidently, preserve that uncertainty under rule 5.

### 3. Mixed answers

"It lives underground. It may eat insects." receives both **assertion present** and **speculation present**.

Preserve both observations. Do not force mixed answers into one mutually exclusive category. A local qualifier does not erase unrelated assertions.

### 4. Confabulation versus licensed fiction

Unsupported invented details presented as real count as confabulation.

The same details under an explicitly imaginary prompt count as licensed fiction.

Evaluate the prompt and response together. Confidence or the absence of a repeated fictional reminder is not sufficient by itself. Establishing lack of support remains part of applying the rule; a familiar-looking word root does not verify a purported real referent.

### 5. Unclear and incomplete cases

Ambiguity receives an **uncertain** flag.

Cut-off answers receive an **incomplete** flag.

Neither automatically becomes a no. Preserve the evidence that is available and identify what cannot be determined.

## Role of the agreed rules in a mechanical study

The five rules constrain interpretation. They do not imply that a phrase matcher can resolve disclaimer scope, determine factual support, or classify every mixed response semantically.

In particular:

- Matching "fictional" and deciding what it qualifies are different operations.
- "It lives underground. It may eat insects." contains a qualification expression but also an independently stated habitat. A whole-response claim that it is entirely hypothetical would exceed the mechanical observation.
- A fictional prompt can license confident narration without an extra output-side fictional reminder.
- Unsupported factual invention requires a support judgment beyond checking for a hedge.
- Incompletion can be identified from available API status. Semantic ambiguity cannot be exhaustively identified through a word list.

The earlier proposed rich semantic dimensions, including category fit, detailed substitutions, and response-wide reporting-versus-interpreting labels, are not default production measurements under the user's preference. Any later use must be separately identified and justified.

## Validation appropriate to these measures

First verify the software contract: identical inputs and scorer versions produce identical outputs, and known text fixtures exercise normalization, phrase boundaries, overlapping matches, quotation/negation cases, empty outputs, and incomplete responses.

Check that aggregation preserves the specified denominators and that prompt text or metadata do not accidentally enter response-only matching.

These checks establish correct execution of the measurement rules. They do not establish semantic accuracy. Broad semantic claims would require further validation, not just more elaborate regular expressions. The primary reports should remain within what the literal measurements support.

The user is not expected to hand-score the corpus or serve as the default adjudicator. No human or model judge has been selected.

## Remaining decisions

- Whether to adopt both proposed expression indicators or a smaller/different mechanically defined set.
- Exact expression inventories, preprocessing, match boundaries, and quotation handling.
- Word-count and completion rules, aggregation denominators, comparisons, and uncertainty calculations.
- Model lineup, spending cap, and the historical/new sample to include.

## Provenance

The [calibration log](calibration-log.md) preserves the changing definitions and the later preference for mechanical scoring. Earlier ratings were elicited under a construct mismatch and are not a fixed answer key.

Historical source inspected at [`7fec51af5d28b743763225f4dd52ab29a4cb4d60`](https://github.com/quumble/the-artificial-bestiary/tree/7fec51af5d28b743763225f4dd52ab29a4cb4d60). The source [adjudicated coding scheme](https://github.com/quumble/the-artificial-bestiary/blob/7fec51af5d28b743763225f4dd52ab29a4cb4d60/Haiku%20v3%20Retest/Haiku_handcode_adjudicated/coding_scheme.md) and earlier automated labels remain historical artifacts, not the new scorer.

The original fabricated words are now public. Apparent recognition or references to prior fictional descriptions may complicate interpretation; this is a possibility, not an established contamination finding.
