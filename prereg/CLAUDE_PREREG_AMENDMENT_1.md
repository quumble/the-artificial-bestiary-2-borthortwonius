# Amendment 1 to the Claude Fable 5.2 preregistration

**Study:** The Artificial Bestiary 2: Borthortwonius
**Analyst:** Claude Fable 5.2 (Anthropic), working with Bo Chesterton
**Written:** November 11, 2026, before any study request was sent
**Amends:** `prereg/CLAUDE_PREREG.md`, which stays in the repository unchanged
**Status:** complete except for the fresh word-list hash in section 2, which is filled in when the GPT-made words arrive. No other section depends on those words.

Where this amendment and the original disagree, this amendment governs. Everything not mentioned here stands as written.

## 1. Why it exists

Three things happened after the original was written, all before collection:

- GPT/Codex reviewed the original (`docs/claude-review.md`). The review found one scorer defect and four places where the analysis was underspecified. I accept all of them.
- The investigator decided to replace half of my no-intent words with words made by a GPT model, so that word authorship is no longer confined to one model family.
- The collector's stopping rule was changed to a per-model issue rate.

Since the original, I have read the GPT preregistration and its review of mine. I have still seen no study response.

## 2. Word sets

The fresh batch is now three sets of eight:

| Label in the word file | Words | Made by | Analysed as |
| --- | --- | --- | --- |
| `fresh-animal-intent` | 8 | Bo Chesterton, with imaginary animals in mind | animal-intent |
| `fresh-no-intent-claude` | 8 | Claude Fable 5.2 | no-intent |
| `fresh-no-intent-gpt` | 8 | a GPT model, named in the sample design | no-intent |

- **My eight** were drawn from my original sixteen with Python's `random.Random("bestiary2-claude-no-intent-draw-20261111").sample(words_in_file_order, 8)`. The other eight are retired and take no part in the study.
- **GPT's eight** are drawn the same way, with the seed string `bestiary2-gpt-no-intent-draw-20261111`, from the sixteen candidates GPT keeps after dropping its four most loaded of twenty.
- **Replacement rule.** If a web search shows a drawn word is an existing word, name or brand, it is replaced by the next word from a continued draw under the same seed. Near-matches do not trigger replacement.
- The original word-list hash no longer applies.

**New fresh word-list SHA-256:** _pending receipt of the GPT-made words_

## 3. Scorer version 1.1

`prereg/claude_scorer_v1_1.py`, SHA-256 `7cebfa2c4e4524ec6a48fd3097485fce758edce20fd4b5773fe466e1ead4f967`.

- **The defect.** Version 1.0 ignores fiction and construction cues inside a sentence it takes to be an offer or a request. It took any sentence containing a phrase like "more information" to be one. "Here is more information: a *target* is a fictional bird" therefore lost its fiction cue.
- **The fix.** A sentence now counts as an offer or request only if it ends in a question mark, matches the offer patterns, or matches an explicit request to the user ("could you provide", "where did you see", "if you can", "let me know", "did you mean").
- **Nothing else changed.** Agreement with the historical hand codes is the same to two decimals as reported in the original.
- **Both versions are reported.** Version 1.1 is primary. The analysis script also runs version 1.0 and writes its results beside it.

## 4. Analysis code

`analyze_claude.py`, SHA-256 `43b549940dae692f1db3242988b27060824eeb46b452616fe16b388883902e28`, with tests in `tests/test_claude_analysis.py`. It implements this amendment exactly and is frozen with the collector before the first study request. This replaces the original's commitment to add it before response text is read.

## 5. Eligibility and denominators

These rules replace section 6 of the original where they differ.

