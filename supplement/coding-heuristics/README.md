# Post-publication coding heuristics: three arms

Added 15 November 2026. Investigator: Bo Chesterton. Record assembled by Claude Fable 5.2.

Three mechanical, no-LLM coding layers were written for the 16,000 published
responses on the same day, under three different information conditions. All
three are post-publication and exploratory. None replaces the preregistered GPT
or Fable scorers, their analyses, or Studies A and B, which remain the
inferential reference for every registered claim.

**Which one to use.** The investigator has designated the zoned heuristic
(third arm) as the main choice for new descriptive recoding. The other two are
kept frozen as the comparison baseline. The reasons, and the limits of that
choice, are set out under [Status of the main choice](#status-of-the-main-choice).

## The three arms

| | Mechanical coding heuristic | Context heuristic | Zoned heuristic |
|---|---|---|---|
| Folder | [mechanical-coding-heuristic-v1/](mechanical-coding-heuristic-v1/) | [context-heuristic-v1/](context-heuristic-v1/) | [zoned-heuristic-v1/](zoned-heuristic-v1/) |
| Version string | `bestiary2-response-categories/1.0.0` | `bestiary-context-heuristic/1.0.0` | `bestiary2-zoned-heuristic/1.0.0` |
| Written by | GPT, temporary chat | GPT, with memory and project conversation | Claude Fable 5.2 |
| Saw the repository | Yes | Yes | Yes |
| Saw prior project conversation | No | Yes | Summary-level memory of the project only |
| Saw the other arms before designing | No | No | Both, plus their disagreement |
| What it is | Wrapper over the frozen GPT v1.0 and Fable v1.1 scorers, adding a six-way class and 14 tags | New 14-field detector with scope rules and null values | New detector that zones each sentence before counting; eight-way class, 16 fields |
| Ships results | No | Yes, all 16,000 | Yes, all 16,000 |
| Role here | Baseline | Baseline | Main choice for exploratory recoding |

Model names are the investigator's reported interface labels, as elsewhere in
this repository. The investigator described both GPT arms as GPT-6 Astra, one
temporary and unpersonalized, one personalized with memory.

## Circumstances of each contribution

### Mechanical coding heuristic (repository-only arm)

- **Condition.** A GPT temporary chat with no memory and no project history.
- **Brief, verbatim** (as recorded in the context arm's `PROVENANCE.json`): the
  repository URL, followed by "please design a mechanical categorization
  heuristic to code responses for the primary and secondary analysis based on
  what you see. export a zip".
- **What it chose to do.** It declined to write a new detector, on the stated
  ground that a near-copy of a frozen scorer could be mistaken for the
  registered one. It loads the upstream scorers from a checked-out copy of this
  repository and derives new categories from their outputs.
- **State on delivery.** Code, codebook and a synthetic example. No corpus
  results. Its own test report records 13 synthetic tests passed and one
  upstream-integration test skipped, because the repository's source files were
  not present in its build environment.
- **Run output in this folder was not produced by its author.** See
  [run-2026-11-15_claude-fable-5-2/](mechanical-coding-heuristic-v1/run-2026-11-15_claude-fable-5-2/):
  Claude Fable 5.2 ran the package unchanged against `main` at `ecc078b` and
  the `response-features.jsonl` inside `bestiary-analysis-2026-11-11.zip`, with
  `--verify-embedded` on. All 16,000 rows passed that check, and all 14 tests
  passed with the upstream integration test enabled. The context arm's author
  reports an equivalent run against the frozen source, also matching the
  released Fable E/U/N values.

### Context heuristic (repository-plus-conversation arm)

- **Condition.** GPT with memory and the project conversation. Its
  `PROVENANCE.json` describes the arm as "deliberately contextual, not blinded
  or neutral", with prior project context and prior exposure to aggregate
  results.
- **Semantic source.** The 14 fields of `measurement-redesign/check32`
  codebook v0.2 and boundary decisions settled in conversation. Calibrated on
  12 previously inspected responses, 24 boundary cards and synthetic cases.
  The reserved audit, targeted and check32 samples were not used for tuning.
- **Freeze and run.** `FREEZE.json` hashes code, definitions, fixtures and
  tests before the corpus run and before the repository-only artifact was
  inspected. It then scored all 16,000 responses. 4,233 responses (26.5%) have
  at least one unresolved field. No rule was revised after the run.
- **Its author's own later assessment.** See the GPT comparison report below.
  It identifies failures in this package against its own definitions and
  recommends repairing them in a separately versioned implementation.

### Zoned heuristic (third arm, informed)

- **Condition.** Claude Fable 5.2, in a single session, with account memory
  enabled. That memory held a summary-level note that this study exists; it
  held no measurement decisions, codebooks or boundary rulings.
- **Sequence.** It first received the two GPT packages and was asked to
  compare them. It ran the mechanical package, joined both codings on all
  16,000 responses, wrote the two-arm comparison report, and only then was
  asked for its own version "with both in mind".
- **Foreknowledge, stated plainly.** Before designing, it had read both
  packages in full, seen their response-level and aggregate disagreement, and
  read about 35 corpus snippets drawn from disagreement cells. It is not an
  independent replication and should never be described as one.
- **Development and freeze.** Rules were written against a seeded development
  sample of 128 responses and 18 synthetic tests. The code was hashed
  (`FREEZE.sha256`) before the held-out sample was drawn. No rule changed
  after the freeze; defects found afterward are listed in its `METHOD.md` and
  left unfixed.
- **Blind check.** 84 held-out responses, weighted toward cases where the two
  GPT arms disagree, were labelled from text alone before the corpus run. The
  reader was Claude Fable 5.2, the same model that wrote the heuristic. These
  are model labels, not human labels.

## Comparison documents

| File | Author | Written when | Scope |
|---|---|---|---|
| [comparison/two-arm-comparison_claude-fable-5-2.docx](comparison/two-arm-comparison_claude-fable-5-2.docx) | Claude Fable 5.2 | Before the zoned heuristic existed | Mechanical vs context |
| [comparison/two-arm-comparison_gpt-context-arm.docx](comparison/two-arm-comparison_gpt-context-arm.docx) | GPT, author of the context arm | By its own statement, before receiving or reading the Claude report | Mechanical vs context |
| [zoned-heuristic-v1/comparison/three_way.json](zoned-heuristic-v1/comparison/three_way.json) | Claude Fable 5.2 | After the zoned freeze | All three, plus the blind check |

The two reports were written separately and reach the same response-level
figures for the three central outcomes (kappa 0.63, 0.70 and 0.44 for
description, unmarked description, and nonrecognition without description).
Both find that the context arm counts guesses about the word, and fragments of
requests, as descriptions of the thing. The GPT report adds a repeatability
comparison and three controlled probes of its own code; the Claude report adds
word-clustered intervals and the endpoint-level consequences.

`comparison/` also holds the crosswalk Claude froze before computing agreement
and the machine-readable two-arm results behind its report.

## Headline three-way figures

Cohen's kappa over all 16,000 responses (A context, B mechanical, C zoned):

| Construct | A vs B | A vs C | B vs C |
|---|---:|---:|---:|
| Description produced | 0.63 | 0.64 | 0.89 |
| Any nonrecognition | 0.60 | 0.60 | 0.94 |
| Nonrecognition without description | 0.44 | 0.45 | 0.89 |
| Unmarked description | 0.70 | 0.70 | 0.91 |

Blind check, correct out of 84 (model-read labels):

| Construct | A | B | C |
|---|---:|---:|---:|
| Description produced | 49 | 76 | 82 |
| Any nonrecognition | 58 | 79 | 78 |
| Nonrecognition without description | 51 | 74 | 79 |
| Unmarked description | 71 of 79 | 80 | 81 |

Human pass on the same 84, correct out of 84 (labels by the investigator, added
later the same day; see [human-pass/](human-pass/)):

| Construct | A | B | C |
|---|---:|---:|---:|
| Description produced | 51 | 72 | 80 |
| Any nonrecognition | 60 | 79 | 78 |
| Nonrecognition without description | 52 | 73 | 80 |
| Unmarked description | 69 of 79 | 77 | 78 |

Agreement is not accuracy, and the sample is enriched for disagreement, so
these raw counts are not population accuracy rates. Weighted figures and full
counts are in `three_way.json` for the model-read labels and in
`human-pass/human_labels.json` for the human pass.

## Human pass

The investigator labelled the 84 held-out responses in one sitting of about 29
minutes, from text alone, on a single-key page that showed no instrument
output and no model-read labels. The page is saved as
[human-pass/labelling-page.html](human-pass/labelling-page.html) so the exact
wording of each question is on record. The investigator was not naive: he had
read the comparison summaries first, and the page's hint says that guesses
about the word are not a description.

The ordering of the three arms is the same under the human labels as under the
model-read ones.

Human reader against model reader, same 84:

| Judgement | Agree | Kappa |
|---|---:|---:|
| Description produced | 80 | 0.90 |
| Any nonrecognition | 82 | 0.95 |
| Nonrecognition without description | 83 | 0.98 |
| Unmarked description | 77 | 0.69 |

On the 34 responses where both readers saw a description, they gave the same
mark code on 26. Whether a description is flagged as invented is the least
reliable judgement here, between readers as well as between instruments.

Defects in the zoned heuristic 1.0.0 that the human pass adds to the list in
its `METHOD.md`:

- **Substitution by respelling.** The human reader marked four responses as
  describing a different word. The heuristic caught one. The other three treat
  the target as a variant spelling or alias of a real word ("kavanesh (also
  spelled kavanah)", hambroqet as a name for the barn owl) and describe that.
  The heuristic scored all three as descriptions of the target, two of them
  as unmarked. The model reader made the same call as the heuristic on these.
- **Soft fiction words.** In several described responses the heuristic, and the
  model reader, took "imagined", "mythical" or "isn't an established term" as
  flagging the description or as nonrecognition where the human reader did not.

The frozen 1.0.0 files are unchanged. These belong in a later version, tested
on a fresh held-out sample, since this one has now been read three times.

## Status of the main choice

The zoned heuristic is the main choice for exploratory, descriptive recoding
because it keeps the registered scorers untouched, returns a value for every
response, separates the response types that the other two conflate, and did
best on the one blind check available. That choice carries these limits:

1. It was designed with knowledge of the other two arms and of where they
   disagree. Its agreement with the registered scorers is not validation by
   them, and its lead on the blind check is not independent evidence.
2. The first blind labels were written by the model that wrote the heuristic,
   from the first 600 characters of most responses. One human pass has since
   been done and agrees on the ordering of the arms. It is one reader, on 84
   responses, who knew the comparison's findings.
3. The mechanical arm wraps a Fable scorer and the zoned arm was written by
   Claude Fable 5.2; the context arm's author had project history. None of the
   three is independent of the others.
4. Known defects in version 1.0.0 are listed in its `METHOD.md`. Fixes belong
   in a new version with the reason recorded.
5. Nothing here is preregistered. Any test built on these codes needs its own
   declared error control and must not be appended to either original family.

## Layout and what is not expanded

```
archives/                         the three packages exactly as received, with SHA256SUMS.txt
mechanical-coding-heuristic-v1/   expanded package, plus the labelled run folder
context-heuristic-v1/             expanded package, large result files left in the archive
zoned-heuristic-v1/               expanded package, evidence file left in the archive
comparison/                       both two-arm reports and Claude's two-arm machine-readable results
human-pass/                       the investigator's labels for the 84 held-out responses, the page used, and scores
declared-contrasts/               the exploratory contrast list, declared before intervals were computed
```

Expanded folders contain only members of the corresponding archive, byte for
byte, with one exception: the labelled run folder inside the mechanical arm.
`human-pass/` is new material and belongs to no archive.
Members larger than 5 MB are not expanded and are available from the archive:

| Archive | Not expanded |
|---|---|
| `Bestiary_2_Context_Heuristic_v1.zip` | `results/evidence.jsonl` (60 MB), `results/response_codes.jsonl` (15.7 MB), `results/cell_consistency.jsonl` (9.2 MB) |
| `Bestiary_2_Zoned_Heuristic_v1.zip` | `results/evidence.jsonl` (18 MB) |

The context arm's `verify.py` and its `execution.json` hashes refer to those
result files, so run verification from the archive, not from the expanded
folder. In the mechanical run folder, `match_evidence.jsonl` is stored zipped.

A local `.gitattributes` turns off line-ending conversion for this directory so
the hashes in each arm's freeze file keep matching on any checkout.

Response texts are not included in this directory beyond the short evidence
excerpts each arm records and the 84 held-out and three practice responses
embedded in the labelling page; the full texts remain in the releases.

## Record of this upload

The investigator first asked GPT to add the three packages to the repository;
that upload did not complete. Claude Fable 5.2 then received five files (three
archives and both reports), confirmed the three archives were byte-identical to
the ones it had already worked from, checked every file for personal
identifiers, and committed this directory.
