# Artificial Bestiary 2 — response categorization heuristic (v1.0)

A **mechanical, no-LLM, auditable coding layer** for the published *Artificial Bestiary 2: Borthortwonius* study. This is a post-publication **additional categorization**, not a revision to its preregistrations, effect sizes, or significance tests. It works with the existing repository's exact feature definitions instead of independently reimplementing a similar but nonidentical regex scorer.

**Repository inspected:** https://github.com/quumble/the-artificial-bestiary-2-borthortwonius  
**Published run:** `gpt-v1+claude-v1.1`, November 11, 2026.  
**Original registered GPT outcomes:** M01, M02, M03, M09.  
**Original Fable outcomes:** E (description form), U (description form with no matched cue), N (nonrecognition with no description form).

## What it produces

1. `coded_responses.csv` — **one record per response/slot**, with registered GPT flags, registered Fable flags, a new exclusive `response_class`, auxiliary cues, scorer disagreements, condition metadata, and an eligibility column for each analysis family.
2. `match_evidence.jsonl` — match entries and positions for auditing. GPT positions are **raw-text spans**; Fable positions are **normalized-text spans** and must not be applied to raw text.
3. `descriptive_by_model_condition.csv` — counts and within-group rates. **Not** a preregistered inferential result.
4. `descriptive_by_word_cell.csv` — counts and rates at the **word × model × condition** level, preserving the word-level structure relevant to the study's bootstraps/permutations.
5. `coding_audit.json` — versions, SHA-256 hashes of input and upstream scoring files, flags for truncation eligibility and scorer origin.

No new API requests are issued. No manual or LLM judgment is used. The package does **not** contain the 16,000 published response texts; those remain distributed in the study's release. It will code them once you have the published export.

## Quick start

Requires Python 3.10+ and **no third-party packages** for this extra coding layer. The upstream original analyzer has its own stricter frozen runtime; see its README.

Obtain the [original repository](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius), along with either the analysis release containing `analysis/response-features.jsonl` or the raw-data release plus the **frozen source** used for exact reproduction. The repository's current `main` does not itself include expanded raw-data/analysis directories.

Unzip this folder, then run from the folder containing `code_responses.py`:

```bash
python code_responses.py \
  --repo /path/to/the-artificial-bestiary-2-borthortwonius \
  --input /path/to/the-artificial-bestiary-2-borthortwonius/analysis/response-features.jsonl \
  --out /path/to/output/bestiary2-coded
```

Windows PowerShell (one line):

```powershell
python code_responses.py --repo C:\path\to\the-artificial-bestiary-2-borthortwonius --input C:\path\to\the-artificial-bestiary-2-borthortwonius\analysis\response-features.jsonl --out C:\path\to\bestiary2-coded
```

**Recommended:** use the published `response-features.jsonl` as input. It already contains the audit-selected response and the GPT scorer's recorded features/match spans. This tool **preserves that embedded GPT scoring**, computes Fable v1.1 outcomes from the same raw response, and adds the derived categories. It does not independently select attempts from the raw ledger. It requires the upstream source files on disk to execute Fable v1.1 and record provenance.

To additionally re-score and verify every GPT match against the provided scorer implementation:

```bash
python code_responses.py --repo /path/to/repo --input /path/to/repo/analysis/response-features.jsonl --out /path/to/output --verify-embedded
```

To suppress matched **text excerpts** while retaining positions and lexicon entries, add `--redact-evidence`. Note that `coded_responses.csv` still contains the target word and other study metadata, but not the original full response.

For a small format demonstration, substitute `examples/synthetic_input.jsonl` as input. These are *invented illustrations*, not original study responses.

## Original measures versus proposed coding

