# Mechanical measurement catalog

Status: broad proposal for discussion. No measures in this catalog have been approved as the final battery or implemented. The user asked to err toward a broad proposal while preserving minimal personal scoring.

The earlier two-indicator proposal remains part of this larger pool; it is not a ceiling. The existing free-text prompts stay unchanged. The output cap is now 1,024 visible tokens (see the [sample design](sample-design.md)). All 32 candidate families below can be computed from saved responses with deterministic text processing and fixed inventories. They require no additional generation calls or per-response semantic judge. Several families yield more than one column; this is not a claim of 32 independent hypotheses.

## How to read the catalog

- **direct**: a count or text-similarity calculation whose meaning follows from its specified algorithm.
- **lexicon**: deterministic matches to a declared inventory. Inventory choices and coverage are limitations.
- **pattern**: deterministic surface constructions that approximate a behavior but do not identify it perfectly.
- **position**: locations of literal matches, not inferred semantic scope.

"Mechanical" describes reproducible execution. It does not turn a proxy into a direct measurement of confidence, knowledge, confabulation, or creativity.

## Language about knowledge and invention

### M01. Fiction-expression matches

Type: lexicon · Candidate for the primary shortlist.

Operation: Count and locate matches to a frozen fiction/invention phrase inventory; record any-match, counts, and word-normalized density.

Question: Does a framing change how often the answer explicitly uses fiction-related language?

Limit: Matches are not verified acknowledgments about the referent.

### M02. Qualification-expression matches

Type: lexicon · Candidate for the primary shortlist.

Operation: Count and locate a frozen set of modal and hedge expressions, with separate component flags for individual expressions or subfamilies.

Question: Does the answer use more qualified wording?

Limit: A modal can concern a local trait, permission, a quotation, or another topic.

### M03. Non-recognition-expression matches

Type: lexicon · Candidate for the primary shortlist.

Operation: Match narrow phrases such as 'I don’t recognize', 'not familiar with', and 'no record of', after specified apostrophe normalization.

Question: Does the answer explicitly use non-recognition language?

Limit: This records language, not actual absence from model knowledge.

### M04. Construction-expression matches

Type: lexicon · Candidate for the primary shortlist.

Operation: Match phrases such as 'let’s imagine', 'we could create', and 'in this fictional version'.

Question: Does the response announce a creative act or proposed version?

Limit: These phrases can appear in an offer without a subsequent description.

### M05. Interpretation-expression matches

Type: lexicon.

Operation: Match phrases such as 'the name suggests', 'based on the word', 'could mean', and 'sounds like'.

Question: Does it discuss interpreting the word rather than simply narrating properties?

Limit: Does not establish the response’s overall stance or a correct etymology.

### M06. Reality and certainty expressions

Type: lexicon.

Operation: Keep separate frozen inventories for realness/established-status wording and certainty wording; retain their individual counts.

Question: Does the response use phrases such as 'a real', 'is known as', or 'undoubtedly'?

Limit: Claims, negations, and fictional narration can all contain these expressions.

### M07. Context-request expressions

Type: lexicon.

Operation: Match phrases such as 'could you provide context', 'where did you encounter', and specified variants.

Question: How often does the response explicitly request more input?

Limit: The inventory may miss paraphrases; not every question is a context request.

### M08. Help and co-creation offers

Type: lexicon.

Operation: Match a fixed inventory of offers such as 'I can help', 'would you like me to', and 'we can create'.

Question: How often does it offer a path forward?

Limit: Offer matches cannot prove that every non-answer remains conversationally open.

## Definition forms, placement, and mixed patterns

### M09. Target definition forms

Type: pattern · Candidate for the primary shortlist.

Operation: Match frozen literal constructions involving the exact target, such as 'a <target> is', '<target> is', and '<target> refers to'; retain negation/cue co-occurrence separately.

Question: How often does it adopt the surface form of a definition?

Limit: '<target> is not a recognized word' also has a definition form. This is not an assertion-of-existence score.

### M10. Attribute-statement forms

Type: pattern.

Operation: Match a narrow set of surface constructions such as 'it has', 'it lives', 'they eat', and 'its body'.

Question: Does the text use forms associated with assigning traits?

