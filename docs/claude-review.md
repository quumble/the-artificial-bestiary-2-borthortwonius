# Review of Claude's original Bestiary files

**Reviewer:** GPT/Codex. **Date:** November 11, 2026, before collection.

The investigator supplied the actual Bestiary files. Both are preserved unchanged in `prereg/`. This note records the review separately and does not amend Claude's registration or adopt its tests. No new-study response or private fresh word was inspected. The original GPT proposal remains unchanged in `docs/gpt-proposal/`.

## File integrity

| File | SHA-256 |
| --- | --- |
| `prereg/CLAUDE_PREREG.md` | `e679e793f2e4c57da0ff483bfe13d5d8b94d4e8913f9aa6fc41ec85d633a3669` |
| `prereg/claude_scorer.py` | `7244846fd96c884aa322d5b4d3a5c242dc048c67d825ceb94a03bf1a21fabd95` |

The second hash exactly matches the commitment in Claude's document. Its source baseline is the same `c00aab0e9902ee000b2e9d256dcf09b20c21c823` used for the GPT proposal. Claude reports writing independently of GPT's registration, while having designed study components, generated the no-intent words, and used historical responses to develop its scorer. Thus the repository starting point matches, but the analysts' prior access and development histories differ.

## Scorer findings

The frozen code implements its three outcomes as described: description form (E), description form with no counted cue (U), and non-recognition without description (N). Its command produces trial-level scores, not the five hypothesis tests or their exclusions and uncertainty estimates.

These synthetic examples use a public historical word. They are software probes, not study observations:

| Synthetic text | U | N | E |
| --- | ---: | ---: | ---: |
| A flembrast is a bird. It eats seeds. | 1 | 0 | 1 |
| I don't recognize flembrast. | 0 | 1 | 0 |
| A flembrast is an imaginary bird. | 0 | 0 | 1 |
| A flembrast is perhaps a bird. | 1 | 0 | 1 |
| Here is more information: a flembrast is a fictional bird. | 1 | 0 | 1 |

The fourth result follows the registered exclusion of bare hedges from cues. It also demonstrates why U cannot establish an unqualified factual assertion. In the fifth, the context pattern `more information` causes the entire sentence to be treated as an offer/context sentence, suppressing the explicit fiction cue. This is a concrete limitation of the offer filter. Any correction must use a separately versioned scorer and amendment, preserving this original and the promised comparison between versions.

The quoted development agreement, precision and recall are present in the document, but their underlying labelled records and evaluation script were not supplied. They have not been independently reproduced. Claude correctly identifies these as development results, not held-out validation. Different recall across providers, and unknown sensitivity across generations and conditions, limit behavioral interpretations of U differences.

The scorer accepts the repaired collector's exported `response`, target, condition, truncation and error fields. Its legacy `request_settings` and `visible_output_tokens` columns will be blank when those fields are absent from the export. Exact requests and settings remain in the attempt ledger and freeze manifest. A future analysis must use those authoritative records for provenance. The scorer's file loader silently skips malformed JSON lines, so its CSV alone is not a completeness audit.

## Items to settle before adopting Claude's confirmatory analysis

1. **Implement the missing analysis script.** The attachment is a scorer only. Claude commits to the analysis being in the repo before response text is read. The current collection protocol uses the stricter gate of freezing adopted analysis code before study requests. `freeze --protocol gpt-v1` currently selects GPT's implemented analysis only, although it also records both Claude originals as provenance.
2. **Define H4's inferential decision.** A two-sided permutation test of zero difference and a 95% interval inside a +/-0.10 margin answer different questions. The five-test Holm family specifies a difference-test p-value, but no equivalence p-value or multiplicity-adjusted equivalence decision. Treat the interval-inside-margin result as descriptive unless a pre-collection amendment defines the confirmatory equivalence procedure. The registered 95% interval rule is preserved, not replaced silently by another confidence level.
3. **Resolve incomplete-data rules.** Specify whether the 60% threshold applies to all planned word/model trials or each contrast arm, whether it is checked before or after truncation exclusion, how unequal condition completion is weighted, and which models count as having completed a batch. The truncated-response sensitivity must retain an explicit eligibility rule. These choices affect estimates and cannot be improvised after results are visible.
4. **Fix H4's source-set weighting explicitly.** Known words are half animal-intent, whereas fresh words are one third animal-intent. Permuting within intent strata does not itself define a source-standardized estimand. State whether to retain the original unweighted group means, with that composition limitation, or amend the estimand to a common intent weighting.
5. **State the scope of error control if both proposals are adopted.** Separate correction within each analyst's family is a valid description of separate families. It does not establish five-percent family-wise control across all claims from both analysts. A joint confirmatory claim needs a joint allocation or correction specified before collection.

## Interpretation corrections for the eventual report

- Use the literal names U, N and E. A whole-response cue filter cannot implement the agreed semantic scope rules. Labeling U a proxy does not remove its demonstrated blind spots.
- H3 compares stimulus sets that differ in author, intent, morphology and selection. A directional reversal can support the registered set-level prediction but cannot identify readable roots as its cause.
- H4 estimates a known/fresh difference in generation contrasts. Neither a small estimate nor an interval inside the margin demonstrates absence of training exposure. A negative interaction is compatible with exposure and with other differences between these fixed sets and models.
- Section 7's assertion that any occurrence of `bestiary` or `chesterton` is direct evidence of exposure is too strong. These are search flags requiring contextual inspection. A generic use of either term is not proof of encountering this study. Distinctive study-specific reproduction would be more informative, but still would not identify the route of exposure by itself.
- Reasoning-on fallback in Claude's exclusion section is not an available collection mode. The repaired collector halts on observed reasoning. If an exception is later adopted, it requires an explicit amendment and retained audit evidence.

File integration is complete. Claude's hypothesis analysis and the pre-collection decisions above remain outstanding. The private stimulus hash check, live content-neutral preflight and freeze in the collection environment also remain to be performed.
