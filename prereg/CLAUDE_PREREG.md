# Preregistration: Claude Fable 5.2

**Study:** The Artificial Bestiary 2: Borthortwonius
**Analyst:** Claude Fable 5.2 (Anthropic), working with Bo Chesterton
**Written:** November 10, 2026, before any study response was collected
**Written from:** repository commit `c00aab0e9902ee000b2e9d256dcf09b20c21c823`, received as a zip of `main`
**Frozen scorer:** `prereg/claude_scorer.py`, SHA-256 `7244846fd96c884aa322d5b4d3a5c242dc048c67d825ceb94a03bf1a21fabd95`
**Fresh word list:** SHA-256 `ba900e410b907a8dc02cab7835a3aaace5473eea72402d40b5f4b0ad209209e3`

This document fixes my measures, hypotheses, tests, and exclusions. It was written without sight of the GPT analyst's preregistration.

## 1. What I have and have not seen

Following the project's practice of recording where a hypothesis comes from, each hypothesis below is labelled **naive**, **prior-informed**, or **replication**. My position is not naive, and this section says why.

- **I designed parts of this study.** I proposed the fresh-word arm, the 1,024-token cap, and the model lineup, generated the sixteen no-intent words, and wrote the collection runner.
- **I have read historical response text.** While building the scorer I read excerpts from the original study's hand-coded files, and I computed base rates on its raw responses. The numbers are in section 4.
- **I have seen no response from this study.** The runner has only been exercised against a local stand-in server that returns placeholder text.
- **I have not seen training cutoffs for most of the lineup.** One report puts GPT-6.1 Sol's cutoff at April 30, 2026. I have nothing for the others.
- **Four of the eight models are Claude models, and I am one.** Scoring is done by frozen code, so my judgment does not enter any trial-level label. It does enter the choice of patterns, made before collection.

## 2. Design, as fixed in the repository

I take the sample design as given: 24 fresh words (8 animal-intent, 16 no-intent), 8 known words (4 and 4), ten conditions per word, eight models (two historical and two current per provider), reasoning off, a 1,024-token visible cap, five repetitions for the fresh batch and ten for the known batch.

Terms used below:

- **Presupposition conditions:** the six conditions that assert the word names something (`real_*` and `type_of_*`).
- **Imaginary conditions:** the three `imaginary_*` conditions.
- **Historical models:** claude-sonnet-4-6, claude-haiku-4-5, gpt-5.4-mini, gpt-5.4-nano.
- **Current models:** claude-sonnet-5-5, claude-haiku-5-5, gpt-6-sol, gpt-6-luna.

## 3. Measures

All measures come from `prereg/claude_scorer.py`. It reads response text only, lowercases it, strips markdown marks, and matches fixed pattern lists. The inventories are in the file and are part of this preregistration.

### Building blocks

| Flag | Mechanical definition |
| --- | --- |
| Description form | At least one un-negated definition form anchored on the exact target word ("a *target* is ..."), or at least two attribute-form matches ("it has", "native to", "used for" and similar). Matches inside questions are ignored. |
| Cue | Any match in four families: non-recognition, fiction vocabulary, construction ("let's imagine"), interpretation ("the name suggests"). Fiction and construction matches inside questions or offers are ignored, so "want me to invent one?" does not count. |
| Non-recognition | Any match in the non-recognition family. |

A bare modal such as "may" or "might" is counted separately and is **not** a cue. This follows agreed rule 3: a local hedge does not erase unrelated assertions.

### Three outcomes

| Outcome | Definition | What I will call it |
| --- | --- | --- |
| **U** | Description form present and no cue anywhere | Unmarked description |
| **N** | Non-recognition present and no description form | Non-recognition without description |
| **E** | Description form present | Description produced |

Under presupposition and neutral conditions the words are fabricated, so any description is unsupported. There, U is my proxy for confabulation in the sense of agreed rule 4. Under imaginary conditions U is not confabulation. It only records that a description carried no fiction vocabulary, which rule 4 treats as licensed.

**These are surface measures.** I will report them under the names above. I will not report U as "the confabulation rate" without the word "proxy" and the validation figures in section 4.

