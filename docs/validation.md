# Pre-collection implementation validation

The repaired collector, literal scorer and analysis passed **37 automated tests** in Python 3.12.14 with NumPy 2.3.5 on Linux. The final suite completed in 51.493 seconds. These are software-contract and synthetic integration checks, not validation of semantic constructs or live provider behavior.

```text
python -m unittest discover -s tests -v
Ran 37 tests
OK

python run_bestiary.py run known --dry-run
known 800 trials/model; 8 models
word SHA-256 ee338d944aa0c6e2de68ce18c8a38af1eb3de34790ab87828f2afe6f9eb0dfe2
```

The end-to-end fixture uses an in-memory provider stand-in, eight model identifiers, a synthetic 24-word fresh file and the eight public known words. It temporarily reduces repetitions to one for that test only, collects 2,560 synthetic study responses plus eight preflight responses, then invokes the actual analysis command with 50,000 bootstrap draws. The production defaults remain five and ten repetitions, with 9,600 fresh and 6,400 known planned responses. A separate freeze test verifies those full counts.

Coverage includes structured refusals, visible block boundaries, failed HTTP-200 generations, unknown schemas, empty/truncated terminal outputs, immutable preflight settings, alias resolution and identity drift, reasoning violations, restart-persistent retry limits, ambiguous charges, billing reconciliation, competing reservations, process locking, source/word hash mismatches, legacy-data rejection, and rebuilding a corrupted JSONL export from the durable database.

Scoring checks cover normalization and raw-span reconstruction, phrase boundaries, contractions, negation, quotation, prompt contamination, definition/cue order, incomplete/null text, formatting, source forms, numeric units, duplicate denominators, target masking and length-window eligibility. Analysis checks exercise unequal repetition counts and unequal source-set sizes, missing-cell null estimates, missing/completion bounds, complete-only eligibility, duplicate/wrong-request auditing, deterministic resampling and serializable secondary outputs.

The independently delivered GPT proposal files are preserved byte for byte in `docs/gpt-proposal/`. No private fresh words, credentials, new-study responses or provider calls were used. Git whitespace checks passed. The live repository data directory was not created during development; all test ledgers were temporary.

Still unverified: live API access on the investigator's accounts, the withheld file's bytes, native Windows execution, and independent reproduction of Claude's historical development metrics. Windows locking is implemented using the standard library, and `.gitattributes` preserves LF file bytes on Windows checkouts, but that is not a Windows test result. Re-run the test command in the actual collection environment before freezing it.

## Claude attachment integration

The original Bestiary preregistration and scorer were added on November 11, 2026. Both match the uploaded bytes. The scorer matches the SHA-256 registered in the original document. Their hashes are now included in the pre-run freeze manifest without changing the selected analysis protocol.

Additional offline tests check the immutable attachment hashes, the documented synthetic scorer boundary cases, and the scorer CLI against terminal JSONL exported by the repaired collector. These establish file integrity and basic compatibility, not measurement validity. No historical development dataset or actual study response was used. See `docs/claude-review.md` for the remaining analysis work.

After integration, the full suite passed **40 tests in 50.562 seconds** on the same Linux/Python/NumPy environment, including the synthetic two-batch analysis. The original scorer contains one trailing space; it is retained to preserve the registered hash. Whitespace checks pass for the other changed files.
