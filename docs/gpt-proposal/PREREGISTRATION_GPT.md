# The Artificial Bestiary 2: Borthortwonius
## Independent GPT preregistration proposal, version 1.0

Prepared November 10, 2026, America/New_York. Investigator: Bo Chesterton. Independent drafting analyst: ChatGPT/Codex, OpenAI. The exact backend model identifier was not exposed to this drafting workflow and is not guessed here.

**Status:** A complete independent proposal for adoption before collection, not an assertion that a registry submission, investigator approval, executable scorer, or collection freeze has already occurred. The accompanying review identifies launch blockers. The primary analysis, measurement appendix and inventory file form one specification. Preserve this independent version when comparing it with Claude's proposal. A reconciled protocol must identify any differences and be timestamped before collection.

## 1. Provenance, independence and prior knowledge

The reviewed source is [quumble/the-artificial-bestiary-2-borthortwonius at c00aab0e9902ee000b2e9d256dcf09b20c21c823](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/tree/c00aab0e9902ee000b2e9d256dcf09b20c21c823). The supplied archive's embedded commit identifier matches GitHub's main branch at review time. The runner and sample-design files fetched through GitHub match the archive byte for byte. `SOURCE_MANIFEST.json` records source hashes.

The analyst read the README, sample design, evaluation draft, measurement catalog, calibration log, known-word file and collection runner. The calibration log contains historical excerpts and earlier judgments. This is therefore informed by prior work, not a claim of complete ignorance of historical outcomes. The analyst did not inspect a separate Claude preregistration, the withheld fresh-word file, or new study responses. Public provider documentation was consulted for API interpretation and model metadata. All execution in this review used dry runs or synthetic offline fixtures. No real model API calls were made.

The investigator and repository describe the study as pre-collection. No study data were present in the supplied snapshot. This does not independently audit files or calls elsewhere. This proposal requires freezing the protocol and scorer **before the first study completion**, which is stricter than the sample-design sequence allowing scorer finalization after unread fresh collection.

## 2. Research questions and interpretive boundary

The experiment asks how a fixed set of language-model endpoints describe unfamiliar fabricated words when the prompt calls the referent real, imaginary, or a type of animal, object or idea, and under a neutral prompt. It measures expression use, definition-shaped syntax, wording, length and structure. The principal causal manipulation is prompt wording within each word and endpoint, under the recorded collection conditions.

The primary question is whether imaginary and type-of framing differ from real framing in four explicitly mechanical outcomes. Secondary questions concern category effects, wording order, source-set associations, endpoint differences, repeated wording, and the historical known-word set.

The five agreed interpretive rules remain in force. Fiction signals can occur in a narrated setting. A final whole-description disclaimer can qualify earlier prose. Local hedges do not erase other assertions. Explicitly imaginary prompts license fiction. Ambiguity and incompletion are not automatic negative semantic labels. No routine human or LLM judge is used. The mechanical battery does not implement semantic scope or factual support judgments, and it does not output a confabulation, truthfulness, knowledge, confidence, substantive-description or category-correctness score.

The estimands concern these words, prompts, endpoints and sampling settings. Models are deliberately selected, and words are deliberately constructed. Neither is a probability sample of all models or all possible nonsense words.

## 3. Fixed design and intended sample

| Batch / source set | Words | Repetitions per word × condition × model | Trials per model | Trials across eight models |
| --- | ---: | ---: | ---: | ---: |
| Fresh, human animal-intent | 8 | 5 | 400 | 3,200 |
| Fresh, model no-category-intent | 16 | 5 | 800 | 6,400 |
| Known, human animal-intent | 4 | 10 | 400 | 3,200 |
| Known, analyst no-category-intent | 4 | 10 | 400 | 3,200 |
| Total | 32 | Batch-specific | 2,000 | 16,000 |

There are ten conditions per word: neutral, and the 3 × 3 crossing of reality frame (`real`, `imaginary`, `type of`) with category (`animal`, `object`, `idea`). Neutral has no category or reality level and is not duplicated into nine factorial cells.

The fresh-word file is committed by the repository's SHA-256: `ba900e410b907a8dc02cab7835a3aaace5473eea72402d40b5f4b0ad209209e3`. It remains withheld until both batches finish or are formally stopped. Before collection verify its exact bytes, 24 unique words and the 8/16 assignment. This analyst could not perform that private-file check. Do not replace words because they appear suggestive, receive search near-matches, or elicit unexpected responses.

