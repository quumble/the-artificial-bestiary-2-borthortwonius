# Mechanical response-coding codebook — version 1.0.0

**Unit:** one selected API response to one specific coined-word prompt, including its word, frame, requested category, model, batch and repetition. Score **response text only**, never the prompt or metadata. The prompt supplies `word` to the scorers; only GPT's M22 (not used for primary coding) uses prompt-word overlap.

**Design principle:** retain the preregistered binary measures **without substitution**. This codebook defines a *new, post-publication* partition and supporting multi-label tags for descriptive analysis. Every rule is a frozen function of published scorer outputs; no individual semantic judgments or inference about actual existence are used.

## A. Registered GPT primary flags (unchanged)

| Column | Mechanical rule | What it does **not** establish |
|---|---|---|
| `M01` | 1 if any literal match to GPT v1.0's fiction-expression inventory | That the entity is known to be imaginary; prompted word echoes can match |
| `M02` | 1 if any literal match to GPT v1.0's modal/qualification inventory | Reliable uncertainty about the referent; e.g. a bare `might` matches |
| `M03` | 1 if any literal match to GPT v1.0's nonrecognition inventory | That the model has never seen the word |
| `M09` | 1 if any exact-target definition-form match (target plus frozen predicate suffix) | A positive assertion; **negated** definitions also match |

These are **overlapping binary features**, not a one-of-four classification. Use the original `score(response, word, prompt)['features'][Mxx]['any']` or embedded `response-features.jsonl` outputs. The original eight fresh-bank GPT primary comparisons are imaginary minus real and type-of minus real for each of the four outcomes, using the repo's registered weighting and word-cluster bootstrap. This package does **not** recalculate their p-values or intervals.

## B. Registered Fable outcomes (unchanged)

Fable v1.1 normalizes the response, identifies nonrecognition (`nonrec`), fiction (`fiction`), construction (`construct`), interpretation (`interp`), and description-form cues using its frozen patterns. Its `E` is true if it finds **at least one positive target definition form or two or more attribute-form matches**. A negated target definition alone does not count as a positive definition; and specified question/offer contexts are filtered by the original scorer.

Let `C = any_nonrec OR any_fiction OR any_construct OR any_interp`.

- `F_E` = `desc_form` = E (1 for description form).
- `F_U` = `unmarked_description` = E AND NOT C. **U is a subset of E.**
- `F_N` = `nonrec_no_description` = `any_nonrec` AND NOT E. **N and E are disjoint.**

E, U and N **do not exhaust responses**; they are **not** three mutually exclusive values. The Fable scorer also returns counts for positive versus negated definitions and separate cue families. It is used unchanged via `score_text`.

### Links to the six registered Fable tests

| Test | Registered response code | Comparison (the original analyzer governs the exact testing and weights) |
|---|---|---|
| H1 | `F_E` | Imaginary − real, fresh words, all endpoints |
| H2 | `F_N` | Type-of − real, fresh words, OpenAI endpoints |
| H3 | `F_U` | Animal-intent − no-intent, fresh words, real + type-of conditions |
| H4 | `F_N` | (Current − historical) endpoint gap, previously published − fresh words; intent-standardized, real + type-of + neutral |
| H5 | `F_U` | Current − historical endpoints, fresh words, real + type-of |
| H6 | `F_N` | (Anthropic − OpenAI) gap, Claude-origin − GPT-origin words in fresh no-intent bank, real + type-of + neutral |

The original registered procedures use permutation tests and familywise Holm correction; this package's descriptive tables **cannot substitute** for those tests.

## C. Proposed exclusive response category (`response_class`)

Only for `usable = 1`. Apply the following tests in order; **exactly one** category results. Every value follows only from Fable v1.1 outputs (it does not rely on the GPT feature inventory).

