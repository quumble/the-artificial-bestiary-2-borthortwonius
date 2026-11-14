# The Artificial Bestiary 2 — Secondary Analysis Plan v0.3

November 14, 2026. For Bo Chesterton. Based on Claude Fable 5.2's v0.2 and the subsequent accepted methodological review.

## Status and scope

Bo approved the v0.3 amendments in conversation before these secondary analyses were run. This text is the governing operational plan once committed. The plan commit must precede inspection of new secondary results. Execution order: verify inputs and reproduce the 14 published estimates; lock the audit sample; run B; run A; then conduct the investigator audit. C remains deferred and requires a separate opt-in and addendum.

Use the 16,000 existing study responses. No new model requests, model judges, or embedding-model calls. Original raw files, scorers, manifest, and released analyses remain unchanged. These are post hoc exploratory analyses of results already available to the investigators, not new confirmatory tests.

### Changes from v0.2

1. Normalize joins to `(batch, model_requested, trial_id)` and enforce one-to-one correspondence. The released Fable CSV has no trial_id: resolve its `(batch, model, word, condition, rep)` through the unique frozen schedule rather than joining on trial_id alone.
2. Keep description disagreement and description rate primary. Keep rho as an unclipped contextual diagnostic, not a variance-explained percentage.
3. Remove A's generation-variance/word-bootstrap-variance share. Show the two uncertainty scales separately.
4. Use request-start timestamps for an explicitly descriptive early/late sensitivity, without diagnosing drift.
5. Lock development, audit, and targeted response IDs before B's results are inspected. Make human coding prompt-aware and keep the targeted cases separate.
6. Store GPT indicator counts alongside Fable states. Retain the smaller audit, closed-form A, all 14 estimands, calls-only reporting, and deferred C.

## Common rules

Verify 9,600 fresh and 6,400 previously published responses, eight endpoints, ten exact conditions, 1,920 fresh and 640 published cells, and five or ten repetitions respectively. Exclude eight content-neutral preflights. `known` is a software label for previously published words, not evidence of model knowledge.

Before analysis, verify these complete archive SHA-256 hashes:

- Raw: `f3a20641ed5d7136d71529cc7325437c9f415e62a3d41f5513e38c115875aef6`.
- Analysis: `b6f8dd11c3438b55cc6193673f2fa0f859c6fabbb13f9baf5a5246d129462373`.

Verify the freeze manifest, included frozen source hashes, expected schedule, eligible terminal records, source labels, unique composite keys, and score-to-response matches. Stop on mismatches. Extract archive paths safely, normalizing Windows separators. The secondary implementation records its own runtime; it does not relax the original analyzers' environment checks or masquerade as an exact rerun of them.

A cell is bank × word × endpoint × exact condition. Use equal thirds for fresh sources and equal intent halves for published words in B. Preserve each released estimand's own weights in A. Do not pool banks except for H4. Conditions within a non-neutral framing receive equal category weights. Endpoints remain fixed, not a random sample of models.

Word bootstraps resample whole words within the three fresh source groups or two published intent groups, keeping conditions and endpoints paired. Use 10,000 draws and linear-quantile unadjusted 95% percentile intervals where specified. These are empirical word-bank sensitivity summaries, not unrestricted population guarantees. Report undefined draws, counts and sparse/degenerate support. Do not replace undefined quantities with zero.

No new tests or p-values in A, B, or the audit. The fixed endpoints used their collected settings; the two newer Claude endpoints did not have explicit temperatures in the runner. Do not rank endpoints' truthfulness, safety, or intrinsic stochasticity from these measures.

## Study B — response consistency

### States and primary quantities

Derive four exclusive states from frozen v1.1 flags: U = U=1; Marked E = E=1 and U=0; N = N=1; Other = E=0 and N=0. Verify U implies E and E excludes N. Other is a scorer residual, not a semantic behavior category. A bare modal need not exclude U under the frozen rules.