Known animal-intent words: borthorpunius, halthibinny, purtaneolotomous, wresanthamulf. Known no-intent words: flembrast, kovashent, plindorf, trolnique. Their supplied file SHA-256 is `ee338d944aa0c6e2de68ce18c8a38af1eb3de34790ab87828f2afe6f9eb0dfe2`.

Source, author, intent, word length, morphology and selection procedure are not independently randomized. Fresh no-intent words were selected from 20 candidates after four were dropped. The two source sets are compared as compound stimulus sets, never as a clean causal effect of human versus model authorship or animal intent.

### Prompt strings

Neutral: `Describe {article} {word}.`

Factorial: `Describe {article} {word}. It is {frame_article} {reality} {category}.`

`article` is `an` iff the first letter of the word, lowercased, is in `aeiou`; otherwise `a`. `frame_article` is `an` for imaginary, `a` for real and type of. Preserve case and punctuation from the source word file. For example, the type-of construction is `It is a type of idea.` No additional system instruction, conversation history, tools, web search, self-classification request or forced output schema is supplied. Each trial is a new independent API request, with no previous-response reference.

### Models and target settings

| Provider | Requested identifier | Repository role | Intended reasoning control | Temperature |
| --- | --- | --- | --- | --- |
| Anthropic | claude-sonnet-4-6 | Historical | Off by documented default | 1.0 |
| Anthropic | claude-haiku-4-5 | Historical | Off by documented default | 1.0 |
| Anthropic | claude-sonnet-5-5 | Current | `thinking.type=between_tools`, no tools | Omitted |
| Anthropic | claude-haiku-5-5 | Current | `thinking.type=disabled` | Omitted |
| OpenAI | gpt-5.4-mini | Historical | `reasoning.effort=none` | 1.0 |
| OpenAI | gpt-5.4-nano | Historical | `reasoning.effort=none` | 1.0 |
| OpenAI | gpt-6-sol | Current | `reasoning.effort=none` | 1.0 |
| OpenAI | gpt-6-luna | Current | `reasoning.effort=none` | 1.0 |

The two historical OpenAI payloads also send `top_p=1.0`, matching the reviewed runner. Other unlisted generation controls are omitted. Keep default effort settings where the source design leaves them at defaults, and record those documented defaults. Omitted temperature is not described as an explicitly controlled temperature of 1.0. Vendor size labels are descriptive lineup pairings, not proof of equal parameter counts or capability.

The requested output cap is 1,024 tokens with reasoning disabled. Tokenization differs between models, so this is not a common word allowance. No 4,096-token reasoning allowance is allowed in the primary run. A 5,120-token total cap would not enforce a 1,024-token visible cap.

Run a content-neutral preflight (`Reply with the single word: ready.`) before study collection. Record every attempt, complete payload, returned model identifier, status, usage and cost. Accept a setting only if the response is valid and terminal and the requested controls comply with the table. A documented alias-to-snapshot resolution may be recorded and locked. Pin a version when supported, retaining the requested alias and actual endpoint identity in the manifest. Pause on a later unexpected returned identity.

If the table's setting is rejected, stop that lane. Do not silently choose reasoning-low, adaptive-default, or a different model. A documented parameter omission that preserves reasoning-off behavior may be adopted only as a timestamped pre-collection amendment specifying the exact payload. An unavailable model is recorded as unavailable. It is not replaced, and an eight-model pooled result is then unavailable unless the entire design is amended before collection. Observing no reasoning on one trivial preflight is not by itself evidence that an unspecified default disables reasoning on study prompts.

## 4. Collection order, stopping and retries

Collect fresh first, known second. Neither batch's outputs or feature summaries may change the other's stimuli, settings or analysis. Within each model and batch, retain the runner's shuffled list with Python `random.Random(f'{20261110}|{batch}|{model_id}').shuffle(order)` applied to the source word-file order, condition order neutral followed by realities real/imaginary/type-of and categories animal/object/idea, and repetitions numbered from 1. Save the actual ordered trial manifest and Python version. The seed fixes scheduling, not model output randomness. Two workers per model may execute that order concurrently; completion order need not match dispatch order. One collector process at a time is permitted.