| Order | Code | Frozen decision rule | Plain-English surface pattern |
|---:|---|---|---|
| 1 | `D0_UNMARKED` | `E=1, C=0` (thus U=1) | Description form without any of Fable's four registered marking-cue families |
| 2 | `D1_NONREC_MARKED` | `E=1, any_nonrec=1` | Description form and matched nonrecognition language coexist |
| 3 | `D2_OTHER_MARKED` | `E=1, C=1, any_nonrec=0` | Description form with fiction, construction, or interpretation marking but no nonrecognition marking |
| 4 | `N0_NONRECOGNITION` | `E=0, any_nonrec=1` (thus N=1) | Nonrecognition language without description form |
| 5 | `O0_CUED_OTHER` | `E=0, any_nonrec=0, C=1` | Fiction/construction/interpretation marking without a description form |
| 6 | `O1_UNMARKED_OTHER` | `E=0, C=0` | Residual response with neither a description form nor any of the four Fable cue families |
| Before all | `X_UNUSABLE` | Missing, unselected/nonterminal, invalid, or blank response | No behavioral value; **never** turn into `O1_UNMARKED_OTHER` |

**Proof that bins partition usable responses:** E is either 1 or 0. If E=1, C is 0 (D0) or 1, and `any_nonrec` is 1 (D1) or 0 (D2). If E=0, `any_nonrec` is 1 (N0), else C is 1 (O0) or 0 (O1). Thus exactly one state. Tests assert the partition.

**Examples (synthetic, illustrative only; actual regex matching is the authoritative rule):**

| Example response to “zorf” | Intended illustration |
|---|---|
| `Zorf is a small creature.` | D0 if the registered positive definition matcher fires and no cue does |
| `Zorf is an imaginary forest creature.` | D2: description with a fiction cue |
| `Zorf is a kind of animal, but I don't recognize the term.` | D1 *only if* the registered scorer finds both a positive description and nonrecognition |
| `I don't recognize zorf as an established term.` | N0 if recognized as nonrecognition and no E |
| `Let's imagine an example together.` | O0 if construction cue fires but E does not |
| `Could you give more context?` | O1 if neither E nor a member of C fires (context requests alone are outside C) |

These labels are **not** labels for knowledge, factual assertion, confabulation, compliance, or appropriateness. In particular D0 is *cue-unmarked syntax*, not a proven unsupported factual assertion.

## D. Secondary, non-exclusive tags (`S_*`)

Tags may co-occur. `secondary_tags` is a pipe-separated **sorted** list of all S_* fields equal to 1; `secondary_tag_count` is its length. A zero means the listed pattern was not observed in the usable visible response, **not** that the behavior or belief is absent.

| Field | Exactly when 1 | Source |
|---|---|---|
| `S_FICTION` | Fable `any_fiction` | Fable cue |
| `S_NONRECOGNITION` | Fable `any_nonrec` | Fable cue |
| `S_CONSTRUCTION` | Fable `any_construct` | Fable cue |
| `S_INTERPRETATION` | Fable `any_interp` | Fable cue |
| `S_QUALIFICATION` | GPT M02 any | GPT inventory |
| `S_CONTEXT_REQUEST` | GPT M07 any | GPT inventory |
| `S_OFFER` | GPT M08 any | GPT inventory |
| `S_NEGATED_DEFINITION` | Fable `n_def_negated > 0` | Fable structural patterns |
| `S_GPT_DEF_LOCAL_NEGATION` | Any GPT M09 match has `local_negation=True` | GPT local 3-token window; **not** semantic negation scope |
| `S_QUOTED_GPT_CUE` | Any GPT M01/M02/M03/M04 match marked `quotation_overlap=True` | GPT quote heuristic |
| `S_PROMPT_IMAGINARY_OVERLAP` | Condition is imaginary_* and GPT M01 match entry literally `imaginary` | Potential prompt-word overlap; **not** proof of copying |
| `S_TARGET_DEFINITION_DISAGREEMENT` | GPT M09 and Fable E disagree | Operational difference, not correctness |
| `S_WORD_REPAIR` | GPT M32 any | GPT inventory |
| `S_CATEGORY_WORDS` | Any of GPT M31's animal/object/idea vocabulary components | Surface lexical overlap; prompt/target exclusions as in GPT scorer |

The original GPT secondary feature summaries (M04–M32) are already available separately in the repository; this package exports selected high-value flags, not a replacement for the complete 32-family feature vector.

