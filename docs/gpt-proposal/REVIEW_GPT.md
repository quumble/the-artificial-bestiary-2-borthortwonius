# Bestiary 2: independent pre-collection review

Prepared November 10, 2026, America/New_York. Baseline: [c00aab0e9902ee000b2e9d256dcf09b20c21c823](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/tree/c00aab0e9902ee000b2e9d256dcf09b20c21c823).

**Recommendation: retain the experiment, fix the collector before running it, and freeze a narrower primary analysis inside the full 32-family battery.** The study can estimate how these prompts change observable language. It cannot, with this design and scoring, establish a general confabulation rate or isolate training-data contamination.

The supplied archive matches GitHub's baseline commit. No new study data were present. I did not read Claude's independent preregistration, retrieve the private fresh words, change the repository, or make a real model API call. The review used all eight supplied source files, current official provider documentation, a known-batch dry run and nine offline probes. Eight probes reproduce defects or missing guards; the ninth verifies trial construction. A successful probe means the observation was reproduced, not repaired.

## Collection defects to resolve before launch

### 1. Structured refusal text is silently lost

**High priority.** In [run_bestiary.py lines 214–218](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L214), OpenAI content is copied only when its type is `output_text`. A valid typed refusal carries its text in `refusal`. The offline fixture returns such a refusal and the runner stores `response=""`, `error=None`, `stop_reason="completed"`.

