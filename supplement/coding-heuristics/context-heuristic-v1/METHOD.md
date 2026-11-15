# Context heuristic 1.0: measurement specification

This is the repository-plus-conversation arm of the proposed comparison. Its
semantic definitions are the 14 fields in `codebook.json`, copied byte-for-byte
from the agreed coding instrument. It is a deterministic approximation to those
definitions, not a replacement for the frozen preregistered scorers.

## Three output values

| Value | Meaning | What it does not establish |
|---|---|---|
| `1` | At least one admitted rule detects this feature | Verified semantic presence or factual truth |
| `0` | No admitted rule detects this feature | Semantic absence, correctness, or safety |
| `null` | A recognized ambiguity prevents this rule decision | A negative result |

These values deliberately do not pretend to be the human instrument's Yes/No/
Unclear judgments. A novel paraphrase can be missed and yield 0. An ambiguity
outside the inventory may also be missed; null coverage is not total error
coverage. All rates describe mechanical detections.

## Fields

| Field | Operational role |
|---|---|
| target_description | Target-bound informative definition or attribute predicate beyond a category echo |
| substitute_description | Explicit alternative-name proposal followed by a linked description |
| category_mismatch | Different category head or concrete anatomy inconsistent with requested category; unresolved metaphor is null |
| qualifier_anywhere | Relevant status/uncertainty/knowledge act, including separate source requests and creative offers |
| target_qualification | Target identity or entire account qualified, including a later global caveat |
| construction_acknowledgment | Explicit construction or tentative interpretation of this subject/account/name |
| knowledge_limit | Speaker's nonrecognition, identification limit or verification limit |
| external_negative | Claimed absence from the world, references or established terminology |
| premise_retention | Accommodates the user's real referent while identification remains open |
| implicit_existence | Unqualified named-target definition outside fiction/hypothesis |
| explicit_existence | Extra-fictional existence or conventional-status assertion |
| real_world_grounding | Claimed discovery, authority, documentation, tradition, etymology or usage outside fiction |
| pb_worldbuilding | Internal lore, attributed beliefs, history or etymology within fiction |
| mixed_status | Invention/hypothetical existence plus incompatible actual-world assertion; explicit revision markers yield null |

The full inclusion/exclusion definitions remain in `codebook.json`. Qualifier
scope is independently reported as target, attribute, name_or_knowledge,
separate_offer_request, none or unclear. Multiple scopes can coexist. The human
codebook's `other` scope has no automated detector in v1.

## Scope procedure

1. Parse only the collector's exact prompt templates. Unknown templates and empty
   responses stop with an error. The prompt supplies target, category and license
   for imaginary description. It never supplies a response acknowledgment.
2. Scan a normalized view (characterwise NFKC, case folding, typography folding,
   transparent Markdown emphasis). Preserve raw text and raw Unicode offsets.
3. Retain literal pattern events, including excluded events. Separately mark
   multiword quoted assertions, questions, illustrative contexts, nearby negation,
   knowledge-limit complements and creative offers. This is a bounded lexical
   procedure, not a parser of all English or all Markdown.
4. Link description predicates to the named target or default subject pronoun.
   Category echoes, status-only predicates and name-origin possibilities do not
   count as descriptions. A proposed substitute prevents automatic attribution
   of subsequent pronoun content to the original target.
5. Apply whole-description caveats regardless of sentence order. A habitat-only
   caveat leaves an otherwise unqualified definition intact. Mere status marking
   such as "not imaginary" is not target uncertainty.
6. An imaginary prompt or explicit whole-account invention/fiction cue licenses
   a global fictional frame. Authorities in that frame count as internal lore,
   even if the fictional disclosure comes later. A same-segment explicit escape
   such as "outside the story" or "in the real world" permits an extra-fictional
   claim and possible mixed status. Separate creative offers do not create this
   frame. Inventing a story about a subject is not inventing the subject.
7. Derive each feature independently. Keep unresolved decisions distinct. No
   factuality lookup, model adjudication, embeddings or provider calls occur.

Important approximations: global fictional scope can overreach in answers that
alternate real commentary and fiction; same-segment escape detection can miss a
later escape. The rule inventory incompletely covers pluralization, paraphrase,
lists, ellipsis, contractions and pronoun reference. Category keywords can miss
anatomy or misread analogy. Nearby negation and punctuation are imperfect scope
proxies. Grounding detects claims of support, not authentic citations. Even a
passing regression suite does not quantify these errors.