Target all 16,000 planned slots. The sample is budget-limited, not power-derived. No minimum detectable effect or assurance of adequate statistical power is claimed. Spending stops at **$20 per provider across preflight, both batches and retries**, or earlier if the conservative ledger cannot authorize the next request. No stopping based on wording, effect sizes or statistical intervals. No extra repetitions or replacement words after inspecting outcomes.

Use a durable per-attempt ledger with current documented pricing, all known charges, in-flight reservations and conservative reservations for requests whose billing is unknown after timeout. Before dispatch, require spent plus reserved plus the next request's upper-bound cost to be at or below $20. Validate the input-token bound; the current runner's assumed 200 input tokens is not a formally verified maximum. Reconcile provider billing when possible. Label the ledger an estimate and report any discrepancy. Do not silently release an ambiguous request's reservation or count a failed transport as necessarily free. No higher `--spend-cap`, reduced-repetition shortcut or unreported trial limit is authorized by this proposal.

Retain up to six attempts per trial **across restarts**, retrying only transient transport failures or the reviewed statuses 408, 409, 425, 429, 500, 502, 503, 504 and 529. Authentication failures pause the lane immediately. Nontransient request errors do not trigger a settings change. Preflight may try up to four times for transient failures with the same compliant payload. The collection runner must retain each attempt rather than just the final attempt count.

Do not regenerate refusals, short answers, empty terminal answers, truncations or unexpected content. HTTP 200 is not sufficient evidence of a completed generation. A provider-reported failed generation may be retried only when its documented error is transient and within the same six-attempt limit. Preserve all attempts and any partial text. For duplicate terminal completions of one slot, select the earliest valid terminal payload by attempt order; retain all duplicates and charges. Failed partial text is not substituted for a terminal response. Interruptions can resume with the same frozen manifest and remaining attempt allowance. Once a provider reaches its budget stop, it receives no further study requests. The other provider may complete its scheduled slots within its own cap.

Budget stopping may leave faster or cheaper lanes better represented. Randomized within-lane order mitigates order imbalance but does not make budget missingness random. Report the full completion grid. Do not fill empty cells with another model or increase budget to complete a favorable comparison.

## 5. Outcomes and hypotheses

The frozen inventory and preprocessing are specified in `inventories-gpt-v1.json` and `MEASUREMENT_SPEC_GPT.md`. All 32 families are retained. Four any-match indicators are primary: M01 fiction expressions, M02 qualification expressions, M03 non-recognition expressions, and M09 exact-target definition forms. M04 construction expressions and M13 definition/cue order are key secondary measures. Remaining families are prespecified descriptive/exploratory measurements.

For each primary outcome there are exactly two fresh-batch contrasts:

1. Imaginary minus real, averaged equally across the three categories.
2. Type of minus real, averaged equally across the three categories.

This yields eight primary estimates, not separate confirmatory tests for every model, phrase, category and word. The directional expectations are more M01, less M03, and more M09 under imaginary than real framing. M02 and all type-of contrasts have no directional prediction. All interval comparisons are two-sided. M01 can increase through literal repetition of the prompt's word `imaginary`; that is still expression behavior, not evidence of private reality recognition.

No outcome combines cue absence and definition presence into a confabulation score. M13's `definition_only` state means that the selected cue inventory did not match, not that the model asserted a real referent without qualification.

## 6. Analysis population and incomplete outputs

The slot key is batch × requested endpoint × word × condition × repetition. Audit keys against the frozen trial manifest. Preserve invalid records in an audit table and exclude them from behavioral analysis: wrong prompt, wrong word-set label, unapproved settings or endpoint, nonterminal failure, corrupt payload or duplicated slot beyond the retained completion. Report each reason and count. Do not exclude for length, apparent nonsense, disagreement with an expectation, source claims, language, or perceived quality.

**Primary estimand:** occurrence of the listed feature in the visible text actually returned for a valid terminal trial. Include nonempty refusal text and nonempty truncated or content-filtered prefixes, carrying their completion flags. A zero on a truncated prefix means no match in observed text only. It is not a completed-response negative label. Include nonempty punctuation-only text for any-match outcomes; density is null when W=0. Empty/whitespace-only terminal responses, failed trials, unavailable endpoints and uncollected slots have null behavioral outcomes and separate operational counts. Never encode them as no-match responses.