| Layer | Output | Interpretation |
|---|---|---|
| **Registered GPT primary** | `M01`, `M02`, `M03`, `M09` (0/1) | Frozen any-match fiction / qualification / nonrecognition / exact-target definition-form outcomes; do **not** overwrite for new bins |
| **Registered Fable tests** | `F_E`, `F_U`, `F_N` (0/1) | Frozen description / unmarked description / nonrecognition without description outcomes (H1–H6 depend on these) |
| **New exploratory primary *taxonomy*** | `response_class` (six states, or `X_UNUSABLE`) | Exhaustive and mutually exclusive **summary** of Fable's E, nonrecognition, and cue flags; **not a confirmatory result** |
| **New exploratory secondary *tags*** | `S_*`, `secondary_tags` | Overlapping evidence flags for fiction, construction, interpretation, hedge, offers, local negation and other behaviors |
| **Agreement audit** | `gpt_definition_fable_E` | `BOTH`, `GPT_ONLY`, `FABLE_ONLY`, `NEITHER` — differences **in operational definition**, not a quality score |
| **Sensitivity** | `M01_without_imaginary`, `M02_modal_only` | Matches the existing GPT sensitivity definitions, useful for interpretation, not additional significance tests |

See [CODEBOOK.md](CODEBOOK.md) for exact category precedence, examples, missing data, eligibility, edge-case handling, and interpretation limits.

## Eligibility and missingness

- Usable = selected/terminal response with nonblank visible text. GPT primary flags remain available on any usable **observed prefix**, and `truncated` is retained. Unusable rows produce **blank** (not zero) outcome fields and `X_UNUSABLE`.
- Fable's original primary analysis excludes truncated records. Hence `fable_primary_eligible = 0` for truncated responses; the Fable *raw flags* and class label remain visible for transparent sensitivity work. For newly created ad-hoc CSV/JSONL without a `truncated` field, eligibility is **unknown** (blank), not silently assumed eligible.
- Nonterminal, invalid/issue rows are ineligible for coding, and the script does **not** repair or select ledger attempts. Use the repo's validated, selected export, not `data/attempts.jsonl`.
- Comparisons in the packaged descriptive CSVs use **ordinary within-group rates**, not the paper's one-third-per-origin pooled GPT estimate, word-cluster bootstrap, Fable Holm-adjusted permutation tests, or any claims about exposure/ownership. For those, run/read the **original `analyze_bestiary.py` and `analyze_claude.py`** outputs.
- A row with `F_U = 1` also has `F_E = 1`. `F_N = 1` precludes `F_E = 1`. **E/U/N are NOT three mutually exclusive categories**. `response_class` is a separate partition that solves this for descriptive cross-tabs.

## Quality checks

Run the supplied synthetic unit tests:

```bash
python -m unittest discover -s tests -v
```

The suite tests the **categorization and I/O rules** via controlled, simulated scorer outputs. The optional upstream integration test runs with actual original regex implementations when you provide:

```bash
BESTIARY2_REPO=/path/to/repo python -m unittest discover -s tests -v
```

PowerShell: `$env:BESTIARY2_REPO='C:\path\to\repo'; python -m unittest discover -s tests -v`.

The synthetic tests are *not* an independent semantic validation and do not establish annotation accuracy. They do assert the algebra of E/U/N, the exhaustive partition, truncation exclusions, original-score preservation, and key discrepancy cases. For an external semantic validation, pre-register an annotation protocol, mask endpoint/source/condition predictions where appropriate, and use a held-out sample.

## Scope and provenance

The repository describes **16,000 completed responses** across eight endpoints and ten conditions. The GPT primary family contains eight contrasts (four measures × two framing comparisons) on the fresh bank; the Fable family tests H1–H6 with independently defined measures. They are not independent replications because they use the same responses. The repo explicitly cautions against treating text patterns as model beliefs, truth, hallucination, or training exposure. This coding layer makes no such claims.

Reference implementation paths in the original repo:

- `bestiary_scorer.py`, `docs/gpt-proposal/inventories-gpt-v1.json` — GPT exact-match feature source.
- `prereg/claude_scorer_v1_1.py`, `prereg/CLAUDE_PREREG_AMENDMENT_1.md` — amended Fable primary scorer.
- `analyze_bestiary.py` — original GPT primary (M01/M02/M03/M09), secondary summaries and frozen-run checks.
- `analyze_claude.py` — original confirmatory Fable H1–H6 (E/U/N), exclusions, weighting, tests.

See also [METHOD_AND_PROVENANCE.md](METHOD_AND_PROVENANCE.md).