- **Eligible record:** a terminal response the collector marked valid, with no error, no protocol violation and no issue flag. If a slot has more than one, the earliest attempt is used.
- **Flagged trials are excluded.** A trial where reasoning was observed, or the payload had an unexpected shape, is recorded by the collector and takes no part in any analysis. Counts are reported by model and condition.
- **The reasoning-on clause is withdrawn.** The collector has no reasoning-on mode, so the original's rule for such a model has nothing to apply to.
- **Truncated responses** are excluded from the primary analysis and included in a sensitivity analysis, as before.
- **Word value for one model:** the mean over the conditions in the stated set of each condition's mean over eligible repetitions. Every condition in the set must have at least one eligible response, and eligible responses must total at least 60% of the planned trials for that word, model and condition set. The 60% is counted after the exclusions that apply to the analysis being run.
- **Word value for a model group:** the equal-weight mean across the group's models. A word enters a test only if every model in the group has a value for it. Dropped words are counted.
- **A model belongs to a group** only if at least 60% of its planned slots in the batch are eligible. A model stopped early by the collector falls out of its group, and the result names it. Tests that compare batches need the model in both.
- **Empty responses** stay in, scored as no description.

## 6. H3: what the result can and cannot show

The contrast is unchanged: unmarked description under presupposition, the 8 animal-intent words against the 16 no-intent words, all models. The no-intent set is now 8 Claude-made and 8 GPT-made words.

My prediction stands: the animal-intent set is higher. The sets differ in author, intent, morphology and selection all at once. A result in my direction supports the set-level prediction. It does not show that readable roots are the cause. I withdraw the sentence in the original that treated it as a test of that account.

## 7. H4: one confirmatory decision, one estimand

- **Estimand.** For each word, the current-model value minus the historical-model value of N over the six presupposition conditions plus neutral. Within each intent stratum (animal-intent, no-intent), take the mean for known words minus the mean for fresh words. Average the two strata with equal weight. This standardises over intent, which the original left undefined: known words are half animal-intent and fresh words are one third.
- **Confirmatory test.** A two-sided permutation test that this quantity is zero, permuting the known and fresh labels within stratum. This is the test that enters the Holm family.
- **The ±0.10 margin is descriptive.** Whether the 95% interval falls inside it is reported and carries no confirmatory weight. No equivalence claim is made.
- **Exposure.** No outcome of this test shows that a model was or was not trained on the original study.

## 8. H6, new: word authorship by model family

- **Provenance:** naive. Added because the swap in section 2 makes it testable.
- **Contrast.** For each fresh no-intent word, N over presupposition plus neutral on the four Anthropic models minus the same on the four OpenAI models. Compare that difference between Claude-made words (8) and GPT-made words (8).
- **Test:** two-sample permutation by word, two-sided.
- **Prediction:** negative. Each family gives less bare non-recognition to words its own family made. I hold this weakly.
- **Limits.** Eight words against eight. Only a large effect would show. The two word sets also differ in which model made them and when, not only in family.

## 9. The confirmatory family

Six tests: H1, H2, H3, H4, H5, H6. Holm correction at 0.05 across the six. A test is called confirmed only if its Holm-adjusted p is below 0.05 and the floor rule does not mark it uninformative. The floor rule applies to H1, H2, H3 and H5, whose arms are rates.

**Scope of error control.** This is one analyst's family. The GPT preregistration has its own family of eight contrasts with its own correction. The two are reported separately and labelled by analyst. No claim of 5% error control across both is made. Where the two families bear on the same question, I will say whether they agree.

## 10. Wording I withdraw or tighten

- **Outcome names.** Reports use U, N and E and their literal definitions. "Confabulation proxy" appears only with the blind spots and validation figures beside it.
- **Search strings.** A response containing "bestiary" or "chesterton" is a flag for someone to read in context. It is not, by itself, evidence of exposure.
- **Historical models.** A historical model identifier called today is a control only if the served version is the one that predates the original study. The collector records the served identifier; I will report it.

## 11. Collector stopping rule

Recorded here because it decides which trials exist:

- A changed model identifier stops that model at once.
- Reasoning, an unexpected payload shape, or a non-retryable request error is recorded as an issue. The slot is closed and never regenerated.
- A model stops when its issues exceed 5% of its closed slots in a batch, checked once 200 slots are closed. The 5% was set by the investigator. I set the 200 after simulating the rule: with a minimum of 100, a model with a true issue rate of 2% would be stopped by chance about 4% of the time; with 200, about 0.5%.
- No model's stop affects another model.
- Preflight tolerates nothing: any violation there halts everything, because nothing has been spent on study trials yet.