## E. Structural comparison (`gpt_definition_fable_E`)

Compare GPT M09's **exact-target definition form** with Fable E's **positive target definition OR at least two attribute forms**:

| Code | GPT M09 | Fable E | How it can happen |
|---|---:|---:|---|
| `BOTH` | 1 | 1 | A positive definition of the target |
| `GPT_ONLY` | 1 | 0 | E.g. the GPT pattern matches `zorf is not ...`, but Fable excludes negated positive definitions |
| `FABLE_ONLY` | 0 | 1 | E.g. two attribute forms but no exact-target GPT definition; or a Fable-only grammatical pattern |
| `NEITHER` | 0 | 0 | Neither syntactic matcher fires |

There is **no gold standard** here. This is a useful disagreement audit, not a measure of scorer accuracy.

## F. Edge cases and coding order

1. **Audit input selection:** input should be the released `analysis/response-features.jsonl`, whose rows were validated against the freeze by the original analyzer. Never select an arbitrary "last successful" attempt yourself. This tool deliberately rejects `attempts.jsonl`.
2. **Exclusions before content coding:** if `terminal=false`, `issue=true`, `protocol_violation=true`, or response is empty, set `usable=0`, all behavioral flags blank, `response_class=X_UNUSABLE`. Retain the record for denominator audits. The published selected export is already audited.
3. **Use correct registered scorer and inventory:** GPT `gpt-bestiary-2-v1.0` and Fable `claude-fable-5-2/1.1`. Hash all source files. If a published GPT score is embedded, prefer it to re-scoring; optional `--verify-embedded` checks equality.
4. **Normalization:** delegated to original scorer. GPT uses its own NFKC/casefold/token matching and sentence boundaries; Fable its separately registered NFKC/punctuation/Markdown normalization. **Do not merge their lexicons.**
5. **Match precedence:** delegated to original scorer's greedy nonoverlap / regex overlap rules; this tool never changes registered matches or adds contextual vetoes.
6. **Mixed responses:** allow simultaneous nonrecognition and description. D1 exists for this case; **do not** force all nonrecognition language into N.
7. **Negation:** GPT M09 matches may be negated; Fable excludes some patterns from positive definitions. Preserve both and flag the difference. An Fable `n_def_negated` occurrence is not an independent semantic negation label.
8. **Questions/offers:** Fable excludes certain matches in question/offer sentences, as specified in v1.1. GPT Mxx binary matches remain independent. Preserve these differences.
9. **Truncation:** GPT retains observed-prefix matches and a truncation indicator. Fable's registered primary excludes truncated responses. `fable_primary_eligible=0` when `truncated=true`; still output its descriptive flags as prefix-only observations. If status is missing, Fable primary eligibility is blank/unknown.
10. **Denominators:** report number of records, GPT usable counts and Fable primary-eligible counts separately. Do not interpret the 16,000 responses or repeated trials as 16,000 independent words. Any new inferential analysis requires word-level clustering/stratification and fresh multiplicity decisions.
11. **Condition parsing:** only `neutral` or `real|imaginary|type_of` × `animal|object|idea`. Source, intent, origin and model labels are metadata, never response-derived behavior labels.
12. **Mismatch is not error:** `GPT_ONLY` / `FABLE_ONLY` are expected because the two registered constructs differ. Use comparison for measurement analysis, not to choose a "winner."

## G. Reportable claims

**Safe:** “Under the frozen surface codebooks, N% of eligible responses had at least one nonrecognition expression”; “X% of syntactically described responses also carried a listed fiction/construction cue.”

**Not supported by mechanical scoring alone:** “X% of responses hallucinated,” “the models believed invented terms were real,” “word origin caused recognition,” or “a response without cues is confidently false.” The imagined prompts deliberately authorize invention, and there is no genuine real-word control bank.

**Statistical status:** This taxonomy was designed after publication; results from it are **exploratory/descriptive**. The registered GPT and Fable outcomes stay separately corrected within their original families. Any new hypotheses/tests using this taxonomy require separately declared error control and should not be appended to either original confirmatory family without disclosure.