For R observations, n_E descriptions and n_N nonrecognition-without-description responses:

`D_E = 2*n_E*(R-n_E) / [R*(R-1)]`

`D_EN = 2*n_E*n_N / [R*(R-1)]`

These observed pair fractions estimate the corresponding pair probabilities under independent, stable cell-specific generation distributions. Their expectation does not depend on R under that assumption, so the main pair-fraction comparison needs no downsampling. Zero describes the observed repetitions, not an impossible future exception.

Report endpoint × framing × bank summaries: E rate p, N rate, mean D_E, and mean D_EN. Average categories within each word, words within source, and sources with the declared weights. Report source-specific diagnostics as well.

### Rho is contextual, not a decomposition

Compute `G = 2*p*(1-p)` and `rho = mean(D_E)/G`, using identical weights in numerator and p. G=0 gives null. Do not clip rho: its finite-sample estimate may exceed one. In an ideal population calculation the ratio contrasts within-cell disagreement with pooled-rate disagreement, but the empirical ratio is not a measured percentage of variability caused by randomness and does not establish identical cell probabilities.

Report 95% bootstrap intervals for mean D_E and rho, with defined/undefined draw counts. For rho, also flag small denominator support when G<0.05; this is a display warning, not an exclusion or threshold test. State p and G beside it. Compare framing patterns descriptively, not through a significance tournament.

### Secondary quantities and influence

Four-state disagreement: `D4 = 1 - sum(n_k*(n_k-1)) / [R*(R-1)]`.

Decompose its unconditional pair fractions into U–Marked E, N–Other, E–N, and E–Other. They must sum to D4. Also show each fraction divided by D4 as a conditional composition, null when D4=0. Summarize using the same word/source weights. Cue-boundary dominance is not a demonstrated change in policy; N–Other differences may reflect the nonrecognition inventory boundary.

Leave one word out, retaining source weights, and report the largest absolute change in D_E and rho. Keep all words in the main result. Report undefined leave-one-out ratios. Reuse available cell-level M26 and M27 as wording context, with eligibility counts and nulls, without relabeling them as new outcomes.

### Outputs

B1: complete endpoint/framing/bank summary including rates, D_E, D_EN, G, rho, intervals and support. B2: D4 and pair decomposition. B3: leave-one-word-out diagnostics. Distributions of n_E over cells, separated by bank and endpoint. A cell file includes R, four state counts, E/N/U counts, each GPT indicator count (M01/M02/M03/M09), source labels, condition, and wording descriptors.

Prose examples, if used, follow a stated deterministic selection rule. No claim about internal beliefs, deception, subjective experience, harm, or accuracy follows from a scored state or unanimous cell.

## Study A — information efficiency

### Scope and reproduction gate

Reconstruct all eight fresh-bank GPT primary contrasts and Fable H1–H6. Check every estimate against the machine-readable release to absolute tolerance 1e-10 on the proportion scale, before any reduced-design analysis. Stop if any fails. This gate checks point-estimator implementation, not reproduction of the original inferential routines.

H1/H2/H3/H5/H6 use their registered fresh-bank conditions and endpoint/source weights. H4 uses the known-minus-fresh change in the current-minus-historical endpoint gap in N, with equal intent weights in both banks. Do not replace H4 with a simple bank difference or change H6's difference-of-differences direction.

### A1 — generation-noise scale

For a linear estimand with combined coefficient w_c on cell c and indicator sample variance `s_c^2 = n_c*(R_c-n_c)/[R_c*(R_c-1)]`, estimate:

`V_gen = sum_c w_c^2 * s_c^2 / r_c`.

Combine coefficients for any repeated use of the same cell before squaring. This calculation assumes independent generations across included cells and a stable cell-specific distribution. It is an empirical plug-in estimate, not an observed prospective sampling distribution. Unanimous cells contribute zero estimated variance; report their count and their share of absolute estimand weight, not a claim of zero true uncertainty.