For OpenAI retain response status, error and incomplete reason plus typed refusal content. For Anthropic retain stop reason and relevant stop details. Treat ordinary terminal endings and explicit refusals as terminal; treat output-cap endings as truncated; preserve any other incomplete reason separately. Unknown status schemas pause the collector for documented resolution, rather than being called successful.

Every table reports planned slots, attempts, retained terminal responses, usable nonempty responses, complete usable responses, cap truncations, other incompletions, empty responses and errors. The repository's tripwire is applied within **batch × model × condition**, with cap-truncated valid terminal responses divided by all valid terminal responses, including empty terminal responses. If the proportion is strictly greater than 1%, flag every report using the cell. Also display the corresponding rates by word set. A triggered flag never silently changes caps, denominators or inclusion rules.

## 7. Primary estimators and uncertainty

For outcome k, compute each model × word × frame × category cell's mean over its usable repetitions. Compute the imaginary-minus-real or type-of-minus-real difference within each category, then average the three differences equally. Average these word-level differences equally within each of the two fresh source sets. Give the sets equal one-half weight, despite their 8/16 sizes. Finally average the eight model estimates equally. Report effects in percentage points.

In notation, with cell means p and n_s words in set s:

`Delta_k(A-real) = (1/8) sum_m (1/2) sum_s (1/n_s) sum_w (1/3) sum_c [p(m,w,A,c,k) - p(m,w,real,c,k)]`.

The pooled estimand gives equal weight to provider and historical/current role because each has the same number of selected models. It is an average of these eight endpoints, not a general vendor ranking. Display all model-specific and source-set effects beside the pool, so opposing effects are visible.

If any cell needed for a primary pooled contrast has zero usable repetitions, that pooled contrast is **not estimable under the complete-panel definition**. Report its missing cells and bounds, and report estimable per-model/set components. Do not renormalize the primary pool over whichever cells happened to finish. A separate available-panel descriptive estimate may be labelled as such. If cells have one to four rather than five usable repetitions, retain their observed cell means but report the imbalance and the missing-slot sensitivity below.

Use a stratified paired word-cluster bootstrap for uncertainty: sort words within source set; with NumPy `Generator(PCG64(20261111))`, draw 8 animal-intent word indices and 16 no-intent indices with replacement for each of 50,000 resamples. Carry all models, conditions and repetitions of each drawn word together. Use the same resampled words for all eight primary estimates. Do not resample responses or pairwise similarities as independent words, and do not resample the fixed model list. This bootstrap describes sensitivity to the observed word bank and does not establish random-sample generalization or exact frequentist coverage.

Report ordinary 95% percentile intervals and Bonferroni-adjusted **99.375%** intervals for the family of eight primary estimates, using linear quantile interpolation (tails 0.003125 and 0.996875 for adjusted intervals). Reserve confirmatory directional statements for adjusted intervals excluding zero. Do not use ordinary 95% intervals from model-specific or secondary tables as additional confirmatory discoveries. Report degenerate bootstrap distributions explicitly; a zero-width interval from identical observed word effects is not proof of no sampling uncertainty and does not support a confirmatory claim. All eight estimates are shown regardless of direction or interval width. No p-values are required.

### Prespecified sensitivity analyses

- **Missing-slot bounds:** within each planned five-slot cell let a be the number of observed positive matches, n the number of usable observed responses and R=5. The observed-text planned-slot rate lies in `[a/R, (a+R-n)/R]` without assumptions about missing outcomes. Difference bounds are lower-A minus upper-real and upper-A minus lower-real, aggregated with the same positive weights. These bounds are not confidence intervals. Apply them even if a primary point estimate is non-estimable.
- **Completion bounds:** for a hypothetical uncensored continuation, treat any observed match as fixed 1, complete observed no-match as fixed 0, and truncated/otherwise incomplete no-match plus missing outcomes as unknown [0,1]. Report separately from the actual-returned-text estimand. This is a descriptive sensitivity, not a claim about what a model would have produced under a changed cap.
- **Complete-only:** repeat primary point estimates using complete, nonempty terminal outputs. Show new denominators and non-estimable cells. This is a selected-response sensitivity, not automatically less biased.
- **Length:** repeat feature prevalence in the first 50 and first 100 words among responses at least that long, with eligibility by condition. Never pad shorter responses or silently remove them from the main result. Do not adjust the primary contrast for response length, which may itself be affected by framing.
- **Inventory:** repeat M01 without `imaginary`, and M02 using its modal subfamily only. Retain all primary inventories unchanged. Compare quoted/local-negation flagged match prevalence descriptively without pretending those flags resolve scope.
- **Weighting/influence:** report the alternative fresh-word 8:16 weighting and leave-one-word-out versions of the primary point estimates. No post hoc removal of influential words.