Limit: Pronoun reference and substantive meaning are not resolved by these patterns.

### M11. First qualification location

Type: position.

Operation: For each selected cue family, store the first matched character offset, word index, and word index divided by response word count.

Question: How early does qualifying language appear?

Limit: Missing cues are null with a separate no-match flag, not a position of zero or one. Truncation limits absence claims.

### M12. Opening and closing cue distribution

Type: position.

Operation: Record cue presence in the first sentence and last sentence, plus proposed first/last 20% word windows.

Question: Are cues concentrated at the beginning, end, or throughout the text?

Limit: Position does not establish scope. Window size and sentence rules need freezing.

### M13. Definition/cue order

Type: pattern · Candidate for the primary shortlist.

Operation: Compare the earliest M09 match with the earliest selected cue match; retain definition-first, cue-first, definition-only, cue-only, and neither cases.

Question: Does definition-shaped language precede explicit qualifying language?

Limit: An eventual whole-answer disclaimer may qualify preceding text. Ordering is not an unqualified-confabulation label.

### M14. Definition/attribute sentences without listed cues

Type: pattern.

Operation: Among deterministically segmented sentences containing M09 or M10, count those with no selected cue match in that same sentence.

Question: How much locally unmarked descriptive-looking syntax occurs?

Limit: A disclaimer in another sentence can govern it; label this absence of same-sentence cues, not absence of qualification.

### M15. Definition/attribute sentences with listed cues

Type: pattern.

Operation: Count sentences containing M09 or M10 and a selected cue, retaining each cue family separately.

Question: How often do descriptive-looking syntax and qualifiers coexist?

Limit: Co-occurrence is not proof that the qualifier governs the trait statement.

### M16. Sequence of sentence-level patterns

Type: pattern.

Operation: Give each sentence a vector of observed pattern/cue indicators; summarize transitions and lengths of consecutive matching or nonmatching runs.

Question: Does the response change its surface style as it proceeds?

Limit: These are pattern transitions, not demonstrated shifts in belief or semantic stance.

## Amount and structure of the response

### M17. Response size

Type: direct.

Operation: Count raw characters and normalized words using a frozen tokenization rule.

Question: How much text does each condition elicit?

Limit: Length is not substantive engagement or quality.

### M18. Sentence shape

Type: direct.

Operation: Record sentence count, mean words per sentence, and maximum sentence length under a fixed splitter.

Question: Does framing alter how compact or extended the writing is?

Limit: Segmentation is approximate for headings, fragments, abbreviations, and lists; not a reading-grade claim.

### M19. Document structure

Type: direct.

Operation: Count Markdown headings, list items, and paragraphs using documented structural rules.

Question: Does it produce an encyclopedia-like entry, a list, or a short conversational response?

Limit: Formatting counts alone cannot establish genre.

### M20. Question marks

Type: direct.

Operation: Count literal question marks and their locations.

Question: How often does the answer visibly ask questions?

Limit: Question marks include rhetorical or quoted questions and are not all requests for information.

### M21. Self and user references

Type: lexicon.

Operation: Count fixed first-person and second-person pronoun inventories, separately, with a declared treatment of contractions.

Question: Does the language focus more on the assistant or the interlocutor?

Limit: A count does not establish social intent or a pronoun’s referent inside a quotation.

### M22. Target repetition and prompt-word overlap

Type: direct.

Operation: Record exact normalized target mentions; separately compute response overlap with the prompt’s content words under a frozen function-word exclusion list.

Question: Does the response repeat the target or prompt framing?

Limit: Shared words are not proof of premise acceptance. Keep target repetition separate from the overlap value.

### M23. Numbers and measurement forms

Type: pattern.

Operation: Count numeric strings, number words if included in a frozen list, and number-plus-unit patterns.

Question: How often does it add quantitative-looking detail?

Limit: Numbers can be list labels, years, or quoted text, and do not establish grounded specificity.

### M24. Source and citation forms

Type: pattern.

Operation: Count URLs, DOI-shaped strings, defined author/year patterns, and a separate frozen inventory of attribution phrases such as 'according to'.

Question: Does it introduce source-like material or appeal to attributed information?