Show generation-noise SD in percentage points for fresh depths r=1,...,5. For H4 use proportional fresh/published depths (1,2),...,(5,10). Alongside these show a separate full-data word-bootstrap SE using the common stratified procedure. Do not divide the two variances, add them as if they were proven independent components, or say repetitions explain a particular share of an interval.

For retrospective subsets without replacement, conditional deviation from the full corpus has variance:

`V_nested = sum_c w_c^2 * s_c^2/r_c * (1-r_c/R_c)`.

Apply the correction per cell, including H4's unequal bank depths. This is conditional finite-corpus resampling variability; it becomes zero when every observation is retained. It is not prospective accuracy, sample-size adequacy, or independent replication.

Check this expression with 500 random within-cell subsets per depth, from recorded independent streams. Report simulated SD, analytic SD and the Monte Carlo diagnostic. Use synthetic brute-force enumeration as the exact implementation test; a real Monte Carlo discrepancy is investigated and disclosed rather than retried with favorable seeds. All 14 estimands here are linear; any discovered exception stops that calculation pending a disclosed amendment.

### A1 — temporal sensitivity

Use `timestamp_utc` from the released export, the recorded request-start time. Break ties by attempt_id. Within each cell compare earliest two and latest two fresh responses, dropping the middle one, or earliest five and latest five published responses. Do not use shuffled repetition numbers or retry ordinals as chronology.

Report signed early-minus-late contrast and the estimated exchangeable-noise SD `sqrt(sum_c 2*w_c^2*s_c^2/h_c)`, where h_c is that cell's half size. This is a descriptive temporal sensitivity, not a drift test or a decision threshold. If timestamp completeness or validity fails, omit the check with a reason; do not substitute an unverified order field.

### A2 — words versus repetitions

Fresh bank only; retain the other 13 estimands and exclude H4. Draw 1,000 independently sampled word subsets at each q=2,4,6,8 words per source, using the same selected words across endpoints/conditions. Retain r=1,...,5 repetitions as an analytical noise allocation, not new requests. Recalculate the original source/contrast weights for each retained bank.

Report separately: (a) SD of full-depth point estimates across those word subsets, and (b) square root of the mean estimated generation variance across those subsets at each depth. Do not call their sum total variance. Word-subset spread is zero at q=8 by construction. The design uses `240*q*r` calls; mark equal budgets q/r=8/1, 4/2 and 2/4 (1,920 calls).

The comparison concerns allocations within these 24 words. It does not estimate the value of unobserved new words. Report all estimands and grids; no retrospective power, optimal stopping, or unnecessary-trial verdict. Calls only; no token or dollar reconstruction. Eight preflights are separate fixed overhead.

## Single-investigator scorer audit

### Lock the sample before B

Draw once with independent named deterministic streams. Development: 12 fresh responses. Audit: up to two remaining fresh responses for each endpoint × four-state cell (maximum 64). If fewer than two are eligible, take all and record the shortfall. Targeted diagnostic: four further fresh gpt-5.4-mini responses under imaginary framing with E=1, sampled after excluding development and audit items. Keep this diagnostic separate from state-stratified counts. All sample sets are disjoint.

Record selected composite keys and hashes before inspecting B. Publish a commitment digest and selection rules; keep the unblinding key separate from the coding packets. Sampling may use existing scores, but no new B results determine selection. Lock the codebook after development and before revealing audit labels or machine comparisons. No resampling to replace inconvenient examples.

### Prompt-aware coding

Show exact prompt and response while masking endpoint metadata, source labels, machine labels and expected directions. Masking is partial because word/style recognition remains possible. Questions: substantive description of the target (yes/no/unclear); contextual presentation (licensed invention/hypothesis, interpretive guess, factual presentation, mixed/unclear, or not applicable); and expressed nonrecognition (yes/no/unclear). Record brief evidence spans or notes.