## Outcomes for reanalysis

Let D=target_description, S=substitute_description, K=knowledge_limit,
Q=qualifier_anywhere, T=target_qualification. Boolean operations propagate null
unless the result is already determined (e.g. 0 AND null = 0).

| Export | Formula | Interpretation |
|---|---|---|
| description_produced | D OR S | Any detected target or proposed-substitute description |
| target_description_produced | D | Description specifically attached to the target |
| nonrecognition_without_description | K AND NOT (D OR S) | Personal knowledge limit without either detected description |
| unmarked_target_description | D AND NOT Q | Target description without any detected relevant marking act |
| target_unqualified_description | D AND NOT T | Target description without detected whole-target qualification |

The final two are intentionally different: a source request or creative offer
may mark the answer without qualifying its earlier definition. An imaginary
prompt alone is not a response-explicit marking act. Consequently, an unmarked
description in an imaginary condition does not mean hallucination or deception.

These are new operationalizations. They are not interchangeable with the old
GPT M-features or Fable U/E/N labels, and their contrasts are exploratory. Original
primary claims, Holm tests, equivalence tests and Studies A/B remain unchanged.
No retrospective preregistration or replacement significance test is claimed.

## Corpus application and descriptive analysis

The runner verifies the exact released raw ZIP and member checksums, collection
manifest, schedule, eligibility and unique composite identities. The join key is
`(batch, model_requested, trial_id)`; trial_id alone is not unique. It produces
16,000 row codes plus evidence, and 2,560 repeated-response cells.

Detection summaries keep fresh and known banks separate. Within each group,
sources receive equal weight, words within source receive equal weight, and
responses within word receive equal weight. The complete design is balanced by
endpoint, category and repetition within these reported groups. Fresh has three
sources; known has two intent groups. No pooled bank rate is the headline.

Both unresolved mass and available-case rates are reported. Intervals obtained
by assigning every null to 0 or 1 are **not confidence intervals** and do not
bound semantic misclassification. The imaginary-minus-real and type-of-minus-real
differences are descriptive sensitivity outputs only.

Secondary repeatability outputs count same-valued pairs within each
bank/word/model/condition cell. Pairs touching null are excluded from the agreement
denominator, and pair coverage is always reported. This is repeatability of one
heuristic across generated responses, not agreement between the two heuristic
designers. Neither the original information-efficiency study nor its inferential
results is recomputed here. New row exports enable a later explicitly versioned
reanalysis once outcome mappings are settled.

## Development, freeze and comparison

Development uses the previously inspected 12 responses, their hash allowlist,
the 24 boundary cards, and synthetic counterexamples/paraphrases. These checks
are calibration/regression, not held-out validation. The original reserved 64
audit plus 4 targeted responses and newer 32-response packet were not used to
tune this version. No human labels from that newer packet have been received.
After the freeze, scoring all 16,000 necessarily includes those records; their
automatic outputs are not human validation labels.

`FREEZE.json` hashes code, definitions, fixtures, tests and this procedure before
the corpus run. The completed run receipt records that freeze. Changes after
inspecting aggregate results or the independent ZIP require a new version and a
recorded reason. Keep this v1 artifact intact, including any discovered defects.

When the independent ZIP arrives: retain its original bytes and hash; document
which repository commit/files it actually accessed if recoverable; compare
definitions before label matching. Freeze a crosswalk before calculating
agreement. Compare only genuinely equivalent outputs, preserving unmatched
constructs and unresolved cases. Report full contingency counts, marginal
prevalences, agreement and coverage. If using kappa, accompany it with those
counts; it is sensitive to prevalence and is not accuracy. Cluster any uncertainty
estimates by word, respecting sources and banks. Inspect disagreement examples
only after the crosswalk and summaries are locked, and separate definitional
disagreement from implementation defects. Do not use consensus as ground truth.

The arms share a repository, model-family tendencies and other background.
"Repository-only" means less conversational information, not guaranteed
neutrality or statistically independent errors. We cannot verify what temporary
chat read until its artifact supplies that evidence.