Limit: Neither existence nor accuracy of a source is verified by these counts.

## Repetition, vocabulary, and the supplied word

### M25. Within-response repetition

Type: direct.

Operation: Count repeated word trigrams and longer fixed-size word sequences, using declared overlap and denominator rules.

Question: Does it repeatedly recycle its own wording?

Limit: Repetition can be functional; it is not inherently poor quality.

### M26. Duplicate response rate

Type: direct.

Operation: Report raw exact duplicates and a separately defined case/whitespace-normalized duplicate rate within model × word × condition cells.

Question: Does the same prompt repeatedly produce the same text?

Limit: Normalization must be stated; distinct strings can still have the same meaning.

### M27. Same-prompt wording similarity

Type: direct.

Operation: Compute pairwise word-trigram Jaccard overlap within repeated trials of the same exact prompt, then summarize at cell level.

Question: How stable is the wording across repetitions?

Limit: Shared wording is not semantic agreement. Pairwise comparisons are dependent observations.

### M28. Reuse across different nonsense words

Type: direct.

Operation: Replace the supplied target with a placeholder under frozen matching rules; compare word-trigram overlap across different words within model and condition.

Question: Are different words receiving interchangeable wording or templates?

Limit: This tests surface reuse, not whether imagined entities are semantically identical.

### M29. Length-controlled lexical diversity

Type: direct.

Operation: Compute distinct word bigram/trigram ratios on prespecified equal-length prefixes, such as 50 and 100 words, with eligibility denominators reported.

Question: How varied is the vocabulary and phrasing among sufficiently long responses?

Limit: Shorter responses remain in the dataset but cannot enter that window’s statistic. Lexical diversity is not conceptual creativity.

### M30. Recurring motif vocabulary

Type: lexicon.

Operation: Count frozen vocabularies for motifs such as colors, iridescence, sounds, burrows, or size comparisons; preserve overlaps and individual term counts.

Question: Do particular recurring motifs dominate invented portrayals?

Limit: Selected motifs are a design choice. Negated or quoted matches still require cautious interpretation.

### M31. Category-associated vocabulary

Type: lexicon.

Operation: Count separate, overlapping inventories associated with animals, objects, and ideas, with prompts and target terms excluded from the response counts as specified.

Question: Does requested category shift the vocabulary used?

Limit: This is not a classifier of whether the response actually satisfies the requested category.

### M32. Word-repair suggestions

Type: lexicon.

Operation: Count a frozen inventory such as 'did you mean', 'misspelling', 'typo', and 'alternative spelling'.

Question: How often does the response visibly try to repair or reinterpret the supplied word?

Limit: Does not establish that an actual substitution occurred or that its alternative referent is real.

## Proposed priority

Collect a broad versioned feature table, but predeclare a small number of primary measurements and contrasts. My proposed initial six families are **M01, M02, M03, M04, M09, M13**: fiction expressions, qualification expressions, non-recognition, construction, target definition forms, and definition/cue order. This shortlist is a proposal, not a decision.

These jointly address how often answers use definition-shaped language and how explicit qualifying language accompanies it. They do not alone produce a valid semantic confabulation rate. Other families can support exploratory analyses and diagnostics.

Potentially informative combinations include:

- More definition-form matches under real framing, with fewer non-recognition matches.
- Similar cue prevalence but different cue placement.
- More locally unmarked attribute-form sentences despite the same whole-response any-cue rate.
- Strongly repeated wording across different nonsense words.
- Different category-associated vocabularies for the same nonce under different prompt categories.

These are questions to investigate, not predictions or findings.

## Measurement details to freeze before the main batch