An imaginary prompt already licenses creative invention. Declarative prose within that frame is not automatically an unsupported factual claim because the answer fails to repeat 'imaginary'. Conversely, mark an explicit incompatible real-world assertion or unclear scope as mixed/unclear and explain it. Keep separate a note of response-explicit qualification so prompt-licensed invention is not confused with response-local cue matching.

The targeted diagnostic asks what the matched cues qualify in context, not merely whether a regex fires. Perform machine comparisons only after human codes are locked. Report state-stratified agreement/disagreement counts and error types, not pooled accuracy or a corpus error rate. No second coder, inter-rater reliability, independent gold standard or recode pass. Any new heuristic is separately versioned; v1.1 is never rewritten.

## Study C — deferred

No convergence calculations in this run. After A/B review, Bo may opt in under a separate dated addendum. Before that run, settle the version-pinned stop-word list, exact tokenization, target masking including plurals/possessives, empty–empty Jaccard behavior, and a length/coverage diagnostic. Preserve v0.2's proposed cross-family same-word versus source-matched different-word comparison, whole-GPT-block permutation, all 24 word values, and descriptive M30 context. No claim of shared facts, independent training, or independently invented knowledge.

## Implementation, settings, and records

Keep code, tests and outputs in `secondary-analysis/`. Execution: committed plan → input integrity and 14-estimand gate → audit sample commitment → B → A → investigator coding. B/A may proceed before human coding because they explicitly measure frozen surface features. Do not publish a completed-audit claim before Bo supplies labels.

Random streams use NumPy PCG64 with a seed obtained from the first 16 bytes of SHA-256 of `bestiary2-secondary-v0.3-20261114|<stream>`, interpreted as a big-endian integer. Name independent streams for B-word-bootstrap (each bank), A-word-bootstrap (each bank), A-response-subsets (each depth), A-word-subsets (each q), development selection, state-audit selection, targeted selection, and packet presentation. Sorted input keys precede random sampling. Record seed integers and NumPy/Python versions. C has no active stream until approved.

Required tests: safe extraction; duplicate joins including cross-endpoint trial-ID collisions; schedule and source completeness; U/E/N consistency; exact pair counts including unanimous, 4:1 and 2:3 examples; pair decomposition; undefined and above-one rho; whole-word stratum-preserving resampling; leave-one-out weights; all 14 coefficients on synthetic fixtures; finite-population variance by enumeration; temporal ordering; disjoint audit IDs; full-data gate. Distinguish synthetic tests, data-integrity checks, and scientific validation.

The manifest records input/archive hashes, scoring hashes, plan commit, runtime, seeds, settings, execution order, code hashes and output hashes. A later code correction keeps its history and is logged; a changed scientific decision requires a plan amendment. Every output remains exploratory, including null or inconvenient results.

## Sources and provenance

v0.2: The Artificial Bestiary 2 — Secondary Analysis Plan v0.2, Claude Fable 5.2, November 14, 2026, supplied by Bo. v0.1: Secondary Analysis Proposal for Fable, November 14, 2026. v0.3 incorporates the subsequently approved review and operational clarifications above.

Repository: `quumble/the-artificial-bestiary-2-borthortwonius`, reporting revision `ecc078b09da59a2859fb8ab82607b9c095de0cb6`. Collection source `0d39166092aac95253fc5a140231fb428a6a4809`. Release tags `raw-data-2026-11-11` and `analysis-v1-2026-11-11`.

Source files checked: README, run_bestiary.py, analyze_bestiary.py, analyze_claude.py, prereg/claude_scorer_v1_1.py, the GPT measurement specification and preregistration, and supplement/REPORTING_REVISION.md. Schema inspection confirmed Fable's normalized join requires frozen-schedule reconstruction, and cell-features.jsonl contains M26/M27. No new secondary results were inspected while fixing this plan.