### Known blind spots

- **Substitution.** A response that silently swaps in a real word and describes that is not detected as such. In the historical data these mostly carry non-recognition language and land outside U.
- **Scope.** The scorer does not resolve what a cue qualifies. A fiction word anywhere marks the whole response.
- **Misspelled targets.** A definition anchored on a misspelling of the target does not count as a definition form.

## 4. How the scorer was developed

I wrote the patterns, compared the three-way output (unmarked description, marked description, no description) with historical hand codes, revised twice after reading disagreements, and stopped. Responses hand-coded as substitution were left out of the comparison.

| Historical labelled set | Responses | Three-way agreement | U precision | U recall |
| --- | --- | --- | --- | --- |
| Haiku 4.5, adjudicated hand codes | 198 | 0.91 | 0.94 | 0.84 |
| Haiku 4.5, full coded set | 789 | 0.91 | 0.94 | 0.82 |
| GPT-5.4 mini and nano, hand codes | 416 | 0.73 | 0.97 | 0.42 |

What this means for interpretation:

- **U is conservative.** When it fires it almost always matches a hand-coded unmarked description. It misses some.
- **It misses far more on GPT text than on Claude text.** Absolute U rates are therefore not comparable across providers, and I make no confirmatory claim that compares them.
- **Most Haiku disagreements are in imaginary conditions**, where the hand coders treated in-world fiction vocabulary as unmarked and the scorer, following agreed rule 1, treats it as a cue.
- **These sets were used for development.** They are not an independent validation. No held-out labelled data exists for this scorer.

Historical base rates under this scorer, which inform the predictions:

| Historical run | U, real | U, type of | U, imaginary | N, real | N, type of |
| --- | --- | --- | --- | --- | --- |
| Sonnet 4.6 retest | 0.00 | 0.00 | 0.42 | 0.96 | 1.00 |
| Haiku 4.5 | 0.07 | 0.10 | 0.70 | 0.76 | 0.82 |
| GPT-5.4 mini | 0.01 | 0.07 | 0.00 | 0.63 | 0.03 |
| GPT-5.4 nano | 0.13 | 0.09 | 0.09 | 0.47 | 0.25 |

## 5. Confirmatory hypotheses

Five tests form one family, corrected by the Holm method at a family-wise level of 0.05. The word is the unit throughout. A **word value** is the mean of an outcome over the relevant trials for one word, averaged with equal weight across the models in the stated group.

### H1. Imaginary framing produces more description than real framing

- **Provenance:** replication.
- **Contrast:** E in imaginary conditions minus E in `real_*` conditions, per fresh word, all eight models.
- **Test:** paired, 24 words.
- **Prediction:** positive, larger than 0.40.

### H2. On OpenAI models, "type of" draws less bare non-recognition than "real"

- **Provenance:** prior-informed. The historical GPT rates were 0.03 against 0.63 (mini) and 0.25 against 0.47 (nano).
- **Contrast:** N in `type_of_*` minus N in `real_*`, per fresh word, the four OpenAI models.
- **Test:** paired, 24 words.
- **Prediction:** negative, beyond −0.15.
- The same contrast on the four Anthropic models is reported descriptively. Historically it ran slightly the other way, and I predict no reliable difference there.

### H3. The two fresh word sets differ in unmarked description under presupposition

- **Provenance:** prior-informed, and deliberately set against the historical direction.
- **Contrast:** U over the six presupposition conditions, animal-intent words (8) against no-intent words (16), all eight models.
- **Test:** two-sample, by word.
- **Prediction:** the animal-intent set is **higher**.
- **Why this is a real test.** Historically the no-intent words drew more unmarked description than the animal-intent words. If intent were the cause, the same direction should hold here. I think the cause was readable roots: the historical no-intent set included words like a blend of two fishing terms. In the fresh sets it is the animal-intent words that carry readable roots, and the no-intent words were built to avoid them. So I predict the direction flips. A result in the historical direction counts against my account.

### H4. Known words are not treated differently from fresh words in a way that tracks model generation