1. Preserve raw responses. Score only response text, never concatenated prompts or metadata.
2. Specify Unicode normalization, apostrophe handling, case folding, tokenization, sentence splitting, and Markdown treatment.
3. Version every expression inventory and pattern. Record each match's raw-text span or an auditable mapping back to raw text. Preserve subfamilies instead of collapsing them into a single confidence number.
4. Record negation and quoted-text overlap where mechanically identifiable. Do not assume regex quotation boundaries or local negation windows resolve semantic scope.
5. For expression families, retain occurrence flags, counts, and matches per 100 words. Define overlapping-match treatment. Empty or failed outputs require explicit handling, not automatic zero-valued behavior scores.
6. Use null for an unobserved first cue, with a separate no-cue-observed indicator. Do not equate a cue-free response with a cue appearing at its end.
7. Retain API completion status, truncation, requested/returned model identifiers, usage, and errors. Observed prefixes can contain valid matches, but absence in a truncated prefix is not evidence of absence in a completed answer.
8. Report raw length as behavior. Use equal-length windows or matched-length comparisons as sensitivity analyses, with their eligible populations reported; do not silently discard short outputs.
9. For similarities, define the normalization, target masking, n-gram size, and empty-set behavior. Cells with fewer than two usable responses have no within-cell pair statistic.
10. Freeze analysis denominators, primary contrasts, and the handling of missing or incomplete records before examining the main new batch. No composite "truthfulness," "photographing," or "confabulation" score is proposed.

## Analysis without making 32 families into 32 headlines

- Apply identical scorers to historical and new responses, preserving historical settings that differ or are unknown.
- Report effect sizes and uncertainty for prespecified comparisons. Clearly identify exploratory results and address multiplicity when testing many contrasts.
- Keep word-level results visible. Repetitions under the same word, derived features from one response, and pairs sharing responses are not independent replications.
- Do not use pairwise similarity counts as the sample size for inference. Summarize at the prespecified cell/word level or use a dependence-aware analysis.
- Inspect whether results depend on length or a few frequent phrases. Narrow and broad inventories can be predefined for sensitivity checks rather than optimized after seeing the results.
- No new claims about hallucination, reality recognition, semantic category accuracy, or internal confidence follow from these surface measures alone.

## Basic software checks

Check documented operations using synthetic fixtures for apostrophes, negation, quotations, questions, headings, lists, abbreviations, empty text, and truncation. Verify that the same text and scorer version produce identical values.

For example, "It lives underground. It may eat insects." should contain both an attribute-form match and a qualification-expression match if those patterns are selected. "This is not fictional" still contains the string "fictional"; the record must not silently convert that lexical observation into positive acknowledgment of fiction.

These are checks of the software contract, not a semantic validation corpus. The user's earlier ratings are not an answer key for all 32 candidate families.

## Research grounding and limits

These sources inform limitations and established metric families. They do not validate this proposed Bestiary battery.

- Liu, J., Zong, Q., Wang, W., & Song, Y. (2025). [Revisiting Epistemic Markers in Confidence Estimation: Can Markers Accurately Reflect Large Language Models' Uncertainty?](https://aclanthology.org/2025.acl-short.18/) Their QA experiments found marker-based confidence associations unstable out of distribution. This supports keeping lexical markers separate from internal confidence claims.
- Szarvas, G., Vincze, V., Farkas, R., & Csirik, J. (2008). [The BioScope corpus: annotation for negation, uncertainty and their scope in biomedical texts](https://aclanthology.org/W08-0606/). The distinction between detecting a cue and identifying its scope is directly relevant; this is not evidence that a biomedical method will transfer to our responses.
- Tevet, G., & Berant, J. (2021). [Evaluating the Evaluation of Diversity in Natural Language Generation](https://aclanthology.org/2021.eacl-main.25/). Metric choice requires attention to the kind of diversity being measured.
- Liu, S., Sabour, S., Zheng, Y., Ke, P., Zhu, X., & Huang, M. (2022). [Rethinking and Refining the Distinct Metric](https://aclanthology.org/2022.acl-short.86/). Their analysis identifies length bias in ordinary distinct scores. Our proposed fixed-length comparisons are a design choice, not an implementation of their expectation-adjusted metric.
- Zhang, T., Peng, B., & Bollegala, D. (2025). [Evaluating the Evaluation of Diversity in Commonsense Generation](https://aclanthology.org/2025.acl-long.1181/). Their evaluation illustrates that form-based diversity can differ from content diversity. Our overlap metrics should be reported as wording diversity or reuse.

## Still open

The final battery, expression inventories, patterns, normalization, priority shortlist, and exact estimators all require specification. The model lineup, sample, and spending stop are decided in the [sample design](sample-design.md). This document expands the proposal; it does not initiate implementation or paid runs.
