# Final instrument and the v1.1 rerun

Declared 18 November 2026, before any declared contrast was computed with
zoned heuristic 1.1. Investigator: Bo Chesterton. Written by Claude Opus 5.5.
Post hoc and exploratory, like the [declaration](DECLARATION.md) it extends.

## Decision

1. **Zoned heuristic 1.1.0 is the final coding instrument for Bestiary 2.** No
   further version will be built or tuned on these 16,000 responses. This
   includes any version built from the residual errors in the
   [41-item human audit](../zoned-heuristic-v1-1/quick/RESULTS.md).
2. **The declared list is rerun once, unchanged, with C = zoned 1.1.0.** A
   (context 1.0.0) and B (registered Fable v1.1 outputs) are unchanged. Every
   estimator, weight, missing-value rule, the bootstrap (10,000 draws, seed
   20261115, the same draw indices), and the interpretation rule are those of
   the declaration and its
   [pre-computation clarification](https://github.com/quumble/the-artificial-bestiary-2-borthortwonius/commit/a73a37f539f3dd99e84f256f7bdf8d2713838120).
3. **Both C results are reported side by side.** The merged results under zoned 1.0.0
   remain the baseline and are not replaced. The rerun adds C = 1.1 estimates,
   their intervals, and paired differences between C 1.1 and each of A, B and
   C 1.0, using shared draws.
4. **Known residual defects are reported as limitations, not fixed.** These are the
   explicit-correction cue overfiring on substitution, soft fiction words,
   habitual "may" counted as a hedge, late section labels counted as marks,
   and substitution by respelling or alias. Substitute descriptions stay out of
   the analyses, as the declaration already deferred them.
5. **Instrument changes belong to a new study.** Any improvement is frozen
   before a new collection, not tested on this corpus.

## Inputs

- C 1.1 codes: `zoned-heuristic-v1-1/results/response_codes.csv`, SHA-256
  `ea071089abc9467e721d0e2d3cea25b25e646263ce3eed6ed737737bbc4dd237`. This
  matches its execution receipt (version `bestiary2-zoned-heuristic/1.1.0`,
  freeze commit `3d8b4c35961fbdfb6ca88084dab3c63b9d4df03b`, n = 16,000). The
  file has the same 34 columns as 1.0.0.
- The merged loader reads zoned 1.0.0 only. The rerun adds a separate input
  step that verifies the 1.1 codes against that receipt and the response
  hashes, then hands them to the existing estimators. The merged code, frozen
  archives and existing results are not edited.

## Expectation stated in advance

Between versions, 1.61% of responses change, mostly by adding detected
nonrecognition among the GPT-5.4 endpoints and Claude Haiku 4.5. The C
estimates are expected to move most for outcomes built on N and least for E
and U, and by small amounts relative to the word-bootstrap intervals. No
framing-direction flip is expected. If a direction flips, or an interval's
relation to zero changes, that is reported as instrument sensitivity. It is
not a reason for another version.