That loses exactly the kind of response behavior this study needs to retain. The raw payload is not saved elsewhere by the runner, so a later scorer cannot recover it from these JSONL records. Preserve the complete provider payload and extract visible refusal text separately, with a refusal-type flag. Join visible blocks with explicit boundaries so adjacent blocks cannot accidentally fuse words. See the [OpenAI Responses reference](https://developers.openai.com/api/reference/resources/responses/methods/create), which documents both output-text and refusal content types.

### 2. HTTP success is confused with generation success

**High priority.** [Lines 222–235](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L222) unconditionally set `error=None` for an HTTP-200 payload. A synthetic payload with `status="failed"` and a provider error is consequently treated as error-free. [Line 560](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L560) then marks it done on restart.

Validate the response schema and terminal status. Keep generation errors, incomplete reasons, refusal information and parse failures distinct. Do not regenerate valid refusals, empty terminal outputs or cap-truncated responses merely because they are unhelpful. The planned unit is one retained terminal outcome per slot, with separately logged transport retries.

### 3. Settings are saved but are not locked

**High priority.** [Lines 336–375](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L336) run selection again and overwrite `request-settings.json`, including when study files already exist. The offline probe demonstrates a different setting replacing an earlier one. Saved trials carry the setting name, but restarts do not enforce a common settings version.

Make the preflight result immutable once collection begins. Store the actual payload parameters, endpoint identity and a settings hash, not only a variant label. Require the saved manifest to match before resuming. A new setting should require a separate run identity or a documented protocol amendment.

### 4. Reasoning fallbacks contradict the stated design and cap

**High priority.** The variant lists in [lines 54–104](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L54) include adaptive/default or reasoning-low fallbacks. [Line 184](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L184) increases the request limit to 5,120 when one is selected. The offline probe confirms that payload.

An allowance of 4,096 does not reserve exactly that many tokens for reasoning. OpenAI documents `max_output_tokens` as the combined upper bound on visible and reasoning tokens. If reasoning uses fewer than 4,096 tokens, visible output can exceed 1,024. The fallback therefore changes both reasoning treatment and potentially available response length.

For the preregistration's primary run, fail closed when reasoning-off settings are unavailable. Do not call an accepted HTTP request proof that controls are equivalent. Sonnet 5.5's no-tools `between_tools` mode is documented and is not itself the defect. The defect is silently accepting a different treatment. See [Sonnet 5.5 overview](https://platform.claude.com/docs/en/models/sonnet-5-5/overview) and the [OpenAI output-limit definition](https://developers.openai.com/api/reference/python/resources/responses/methods/create).

### 5. Resume does not validate the trial's provenance

**High priority.** [Lines 556–566](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L556) skip any error-free stored trial with the same trial ID. The probe supplies matching IDs with `STALE PROMPT` and `STALE SETTINGS`; the runner makes zero replacement calls and treats the batch as done. This is not a recommendation to replace them automatically. It should stop and identify the mismatch.

The fresh-word loader [lines 239–257](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L239) computes a hash but does not compare it with the committed hash or validate the 8/16 composition. A one-word file with an unrecognized set label is accepted by the probe. Verify the hash and composition before any calls, and validate model, batch, prompt, repetitions, word set, payload and run hash on resume. Recording a hash in each session manifest provides an audit trail but does not prevent mixed data.

### 6. A torn JSONL tail can swallow the next completed record

**High priority for crash recovery.** [Lines 288–300](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L282) silently ignore malformed lines. [Lines 430–432](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/c00aab0e9902ee000b2e9d256dcf09b20c21c823/run_bestiary.py#L430) append without repairing an unterminated last line. The probe writes a torn tail, appends a valid record and gets zero readable records. The next completion has joined the malformed line and is also lost to parsing.

Before append, quarantine and preserve a torn tail and restore a clean line boundary. Reject malformed interior records instead of silently ignoring arbitrary corruption. Use durable append/checkpoint handling and propagate worker write failures to the main process. Resume should not mean paying for the same slot repeatedly after hidden data loss.

### 7. The $20 stop is an incomplete ledger

**High priority because the budget is an explicit constraint.** Successful preflight calls are not written to the JSONL paths scanned by `spend_on_disk`. A simulated $0.01 preflight produces a ledger total of $0.00. Intermediate retries are not individually recorded. Transport failures can have ambiguous billing, and restart resets per-trial attempt limits. The reservation estimate also assumes 200 input tokens and uses six-decimal rounding per recorded completion.

The in-process reservation mechanism is useful: it prevents simultaneously running workers from all spending the same unreserved estimate. It does not cover omitted charges, unknown billed requests, two independent collector processes or changed prices. Preserve every attempt, charge and unresolved reservation in a durable ledger; count preflight; validate input bounds; and run one collector process. Report estimated versus reconciled spend honestly.

At the runner's listed prices, the full 16,000-slot design at 1,024 output tokens and the assumed 200 input tokens per request would cost about **$64.90 Anthropic and $34.50 OpenAI**, excluding retries and preflight. This is a conservative cap scenario, not a forecast. The $20 caps are compatible with shorter average responses, but completion of all slots is not guaranteed. This is why incomplete-panel rules belong in the preregistration.

## Design judgments that code fixes cannot resolve

- **The study's strongest question is framing behavior.** The same word receives every frame/category combination, which supports within-word contrasts. New conversations, fixed wording and a recorded schedule help.
- **The independent units are words.** Fresh gives 24 deliberately constructed words, including only eight in one source set. Five repeats improve estimates for a particular prompt; they do not create five independent words. The proposed bootstrap carries all conditions and models of a word together.
- **There is no clean intent or authorship effect.** Human/animal-intent and Claude/no-category-intent differ simultaneously in author, intention, morphology, length constraints and selection. Keep per-word displays and compound source-set labels.
- **Known/fresh does not identify contamination.** The word sets differ in content and creation process, and the batches occur at different times. Endpoint-generation interactions cannot remove those differences. The claim that historical models are necessarily unchanged, exposure-free controls also requires verifying the served versions.
- **An inventory match is a literal observation.** `imaginary` is supplied in one prompt frame. A higher output match rate can reflect echoing. `target is not a recognized word` has a definition form. `may` can qualify a local trait. Absence of a listed expression cannot establish real-world assertion or confident invention.
- **Thirty-two families are acceptable as a feature battery.** They are not 32 independent primary hypotheses. My proposal selects four primary indicators and two frame contrasts, retaining every other family under prespecified descriptive/exploratory status.
- **Freeze before collection.** The README says preregistration precedes collection, while the sample design places scorer freeze after fresh collection. My proposal chooses the stricter sequence so later disagreements about what was seen do not affect the registration's status.

## Provider documentation checked

These are reported provider metadata, consulted November 10, 2026 ET. They do not prove ingestion of any Bestiary file, and live account access was not tested. Knowledge cutoffs and training-data cutoffs are different fields.

| Model | Reported knowledge cutoff | Separate training-data cutoff, if shown | Standard input/output USD per million tokens | Official source |
| --- | --- | --- | --- | --- |
| Claude Sonnet 4.6 | August 2025 | January 2026 | 3 / 15 | [Model page](https://platform.claude.com/docs/en/models/sonnet-4-6/overview) |
| Claude Haiku 4.5 | February 2025 | July 2025 | 1 / 5 | [Model page](https://platform.claude.com/docs/en/models/haiku-4-5/overview) |
| Claude Sonnet 5.5 | June 2026 | June 2026 | 2 / 10 | [Models overview](https://platform.claude.com/docs/en/models/overview) |
| Claude Haiku 5.5 | June 2026 | June 2026 | 0.10 / 0.50 for these short prompts | [Model page](https://platform.claude.com/docs/en/models/haiku-5-5/overview) |
| GPT-5.4 mini | August 31, 2025 | Not separately established here | 0.75 / 4.50 | [Model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini) |
| GPT-5.4 nano | August 31, 2025 | Not separately established here | 0.20 / 1.25 | [Model page](https://developers.openai.com/api/docs/models/gpt-5.4-nano) |
| GPT-6 Sol | April 20, 2026 | Not separately established here | 2 / 10 | [Model page](https://developers.openai.com/api/docs/models/gpt-6-sol) |
| GPT-6 Luna | May 18, 2026 | Not separately established here | 0.10 / 0.50 | [Model page](https://developers.openai.com/api/docs/models/gpt-6-luna) |

The two current OpenAI models have different documented knowledge dates. Do not transfer a GPT-6.1 cutoff to them. Relative to the repository's reported late-April/early-May historical data dates, these dates motivate caution, not a binary exposure label. The listed standard prices match the runner's values for this short-prompt workload. Neither documentation nor this review establishes that every requested model is accessible on the investigator's account.

## What was verified and what remains

The known dry run correctly reports eight words × ten conditions × ten repetitions = 800 trials per model. The synthetic construction check verifies unique IDs and vowel articles. All nine offline probes completed successfully against the unchanged baseline. Their exact observations are in `offline-review-results.json`; rerun with:

```bash
python offline_review_checks.py /path/to/run_bestiary.py
```

The script imports the supplied runner, replaces request functions with in-memory stubs and writes only in a temporary directory. It never calls `load_keys` from the source or makes a provider request. It is a review reproduction harness, not a comprehensive production test suite.

Still required before launch: collector fixes, a real content-neutral preflight by the investigator, private fresh-file validation, and implementation/fixture validation of the adopted scorer and analysis. The delivered preregistration supplies the decisions for that implementation. It does not claim those remaining steps have been completed.
