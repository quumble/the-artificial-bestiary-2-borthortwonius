# The Artificial Bestiary 2: Borthortwonius

*A preregistered study of framing and description in eight language model endpoints.*

**Bo Chesterton | Working-paper stage, November 2026**

A continuation of [The Artificial Bestiary](https://github.com/quumble/the-artificial-bestiary): the same coined words were presented under real, imaginary, and "type of" framings to measure changes in specified response features. The study combines fresh stimuli, two separately preregistered analysis families, and a public record of the prompts, responses, code, and results.

> "This is not a redo of the bestiary, this is the bestiary with wings."

## Current status and public materials

**Collection is complete. All eight GPT primary contrasts and all six Fable confirmatory tests have been reported.** The study collected 16,000 complete responses on November 11, 2026 under protocol `gpt-v1+claude-v1.1`. The working paper interprets those results. Some preregistered ancillary summaries remain outstanding, as described below.

| Material | Where to find it |
| --- | --- |
| Raw responses, stimulus lists, frozen source, manifest, and collection metadata | [Raw-data release: `raw-data-2026-11-11`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/raw-data-2026-11-11) |
| Original analysis outputs: 12 GPT files and four Fable files | [Analysis release: `analysis-v1-2026-11-11`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/analysis-v1-2026-11-11) |
| Analysis archive also uploaded to the repository | [`bestiary-analysis-2026-11-11.zip`](bestiary-analysis-2026-11-11.zip) |
| Exact source and protocols used for the run | [Frozen commit `0d39166092aac95253fc5a140231fb428a6a4809`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/tree/0d39166092aac95253fc5a140231fb428a6a4809) |

The raw-data release preceded the analysis release. Both include archive checksums. They are published, checksum-identified checkpoints. Current `main` also contains later repository maintenance, including the merged [Windows test-encoding fix](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/pull/2). Use the frozen source for exact reanalysis.

The summary below follows the November 2026 working paper, *The Artificial Bestiary 2 Borthortwonius: A preregistered study of framing and description in eight language model endpoints*, by Bo Chesterton. Its interpretation remains open to review.

## Study at a glance

| Component | Completed design |
| --- | --- |
| Fresh stimuli | 24 words: eight by Bo with imaginary animals in mind, eight from Claude with no category intent, and eight from a separate GPT Temporary Chat with no category intent |
| Previously published stimuli | Eight coined words from the earlier project, with four in each of its two historical intent groups |
| Conditions | Neutral description request, plus real / imaginary / type of crossed with animal / object / idea: ten conditions per word |
| Endpoints | Claude Sonnet 4.6, Haiku 4.5, Sonnet 5.5, Haiku 5.5, GPT-5.4 mini, GPT-5.4 nano, GPT-6 Sol, and GPT-6 Luna |
| Repetitions | Five per fresh word × condition × endpoint, ten per previously published word × condition × endpoint |
| Study responses | 9,600 fresh + 6,400 previously published = **16,000** |
| Completion | Every planned study slot completed on its first attempt, with no missing cells, cap truncations, or issue closures |
| Retained attempts | 16,008, including eight content-neutral preflights excluded from behavioral analyses |
| Fresh GPT primary weighting | One-third per word source, equal weights across categories and the eight fixed endpoints |
| Generation | One user message per request, no supplied tools or conversation history, 1,024-token output cap, and endpoint-specific supported controls |
| Analysis environment | Python 3.14.6 on Windows, NumPy 2.3.5, with the exact runtime recorded in the freeze manifest |

The software label `known` means **previously published**, not demonstrated model knowledge. Fresh words were withheld during collection and are now available in the raw-data release.

No reasoning tokens or thinking blocks were observed in the retained responses. Temperature was 1.0 where explicitly accepted and was omitted for the two current Claude endpoints. The study therefore does not establish a common numerical temperature across all endpoints. See the [sample design](docs/sample-design.md), the frozen request records, and the working paper's endpoint appendix for the precise controls and returned identities.

## Findings reported in the working paper

The main finding is **instruction-sensitive response behavior**: changing the framing around a fixed coined word changed the prevalence of registered definition forms, nonrecognition expressions, and qualification language.

### GPT-proposed analysis family

"GPT" identifies the analysis proposal. Every primary estimate below includes **all eight GPT and Claude endpoints**. M01 counts fiction-expression matches, M02 qualification-expression matches, M03 nonrecognition-expression matches, and M09 exact-target definition forms. Each is a mechanical any-match outcome.

| Measure | Contrast | Difference, percentage points | Adjusted 99.375% word-bootstrap interval |
| --- | --- | ---: | --- |
| M01: fiction expressions | Imaginary minus real | +16.39 | [+9.58, +22.74] |
| M01: fiction expressions | Type of minus real | +32.47 | [+27.36, +36.81] |
| M02: qualification expressions | Imaginary minus real | -26.11 | [-29.86, -22.53] |
| M02: qualification expressions | Type of minus real | +0.45 | [-2.26, +3.13] |
| M03: nonrecognition expressions | Imaginary minus real | -56.25 | [-59.65, -52.85] |
| M03: nonrecognition expressions | Type of minus real | -5.83 | [-10.17, -1.49] |
| M09: exact-target definition forms | Imaginary minus real | +74.20 | [+70.00, +78.43] |
| M09: exact-target definition forms | Type of minus real | +13.78 | [+8.13, +19.79] |

The intervals use 50,000 paired word-cluster bootstrap draws, resampling eight words within each source while retaining all their conditions, repetitions, and endpoints. Seven of the eight adjusted intervals exclude zero. Only three contrasts carried advance directional predictions, all supported under the full inventories. The seven-of-eight count is not a count of seven confirmed directional predictions.

**The fiction-expression result depends on the inventory.** Removing the literal entry `imaginary` changes M01's imaginary-minus-real estimate from **+16.39 to -13.19 percentage points**. This was a prespecified sensitivity, reported as point estimates without additional intervals or tests. It demonstrates inventory dependence, not a direct measurement of prompt copying or private recognition of fictionality.

Endpoint effects vary. All eight endpoints had positive imaginary-minus-real M09 differences and negative M03 differences, but "type of" effects were less uniform. Endpoint components are descriptive, without additional corrected significance claims.

### Fable analysis family

Fable's scorer defines **E** as a description form, **U** as E without any matched nonrecognition, fiction, construction, or interpretation cue, and **N** as nonrecognition without E. U is a subset of E. N and E are disjoint but do not exhaust every response. They are not three mutually exclusive response categories.

| Test | Registered comparison | Difference, percentage points | Holm-adjusted p | Registered interpretation |
| --- | --- | ---: | ---: | --- |
| H1 | E: imaginary minus real, all endpoints | +76.70 | .000060 | Supports the predicted direction |
| H2 | N: type of minus real, OpenAI endpoints | -24.38 | .000060 | Supports the predicted direction |
| H3 | U: animal-intent minus no-intent fresh words | -1.56 | .81629 | Does not support the predicted excess |
| H4 | N: current-minus-historical endpoint gap, previously published minus fresh words | -2.66 | .81629 | No corrected difference established |
| H5 | U: current minus historical endpoints | -3.47 | .06726 | Does not meet the corrected threshold |
| H6 | N: Anthropic-minus-OpenAI gap, Claude-origin minus GPT-origin words | +9.38 | .02744 | Corrected difference **opposite to the predicted direction** |

These tests use 100,000 two-sided permutations, with Holm correction across the six tests. The released 95% bootstrap intervals use 10,000 draws and are unadjusted. H3 and H5 use real and type-of conditions. H4 and H6 also include neutral. H4 standardizes both word banks to equal intent weights.

H6's interaction does not establish recognition of a model family's own inventions or shared memory. H4 is not a confirmatory equivalence result or a test establishing the presence or absence of training exposure. A reduction in N, as in H2, does not by itself establish more unqualified factual assertions.

Both families analyze the same responses. Their agreements are not independent replications, and multiplicity is controlled separately within each family. Source: [original analysis release](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/analysis-v1-2026-11-11).

## Interpretation and limitations

The working paper presents a focused extension of research on nonexistent entities, false premises, and pseudoword interpretation. Its claims concern the selected words, prompts, endpoints, and scoring rules.

- **The outcomes measure surface features.** They do not directly measure factual accuracy, unsupported factual commitment, private belief, or training exposure. Imaginary prompts explicitly license invention. M09 can match negated definitions, and a bare modal such as "may" or "might" does not by itself block Fable U.
- **The new responses have no independent semantic annotation.** Historical scorer-development comparisons are not held-out validation. The Fable preregistration excludes direct comparisons of absolute U rates across providers because scorer sensitivity differs.
- **The word banks and endpoints were deliberately selected.** Source, intention, morphology, length, and selection procedure were not independently randomized. Equal source weights define the pooled estimator without identifying a causal effect of authorship.
- **There is no genuine real-word or real-entity control bank.** Previously published coined words cannot establish selective recognition or serve as a known-exposure control.
- **Reporting is complete for the primary and confirmatory tests, with ancillary gaps.** Several planned Fable descriptive summaries were not generated by the released analyzer. They were produced afterward as a [post hoc descriptive supplement](supplement/fable-descriptives/summary.md), labelled as such and separate from the frozen outputs. The pooled 50-word and 100-word GPT prefix sensitivities were unestimable under the registered complete-panel rule. Those unavailable estimates are not zero effects or missing API responses.

The next research step proposed in the paper is a separately versioned validation of a prespecified sample of existing responses. Annotators would see the prompt and response while being masked to endpoint identity, word origin, and predicted directions. Further experiments would add real but unfamiliar controls, comparable generation briefs, repeated word-generation batches, and multiple prompt formulations.

## Reproducing the published analyses

Use a separate replay directory containing the **original frozen source files** and the data from the [raw-data release](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/raw-data-2026-11-11). Preserve the analysis release as the reference output.

The analyzers require `data/freeze.json`, `data/collection-status.json`, `data/attempts.jsonl`, and every source, specification, inventory, scorer, preregistration, and test file listed in the manifest. The raw snapshot preserves the frozen files. Alternatively, use the exact [frozen source commit](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/tree/0d39166092aac95253fc5a140231fb428a6a4809) alongside the released data, preserving the recorded file bytes.

Use **Python 3.14.6 on Windows with NumPy 2.3.5**. The programs validate the complete `sys.version` string from the manifest, so a different build with the same short version number can still be rejected. From the directory containing the frozen programs and restored `data/` folder:

```text
python -m pip install -r requirements-analysis.txt
python analyze_bestiary.py
python analyze_claude.py
```

The default commands retain the registered draw counts. GPT outputs go under `analysis/`, and Fable outputs under `analysis/claude/`. Reanalysis uses the released records and needs no provider keys, new API requests, or working SQLite database.

**Current `main` is not an exact replay substitute.** The frozen manifest includes test files, and the later Windows encoding fix changed `tests/test_claude_analysis.py`. That maintenance change leaves the scientific programs unchanged but will fail the original file-hash check. Use the frozen files and matching runtime rather than altering the manifest or creating a new freeze for the old observations.

Archive SHA-256 digests:

```text
f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6  bestiary-raw-snapshot.zip
b6f8dd11c3438b55cc6193673f2fa0f859c6fabbb13f9baf5a5246d129462373  bestiary-analysis-2026-11-11.zip
```

The raw archive includes its own manifest and per-file checksums. Its snapshot excludes credentials, the working SQLite database, and analysis outputs.

## Repository guide

| Path or resource | Contents |
| --- | --- |
| [docs/sample-design.md](docs/sample-design.md) | Word sets, conditions, endpoint lineup, request settings, and design decisions |
| [docs/evaluation-draft.md](docs/evaluation-draft.md) | Historical development of the five interpretive rules |
| [docs/measurement-catalog.md](docs/measurement-catalog.md) and [docs/calibration-log.md](docs/calibration-log.md) | Measurement proposals and calibration history. The frozen specifications govern the implemented outcomes |
| [run_bestiary.py](run_bestiary.py) | Collection runner, implemented with the Python standard library |
| [bestiary_scorer.py](bestiary_scorer.py) and [analyze_bestiary.py](analyze_bestiary.py) | GPT feature battery, match spans, word-level estimates, sensitivities, and descriptive comparisons |
| [docs/gpt-proposal/](docs/gpt-proposal/) | GPT preregistration, amendment, inventories, measurement specification, and development review |
| [prereg/CLAUDE_PREREG.md](prereg/CLAUDE_PREREG.md) and [prereg/claude_scorer.py](prereg/claude_scorer.py) | Original Fable preregistration and scorer, preserved for provenance and version sensitivity |
| [prereg/CLAUDE_PREREG_AMENDMENT_1.md](prereg/CLAUDE_PREREG_AMENDMENT_1.md) and [prereg/claude_scorer_v1_1.py](prereg/claude_scorer_v1_1.py) | Precollection amendment and primary scorer v1.1 |
| [analyze_claude.py](analyze_claude.py) | Fable's six confirmatory tests and scorer-version comparison |
| [docs/implementation-protocol.md](docs/implementation-protocol.md), [docs/claude-review.md](docs/claude-review.md), [docs/fable-final-review.md](docs/fable-final-review.md), and [docs/validation.md](docs/validation.md) | Historical implementation and review records. Pre-run status language in these records describes that stage |
| [tests/](tests/) | Offline tests, including the post-freeze Windows encoding fix |
| [stimuli/known-words.txt](stimuli/known-words.txt) | The eight previously published words |
| Raw-data release | Released fresh words, both stimulus files, `data/freeze.json`, `data/attempts.jsonl`, per-model raw exports, and collection metadata |
| Analysis release and repository ZIP | Original feature tables, estimates, sensitivities, audits, and provenance |

The fresh stimulus file and expanded `data/` and `analysis/` directories are distributed in the releases, rather than tracked as expanded directories on `main`. Their local paths remain ignored by Git.

## Running a new collection

The completed study can be inspected and reanalyzed from the releases. A new collection is a separate workflow that produces new observations and incurs provider charges. Follow the [sample design](docs/sample-design.md) and [implementation protocol](docs/implementation-protocol.md) in a separate working directory.

API keys go in the environment as `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`, or in a Git-ignored `keys.local` file beside the runner. Restore both released stimulus files under `stimuli/`, preserving their exact bytes. The current runner accepts only the committed stimulus hashes. Different stimuli require updated documented commitments and runner hash constants before freezing a separate study.

```text
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -v
python run_bestiary.py run known --dry-run
python run_bestiary.py check
python run_bestiary.py freeze --protocol gpt-v1+claude-v1.1
python run_bestiary.py run fresh
python run_bestiary.py run known
python run_bestiary.py status
```

`check` is a paid content-neutral preflight. The runner records accepted settings and returned identities, stops an endpoint if its identity changes or its issues exceed the registered threshold, and includes preflight and retries in the $20/provider spending cap. Completed refusals, empty outputs, and truncated responses are retained rather than regenerated. Resume requires the same frozen code and settings.

The collector supports native Windows Python. A new run using the released fresh list reuses publicly available stimuli, so it is not a new exposure-naive stimulus bank. New stimuli or protocol changes require their own documented commitments before collection. Keep keys and the working SQLite ledger private.

## Authorship and AI collaboration

**Bo Chesterton is the sole listed author and investigator.** GPT 6 Pro and Claude Fable 5.2 Medium participated throughout design discussion, preregistration, implementation and review, interpretation, and research prose. The manuscript was prepared with GPT assistance after the analysis release. This does not assert a Fable review of this particular manuscript.

Those collaborator names are the investigator's reported conversational-interface labels. They are distinct from the exact experimental endpoint identities and from the separate GPT Temporary Chat that supplied one stimulus bank. Both collaborators belong to model families evaluated in the study. Their participation is part of the provenance and is not an independent external endorsement. The two analysis plans were initially drafted separately and subsequently cross-reviewed.

## Decision history

These dated entries preserve the sequence of precollection decisions. Later amendments supersede earlier choices. The completed study and current reporting status are described above.

### Agreed November 9, 2026

- **Preserve the core design.** Real, imaginary, and "type of" framings crossed with animal, object, and idea, plus a neutral condition. Ten conditions per word.
- **Rebuild the evaluation from the ground up.** The earlier categories and results are evidence to learn from. They do not predetermine the new measurements.
- **Mechanical scoring with minimal personal scoring.** Fixed, auditable code. No default human or LLM judge. Surface measures must not be presented as an automatic confabulation detector.
- **Five core interpretive rules**, recorded in the [evaluation draft](docs/evaluation-draft.md#agreed-core-rules).
- A shared 500-token output limit was agreed on this date. It was replaced on November 10.

### Agreed November 10, 2026

- **A fresh-word run.** The original words are public, alongside roughly 5,000 raw responses, so any current model may have seen them. The new run uses 24 words that have never been published: 8 improvised by Bo Chesterton with imaginary animals in mind, and 16 generated by Claude Fable 5.2 with no category in mind.
- **The fresh words are withheld until collection is complete.** The design doc carries a SHA-256 hash of the list. The list and the fresh-batch responses are published afterward.
- **The known-word replication is a separate batch**, using the historical eight-word retest set. Neither batch's results may alter the other's stimuli, prompts, or settings. This replaces "comparison first, exploration second."
- **Eight models**: two historical and two current per provider, in matched size pairs.
- **A 1,024-token cap on visible output**, replacing 500. Historical responses almost never reached their caps; 500 would have cut off some conditions more than others.
- **Reasoning off for every model, temperature 1.0 where the API accepts one.**
- **Five repetitions per word and condition for the fresh batch, ten for the known batch.** 1,200 and 800 trials per model.
- **A spending stop of $20 per provider** across both batches.

### Agreed November 11, 2026

- **Word authorship is balanced.** Eight of the sixteen Claude-made words are replaced by eight GPT-made words, selected through fixed seeded draws from candidate pools with different construction histories. The fresh batch is three sets of eight. Trial counts are unchanged.
- **Stopping is per model.** A model stops when its issues exceed 5% of its closed slots in a batch, or at once if its served identifier changes. One model's stop does not affect the others.
- **Both analysts' families are kept, separately.** Each is corrected within itself. No joint error-control claim is made.
- **GPT fresh primary weights are one-third per source.** The original 50% Bo / 25% Claude / 25% GPT weighting is a sensitivity. Bootstrap resampling preserves all three source groups. Known/fresh comparisons retain common 50/50 intent weighting.

This project repeats the core design with new words, revised measurement, and standardized settings. It should not be described as an exact reproduction of every historical setting.

## Historical reference

Initial source inspection: [`quumble/the-artificial-bestiary` at `7fec51af5d28b743763225f4dd52ab29a4cb4d60`](https://github.com/quumble/the-artificial-bestiary/tree/7fec51af5d28b743763225f4dd52ab29a4cb4d60).

That repository contains the nine-word Sonnet pilot, eight-word retests, raw responses, and several stages of coding. Its runners used output caps of 400 tokens for the Anthropic runs and 700 for the OpenAI runs, at temperature 1.0. Historical source defaults do not by themselves establish every setting used in the original runs. Further comparison must distinguish runner defaults, recorded settings, and unknown settings.
