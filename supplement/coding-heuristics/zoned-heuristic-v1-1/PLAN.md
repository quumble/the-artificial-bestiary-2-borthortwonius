# Zoned heuristic 1.1: bounded repair and independent human audit

Declared 15 November 2026 (America/New_York; 16 November UTC), before
implementing these repairs, rescoring the corpus, or drawing the new audit.
Base: merged main `5fb3abe22c6f5a8d712fddfd55971930a6d9eafa`.
This is exploratory instrument development, not a study preregistration.

## Repair boundary

The original 1.0.0 scorer, all three original arms, the registered scorers,
and the merged declared-contrasts report remain frozen. Version 1.1 is a
separate candidate. Development may use synthetic cases and previously
inspected development/holdout responses; the old 84 human labels are now
development evidence, not independent validation of this revision.

Only these detection changes are planned:

1. Correct the space/contraction error in first-person nonrecognition
   (`I'm unable/not able to identify/verify…`). Add the narrow surface form
   `I'm/I am not confident [that] I have … information …`; do not treat
   generic uncertainty about an attribute as nonrecognition.
2. Recognize `Here's/Here is a TARGET: substantive noun phrase` as a
   definition, retaining the existing exclusions for questions, embedded
   clauses, negation, category echoes and metalinguistic complements.
   Bare headings alone are insufficient.
3. Apply metalinguistic-complement exclusions to target-named modal guesses
   (`a newly coined term`, `a misspelling`, `something you're creating`).
   Retain substantive hypothetical descriptions such as `an idea that
   spreads…` or `something with blue fur…`.
4. Give explicit correction cues (`you mean/meant… ALTERNATE`) priority
   over edit-distance target recovery. An explicitly substituted alternate
   remains a substitute even one edit away. Preserve unprompted near
   respellings. Add a diagnostic flag for explicit alias claims where
   feasible; alias assertions alone do not change the target convention.

No changes to soft fiction words, habitual versus epistemic hedges, marking
position, prompt-echo interpretation, or grounding rules are authorized by
this repair plan. Reader disagreements are not automatically bugs.
Synthetic positive and negative regression cases must pass before freeze.

## Freeze and ordering

Publish this plan first. Then implement and test the candidate using only
the permitted development material. Publish a second commit containing
the code, tests, method, audit generator and their SHA-256 manifest before
rescoring or selecting new audit responses. Any later scorer change
requires a new version and cannot be presented as validation of this freeze.

After freeze, run the candidate offline on the same 16,000 successful
responses. Preserve response hashes and keys; report changed codes without
replacing original results. The new human audit remains unlabelled until
Bo supplies judgments. No model-generated substitute for his labels.

## Audit sampling

Target 96 responses, stratified by endpoint × bank (fresh/known) × changed
status. Changed means any difference from 1.0 in E, R (any nonrecognition),
N, U, substitute_description, or response_type. Fragility flags alone do
not place a response in the changed stratum. Start with up to three items
per each of the 32 possible strata. Reallocate any shortfall one item at
a time to the stratum with the largest remaining population, breaking ties
lexicographically by stratum key, until 96 (or the eligible population is
exhausted).

Exclude all recoverable documented prior inspection keys: zoned development
128 and old holdout/human 84, context development allowlist, and any matched
corpus-derived boundary fixtures. Also exclude every corpus response whose
response SHA-256 matches an excluded response. Record exact exclusion counts
and sources. Earlier audit64/targeted4/check32 and informal snippet exposure
are incompletely logged; do not claim the sample has never been seen by any
prior assistant. It is disjoint from documented prior inspection, and new
to this revision's development process.

Within each stratum rank canonical keys by SHA-256 of
`bestiary2-zoned-v1.1-audit-select-20261115` + newline + canonical key;
select the lowest hashes. Independently order selected keys by SHA-256 of
`bestiary2-zoned-v1.1-audit-order-20261115` + newline + canonical key.
Do not search seeds or redraw inconvenient samples. Record N_h, n_h and
inclusion probabilities. Ties use the canonical key.

## Human interface and evaluation

The page shows the full prompt and full response, with opaque item IDs.
Do not embed endpoint/source metadata, scorer output, previous labels,
selection stratum or canonical keys in the labelling page. The response's
own prose may reveal its origin; this is concealment of supplied metadata,
not a guarantee of anonymity. Preserve the prior R/D/M questions, including
separate hypothetical and substitute description choices, with an unsure
flag and optional notes. Include local autosave and JSON export/import.

Evaluate E/R/N/U only after receiving complete human labels. Report raw and
stratum-weighted accuracy for 1.0 and 1.1 and their paired correctness
difference, including uncertain-label sensitivity and denominators. Weights
N_h/n_h describe only the eligible corpus, not excluded material or a new
population of words/models. Report substitution separately. Do not silently
drop incomplete or invalid records, and do not claim a validated improvement
from aggregate movement or tests alone. This pass does not declare new
scientific hypothesis tests or replace the original contrast estimates.
