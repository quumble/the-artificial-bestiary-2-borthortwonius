# Method, source mapping, and research safeguards

## Repository basis (inspected November 15, 2026)

The source study is:

- https://github.com/quumble/the-artificial-bestiary-2-borthortwonius
- Source of GPT v1.0 flags and match evidence: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/bestiary_scorer.py
- Exact GPT inventory: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/docs/gpt-proposal/inventories-gpt-v1.json
- GPT analysis and registered `PRIMARY` array: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/analyze_bestiary.py
- Fable v1.1 scorer: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/prereg/claude_scorer_v1_1.py
- Fable registered tests: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/analyze_claude.py
- Preregistration amendment: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/blob/main/prereg/CLAUDE_PREREG_AMENDMENT_1.md
- Source study's analysis release: https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/releases/tag/analysis-v1-2026-11-11

Original source code is **not bundled** here. You provide its path explicitly, so each output audit records the exact scorer and inventory SHA-256 hashes. This avoids accidentally presenting a paraphrase of an already frozen scanner as an equivalent preregistered implementation.

## Relation to the study's analyses

The original study has two **separately preregistered analysis families**, both on the same responses. The GPT primary family uses four non-exclusive any-match surface metrics M01/M02/M03/M09 and eight fresh-frame contrasts; the Fable family uses non-exclusive E/U/N-derived outcomes for six H1–H6 tests. GPT also reports a broad **secondary descriptive feature battery**; Fable also has ancillary descriptive summaries.

This package refers to the original four GPT flags as `Mxx`, the Fable response flags as `F_E/F_U/F_N`, and its **new** mutually exclusive categorization as `response_class`. This prevents a terminological conflict between "primary/secondary analysis family" and "primary/secondary coding layer". Analysis families, coding layers, and prompt conditions are distinct objects.

We deliberately do **not** implement the original GPT bootstrap (50,000 paired word-cluster draws), Fable permutations (100,000 per test), six-test Holm correction, or observed-vs-planned missingness bounds. Consult the upstream analyzers and releases for their results. Our summary CSVs are unweighted diagnostics within model × condition or model × word × condition, with explicit denominators.

## Why a partition is useful

Treating E, U, and N as three possible answers is logically incorrect because U is a **subset** of E; moreover there can be responses with neither E nor N. The six-bin partition resolves that only for **surface-coding and cross-tabulation**. It also distinguishes nonrecognition which coexists with descriptive syntax (D1) from nonrecognition without descriptive syntax (N0). This is a descriptive decomposition, not an independently validated measure of confabulation.

The GPT vs Fable definition-form comparison is especially useful because GPT M09 matches some negated definitions; Fable E can arise from multiple attribute statements without a target definition. Disagreement is a predictable feature of their different construct definitions.

## Data preservation and original-run integrity

The repository's release README says that current `main` contains a post-freeze Windows test-encoding fix. Exact replay must use the raw-data release and frozen source at commit `0d39166092aac95253fc5a140231fb428a6a4809`, with the manifest's original runtime validation. This **additional** coding package does not mutate frozen files, preregistered rules, run manifest, trial selection, released outputs, or prior claims. It may be run on the already-audited feature export even if exact replay isn't practical on your machine.

To keep independent provenance:

- Preserve a checksum-identified copy of the input file.
- Record `coding_audit.json`, the version of this ZIP, the exact source-scorer hashes and any local modifications.
- Declare exploratory analyses before selecting new statistical tests; mask word origin/endpoint in any later semantic validation.
- Keep familywise corrections within the original preregistered families for their registered claims. If these novel bins are tested, devise and report a new appropriate multiplicity plan rather than retroactively calling them preregistered.

## Interpretation limits

- Pure literal text matching is reproducible, **not** truth verification, confidence inference or model-state inference.
- Prompt words can appear in replies (including literal `imaginary`); the code exposes that sensitivity rather than inferring copying.
- Nearby negation, sentence boundaries and quotation marks provide **surface evidence only**; they cannot reliably determine discourse scope.
- The word bank has no genuine real-word control. Previously published coined words are labeled `known` solely as publication history, not as model recognition.
- Response-level repetitions are correlated within word, condition and endpoint; inferential methods must respect that structure.
- The instrument was built with knowledge of already reported results, so any inferential follow-up is **post hoc** unless separately designed on independent data.