If adjusted intervals exclude zero but missing-slot bounds include zero, explicitly qualify the result as conditional on the observed responses and sensitive to missing outcomes. Sensitivities do not create a second set of confirmatory tests.

## 8. Prespecified secondary and exploratory analyses

Report all ten conditions for each model and source set, including neutral. For each primary outcome, compare each frame's category-averaged value with neutral; these are secondary differences because neutral has no category. Report animal/object/idea contrasts within each frame, and source-set differences and their frame interactions. Use the measurement appendix's denominators and aggregation for all remaining features. M04 and M13 receive highlighted descriptive tables but no extra confirmatory status.

Report four endpoint pairings: Sonnet 5.5 minus Sonnet 4.6, Haiku 5.5 minus Haiku 4.5, GPT-6 Sol minus GPT-5.4 mini, and GPT-6 Luna minus GPT-5.4 nano. Show changes in the two primary framing effects and each condition's primary rates. These are selected-endpoint comparisons, not a controlled estimate of model age, size, training method or provider quality.

The new known-word batch is a separately planned replication on eight public words. Apply identical measurement code and report its two framing contrasts for every primary outcome, weighting the two four-word sets equally. Repetitions do not turn those eight words into 6,400 independent stimuli. A known-batch bootstrap, when shown, resamples four words per set with seed 20261112 and 50,000 draws, preserving all models and conditions. Its intervals are descriptive, without a second confirmatory success criterion.

Compare newly collected known and fresh batches within source set, then equally across sets, for each endpoint and condition. Compare the known-minus-fresh contrast across the four endpoint pairs above. These differences combine word identity, morphology, source/selection details, collection time and possible exposure. Even an interaction between model generation and word batch cannot isolate training-data contamination. Knowledge cutoffs are metadata, not proof that a specific file was included in or excluded from training. Historical endpoints are helpful controls only to the extent their served versions are genuinely comparable to their earlier versions.

Existing historical raw responses are not part of the primary or new-known denominators. Any comparison against the original repository is exploratory, uses the same frozen scorer, and must first publish a source-file manifest explaining any overlapping re-coded files. Count each original generated response once, not once per CSV coding version. Keep original prompts, settings, caps, dates and missing metadata explicit. Historical labels and calibration judgments are not validation ground truth for the new mechanical scorer.

All analyses outside the eight primary contrasts are descriptive or exploratory. No uncorrected significance claims across the 32 families. Any later formal hypothesis testing, alternate lexicons, human annotation, LLM judging, semantic scoring, or selected exemplar analysis is a separately versioned post-registration analysis. Illustrative excerpts cannot substitute for the full feature tables.

## 9. Freeze, release and deviations

Before the first study request, commit this adopted protocol, its appendices, tested scorer and analysis code, exact request payloads, ordered trial manifest, source/word hashes, runtime/dependency versions, provider pricing metadata, and attempt-ledger implementation. Resolve the collection defects identified in `REVIEW_GPT.md`. Preserve the baseline commit and amended launch commit separately. The current review leaves the supplied repository unchanged.

During collection, operational checks may inspect statuses, counts, returned model IDs, usage, spend and payload integrity. Do not inspect study response text, feature rates or effect estimates. Record any accidental text exposure, who saw it, when, and whether it preceded a protocol change. Content-neutral preflight outputs and synthetic fixtures are allowed before freeze.

After both batches finish or are formally stopped, publish the exact fresh-word file and verify its committed hash. Release the trial manifest, all retained raw outputs, attempt logs with secrets removed, completion/exclusion tables, scorer and inventories, feature/match-span tables, analysis script and environment versions. Keep raw outputs immutable. Report every primary estimate, unavailable result and deviation. Do not publish credentials or authorization headers.

