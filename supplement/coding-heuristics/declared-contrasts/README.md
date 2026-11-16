# Reproduce the comparisons and declared exploratory analyses

This workflow reads the three frozen instruments' published response codes,
reproduces the existing three-way and human-pass comparisons, and computes the
declared exploratory estimates. It requires no provider keys, model calls,
raw response text, private intermediate files, or manual archive extraction.

Read the [results report](REPORT.md) for interpretation and the
[complete tables](results/tables.md) for every reported estimate. The
[declaration and implementation clarification](DECLARATION.md) govern the
calculations. The clarification was committed before the new estimates at
[`a73a37f539f3dd99e84f256f7bdf8d2713838120`](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/commit/a73a37f539f3dd99e84f256f7bdf8d2713838120).

## Run from the repository root

Install the numerical dependency pinned in the repository's requirements:

```text
python -m pip install -r requirements-analysis.txt
```

This installs NumPy 2.3.5. The remaining dependencies are Python's standard
library. This supplement was executed with Python 3.12.14 and NumPy 2.3.5;
the full runtime is recorded in the receipt. It analyzes already exported
codes and is separate from exact replay of the original frozen analyses,
which retains the original manifest's runtime requirements.
The commands below write replay outputs to the Git-ignored
`analysis/coding-heuristics-replay/` directory, preserving the committed results.

First reproduce the published comparison summaries:

```text
python supplement/coding-heuristics/declared-contrasts/reproduce_comparisons.py --output analysis/coding-heuristics-replay/reproduction.json
```

The script verifies every reported field against the saved three-way and
human-pass outputs and exits unsuccessfully if any comparison fails. It also
recalculates agreement between the human and model readers. These historical
summaries retain their original response-level and holdout-sampling weights;
they are distinct from the new word-weighted analyses.

Then run the declared analyses:

```text
python supplement/coding-heuristics/declared-contrasts/run_analysis.py --out analysis/coding-heuristics-replay
```

Check nine selected estimates and both interval endpoints using a separate
implementation that reads the published CSVs directly and imports none of
the analysis modules:

```text
python supplement/coding-heuristics/declared-contrasts/check_selected_estimates.py --estimates analysis/coding-heuristics-replay/estimates.json --output analysis/coding-heuristics-replay/independent_check.json
```

This is a numerical cross-check of selected results, not an independent
replication of the study. It requires the adjacent execution receipt and the
declared default bootstrap settings.

The defaults are **10,000 bootstrap draws**, seed **20261115**, NumPy PCG64,
and linear 95% percentile intervals. `--draws` and `--seed` are exposed for
diagnostics; changing them does not reproduce the declared run. The script
records the runtime, input and source hashes, word ordering, shared draw
identity, and output hashes in its execution receipt.

Both scripts locate the repository from their own paths. For an alternate
checkout, use `--repo-root` for comparison reproduction or `--root` for the
analysis. With no output argument, they write to this folder's `results/`.
The analysis refuses to replace any existing analysis output unless
`--overwrite` is supplied. The comparison script replaces its selected
`--output` JSON file. Prefer a new replay directory when preserving an earlier
run matters.

## Outputs and implementation

| File | Contents |
| --- | --- |
| [results/reproduction.json](results/reproduction.json) | Rebuilt historical comparisons, reader agreement, input provenance, and match diagnostics |
| [results/specifications.json](results/specifications.json) | Every reporting row's selection, terms, coefficient signs, and tier |
| [results/estimates.json](results/estimates.json) | Estimates, intervals, component rates, missing-value support, denominator information, and undefined-draw counts |
| [results/estimates.csv](results/estimates.csv) | Compact numerical table; rates and differences are stored as fractions |
| [results/tables.md](results/tables.md) | Readable tables; rates are percentages and differences are percentage points |
| [results/interpretation.json](results/interpretation.json) | Block 1 direction summaries and paired instrument differences |
| [results/execution.json](results/execution.json) | Completed-run receipt, hashes, runtime, bootstrap settings, and consistency checks |
| [results/independent_check.json](results/independent_check.json) | Separate numerical cross-check of nine selected estimates and intervals |
| [inputs.py](inputs.py) | Validates and joins the published records, reading the context codes directly from their ZIP |
| [estimation.py](estimation.py) | Nested estimators, source-stratified word bootstrap, support accounting, and interpretation rules |
| [contrasts.py](contrasts.py) and [questions.py](questions.py) | Explicit Block 1 and Block 2 specifications |

The frozen scripts and archives remain historical records. These reproducible
counterparts replace the need for unpublished joins and hardcoded workspace
paths without modifying any frozen package, registered scorer, or original
analysis output.

## Estimands and interpretation

There are **225 reporting rows**: 66 Block 1 rows and 159 Block 2 rows. These
include instrument versions, paired instrument differences, and component
rates. They are **not 225 independent tests**. H1 is an alias of G1/E and is
not counted again. The primary tier covers the declared description and
declining questions; U outcomes and Questions 3, 5, and 8 belong to the
secondary tier because they depend on marking.

The estimator averages resolved repetitions within a condition, conditions
within an endpoint, endpoints within a word, and words within source strata.
It retains the declaration's fixed source weights, including equal intent
weights for H4. Whole words are resampled within strata, carrying all their
endpoints, conditions and repetitions together. The same draws are used
across instruments and contrasts. Repetition consistency averages each
cell's unordered-pair agreement proportion rather than pooling pair counts.

Null repetitions are omitted; empty cells and unavailable word support are
reported. Within-word contrasts pair usable words within each instrument.
Instrument differences preserve each instrument's own available-case
estimator, so differences involving A can reflect both coding and unresolved
support. Conditional rates divide weighted numerator rates by weighted
denominator rates. Group contrasts subtract the resulting group ratios.
Zero denominators or empty required strata yield undefined estimates or
bootstrap draws, never zero rates. An interval calculated after omitting
undefined draws is explicitly flagged as conditional on defined draws.

All results are post hoc and exploratory. Intervals are unadjusted, with no
p-values, multiplicity-control claims, or replacement of registered results.
Common direction and differences in magnitude are reported separately.
An interval containing zero establishes neither an instrument effect nor
equivalence. The intervals describe word-resampling variation for the fixed
endpoints and frozen detectors; they do not incorporate detector error.
