# The one-time rerun with zoned 1.1

18 November 2026. Investigator: Bo Chesterton. Analysis and report by Claude
Opus 5.5. This is the rerun declared in [FINAL_INSTRUMENT.md](../FINAL_INSTRUMENT.md):
the 225 declared rows, unchanged, with C = zoned 1.1.0 reported beside
C = zoned 1.0.0. Post hoc and exploratory; no p-values.

## How it ran

[`rerun_v1_1.py`](rerun_v1_1.py) runs the merged estimators unchanged, twice.
The first run uses the published rows. In the second, C is replaced by the 1.1
codes, which are verified against their hash, their execution receipt, and
every response hash and metadata field. Both runs use seed 20261115 and the
same 10,000 word draws. C 1.1 minus C 1.0 is computed draw by draw.

Two gates passed before any output was written:
- The 1.0 run reproduced every merged estimate and interval exactly. Rerunning
  the merged analysis in this environment also reproduced its published
  tables byte for byte.
- Every row that does not involve C was identical across the two runs.

Complete outputs are in [results/](results/): [tables](results/tables_v1_1.md),
all 225 rows with C = 1.1, the 132 C-only rows with paired differences,
direction status under both versions, and the execution receipt.

## Block 1

| Shape/outcome | C 1.0 | C 1.1 | C 1.1 minus C 1.0 |
|---|---:|---:|---:|
| G1.E imaginary minus real | 80.87 | 81.81 | +0.94 [0.56, 1.35] |
| G1.N | -74.41 | -78.40 | -3.99 [-4.90, -3.12] |
| G1.U | 40.31 | 40.83 | +0.52 [0.28, 0.80] |
| G2.E type-of minus real | 18.65 | 19.27 | +0.62 [0.03, 1.18] |
| G2.N | -14.17 | -17.85 | -3.68 [-4.65, -2.71] |
| G2.U | 7.67 | 8.12 | +0.45 [0.17, 0.76] |
| H2.N OpenAI type-of minus real | -24.86 | -29.24 | -4.38 [-5.76, -2.99] |
| H3.U | -1.85 | -2.03 | -0.18 [-0.55, 0.16] |
| H4.N | -1.65 | -2.43 | -0.78 [-2.32, 0.74] |
| H5.U | -7.19 | -6.67 | +0.52 [0.24, 0.83] |
| H6.N | 7.68 | 8.12 | +0.45 [-0.89, 1.79] |

Percentage points; brackets are 95% intervals on the paired difference.

**The direction status is unchanged for all eleven shapes.** The seven
framing rows remain `direction_robust`. H3, H4, H5 and H6 remain
`direction_unresolved`, for the same reasons as before. Every C interval keeps
its relation to zero.

**Against the expectation stated in advance:**
- No direction flipped, as expected.
- N moved most, as expected: by 3.7 to 4.4 points on G1, G2 and H2.
- E and U moved by less than a point, as expected.
- "Small relative to the intervals" held for E, U and H3 to H6. It did not
  fully hold for G1.N and G2.N. There the shift is larger than the half-width
  of the word-bootstrap interval, and the paired interval excludes zero.

## Block 2

121 zoned rows were compared. Two changed their relation to zero, and both
lower bounds were within 0.4 points of zero before:

| Row | C 1.0 | C 1.1 |
|---|---:|---:|
| Q2 describe anyway, type-of minus real, all endpoints | 1.56 [-0.00, 3.12] | 1.67 [0.31, 3.06] |
| Q3 bare share, Anthropic minus OpenAI (secondary tier) | 7.07 [-0.36, 13.39] | 7.63 [0.17, 13.88] |

As declared, these are reported as instrument sensitivity, not as new findings.

The largest movements were these. Response-type consistency for Claude Haiku
4.5 rose by 5.83 points on previously published words and 4.83 on fresh words. The
possibility-list share among GPT-5.4 mini's declines rose by 4.94. The rest
moved by 2.5 points or less. The single conditional interval is unchanged: Haiku
5.5's grounding share is still defined in 6,601 of 10,000 draws.

## What the rerun adds: C now separates from B on nonrecognition

Under 1.0, the zoned and registered instruments agreed on the N-based framing
contrasts. Under 1.1 they do not:

| B minus C | With C 1.0 | With C 1.1 |
|---|---:|---:|
| G1.N | 2.36 [0.83, 3.99] | 6.35 [4.79, 7.88] |
| G2.N | 0.73 [-1.01, 2.50] | 4.41 [2.85, 5.90] |
| H2.N | 0.49 [-1.81, 2.78] | 4.86 [2.57, 6.94] |

The 1.1 repairs that drive this added detected nonrecognition. The 41-item
human audit supported them over 1.0. If the registered Fable scorer misses the
same phrasings, the registered N-based effects, including H2, understate their
magnitudes by a few points. Their directions and Holm decisions would not
change.

### Check against the 41 labels (undeclared, run after the rerun)

At the investigator's request, the registered Fable v1.1 outputs (B) were
scored against the same 41 human labels
([`check_registered_on_core41.py`](check_registered_on_core41.py),
[output](results/registered_on_core41.json)). This was not part of the
declaration and adds no estimate to it.

| Outcome, correct of 41 (25 changed + 16 controls) | Registered | Zoned 1.0 | Zoned 1.1 |
|---|---:|---:|---:|
| E description | 33 | 29 | 37 |
| R any nonrecognition | 33 | 25 | 38 |
| N nonrecognition without description | 30 | 19 | 37 |
| U unmarked description | 40 | 37 | 41 |

The registered scorer sits between the two zoned versions. On the 19 responses
where 1.1 newly detected N and the reader agreed, the registered scorer had
already detected 11 and missed 8. Over all 28 responses the reader labelled N,
it missed 10: eight on real prompts and two on type-of prompts. Five of those
ten were plain misses of the nonrecognition statement. In the other five it
counted a description that the reader did not see.

Because the misses fall mostly on real prompts, they lower the registered N
rate there more than in the other frames. That shrinks the real-versus-imaginary
and real-versus-type-of gaps, which is the direction the inference predicts.
The check supports the direction. It cannot size the effect: the 41 were
selected on zoned disagreement, not on the registered scorer, and were read by
one person. The B minus C 1.1 gaps above remain the best available indication
of size, conditional on 1.1 being right about those responses.

## Bottom line

The framing account is unchanged under the final instrument. The repair makes
the nonrecognition contrasts somewhat larger and leaves everything else within
about a point. No registered decision changes. Zoned 1.1.0 remains the final
instrument for this corpus.