Amendments before collection state their reason and timestamp. Changes after collection begins, even if outputs remain unread, are labelled post-collection amendments with the extent of data access disclosed. Changes after response inspection are exploratory unless they are a strictly documented software correction, in which case retain original and corrected results where possible. Comparing the two independent preregistrations is design work; choosing between them after observing outcomes is not.

## Companion files

- `MEASUREMENT_SPEC_GPT.md`: exact preprocessing, all 32 feature families and fixture contract.
- `inventories-gpt-v1.json`: closed expression inventories and suffix lists.
- `REVIEW_GPT.md`: independent source review, demonstrated bugs and launch requirements.
- `offline_review_checks.py` and `offline-review-results.json`: reproducible synthetic probes of the baseline collector.
- `SOURCE_MANIFEST.json`: reviewed source hashes and baseline commit.
- `SHA256SUMS.txt`: integrity checks for this delivered proposal package.

## Amendment 1: balanced word sources and analysis weights

**Written:** November 11, 2026, 12:27 EST (17:27 UTC). **Analyst:** GPT/Codex. **Stage:** pre-collection, following the investigator's explicit approval of equal source weights. This append-only note supersedes the conflicting passages above. The original body is preserved, as are the measurement specification and inventories. Since the original, I have read Claude's preregistration and amendment. This review used public source files and synthetic fixtures, with no private fresh-word file, study response inspection or provider API calls.

**Word bank.** The fresh bank is eight Bo-authored animal-intent words, eight Claude-authored no-intent words and eight GPT Temporary Chat-authored no-intent words. The file labels are `fresh-animal-intent`, `fresh-no-intent-claude` and `fresh-no-intent-gpt`. All 24 words still receive ten conditions, five repetitions and eight endpoints: 9,600 fresh slots, with 6,400 known slots separately. The superseded fresh-file hash in section 3 must not be used for the revised bank. Its final bytes, generation/selection record and replacement hash remain pending and must be fixed before freeze. Source, intent and selection remain confounded.

**Primary weighting.** Each fresh source contributes exactly one-third. Words within source, categories and endpoints retain equal weights. With eight words per source, each fresh word therefore has equal influence. This promotes the previously specified equal-word sensitivity to primary status. The original equal-intent weighting becomes a descriptive sensitivity: one-half Bo, one-quarter Claude and one-quarter GPT. Both estimates and their missing-slot/completion bounds are reported. No favorable weighting is selected after observing results.

**Uncertainty and missingness.** Bootstrap whole words separately within the three source groups: eight Bo, eight Claude and eight GPT draws with replacement per resample, carrying all models, conditions and repetitions together. Sort groups and words lexicographically, and retain PCG64 seed 20261111, 50,000 draws and the original interval rules. Use the same resampled words for the alternative weighting, whose intervals are descriptive. Apply the primary weights to all primary bounds, completion/length/inventory sensitivities, within-batch endpoint comparisons and leave-one-word-out estimates. Leave-one-word-out diagnostics retain each source's fixed one-third weight. A missing required cell still makes the full primary contrast unavailable; never redistribute weight to surviving words or models.

**Known-word comparisons.** The known batch retains equal weights for its two four-word intent groups. Direct known-minus-fresh comparisons retain a common one-half animal-intent and one-half no-intent weighting in both batches, with Claude and GPT equally represented within fresh no-intent. Report that standardized comparison separately from the fresh primary average.

**Collection amendment.** Adopt the documented per-model study stopping rule: identity change stops that model immediately; reasoning, schema and non-retryable request issues close their slots and remain excluded. Stop when issues exceed 5% of valid-or-issue closed slots in a batch once that denominator reaches 200. Retry-exhausted slots are separate missing observations, outside this issue-rate denominator. Stop decisions survive restarts, with already in-flight attempts retained. Preflight and accounting violations retain their stricter global stops. The existing budget, retry and outcome-blinding rules stand.

The four primary indicators, eight primary contrasts, 99.375% adjusted intervals, 32 measurement families and interpretive limits are unchanged. GPT and Claude remain separate analysis families, with no joint error-control claim. Claude's final choices and updated code commitment remain for Fable's review before the combined protocol is frozen.