- **Provenance:** naive as to outcome. I expect no exposure effect.
- **Contrast:** N over the six presupposition conditions plus neutral. For each word, take the current-model value minus the historical-model value. Compare that difference between known words (8) and fresh words (24).
- **Test:** two-sample by word, permuting within intent stratum (animal-intent, no-intent).
- **Prediction:** no difference. I set ±0.10 as the smallest difference I would treat as meaningful.
- **Reading the result:**
  - 95% interval inside ±0.10: consistent with no exposure effect of that size.
  - Interval excludes zero, with known words drawing *less* non-recognition on current models: evidence consistent with exposure.
  - Anything else: inconclusive, and reported as such.
- **Limits.** The historical models cannot have been trained on the original study, which is what makes them a baseline. Whether any current model was is unknown. The two batches run on different days; the contrast removes day effects shared across models but not ones specific to a generation. Known and fresh sets differ in size and in repetitions.
- This test requires the known-word batch. If it is not collected, H4 is reported as untested.

### H5. Current models produce less unmarked description under presupposition than historical models

- **Provenance:** naive.
- **Contrast:** U over the six presupposition conditions, current-model value minus historical-model value, per fresh word.
- **Test:** paired, 24 words.
- **Prediction:** negative, and small, because historical rates are already near zero.

### Test procedure

- **Paired tests:** sign-flip permutation test on the mean of per-word differences.
- **Two-sample tests:** permutation of word labels on the difference in group means.
- **Resamples:** 100,000 Monte Carlo permutations, seed 20261110. Two-sided p = (1 + count of permuted statistics at least as extreme) / (1 + 100,000).
- **Intervals:** 95% percentile bootstrap over words, 10,000 resamples, same seed. For H3 and H4, words are resampled within group.
- **Floor rule:** if an outcome's mean is below 0.02 in both arms of a contrast, I report the test and label it uninformative. A null at the floor is not evidence of no effect.
- The analysis script will be committed before any response text is read and must implement exactly this section.

## 6. Denominators and exclusions

- **Record used:** the latest record without an error for each trial.
- **Errors:** missing. A word needs at least 60% of its planned trials for a model to enter that model's value. Dropped words are listed.
- **Truncated responses:** excluded from U, N, and E in the primary analysis, because absence of a cue in a cut-off response is not absence in the full one. A sensitivity analysis includes them as scored.
- **Truncation tripwire:** any model-by-condition cell above 1% truncation is flagged in every table that uses it. If a cell entering a confirmatory test exceeds 5%, that test is also reported with the model removed.
- **Empty responses:** kept, scored as no description.
- **Reasoning:** if a model could only be run with reasoning on, or reasoning appears in more than 1% of its trials, it stays in the primary analysis and every confirmatory test is repeated without it.
- **Models that do not run:** groups are formed from the models that completed the batch. If a group loses a model, I say so beside the result. H4 and H5 need at least one historical and one current model.
- **No response is dropped for its content.**

## 7. Descriptive analyses

Reported with word-bootstrap intervals and no claim of confirmation:

- U, N, and E for every model and condition, and by category (animal, object, idea).
- Every confirmatory contrast, model by model.
- Definition and cue order, and how early the first cue appears.
- Response length in words. Tokens are not compared across model generations.
- Context requests and offers.
- Reality-assertion wording ("is a real", "was first described") inside unmarked descriptions under `real_*` conditions.
- A count of responses containing "bestiary" or "chesterton", with the matched trials listed. Any hit would be direct evidence of exposure.
- For the four historical models: the known-word batch against the original study's responses to the same words, scored with the same code. The original runs used lower caps and earlier dates, so this is a stability check and not a controlled comparison.

## 8. What I will not claim

- That U measures confabulation directly, or N measures a model's knowledge.
- That absolute rates are comparable between Anthropic and OpenAI models.
- That absence of an exposure effect shows the models were not trained on the original study.
- Anything about internal confidence, belief, or recognition.

## 9. Deviations

Any departure from this document will be listed in the analysis write-up with its date and reason. If the scorer has to change, the changed version gets a new version string, and results from both versions are reported side by side. Analyses added after response text has been read are labelled exploratory.
