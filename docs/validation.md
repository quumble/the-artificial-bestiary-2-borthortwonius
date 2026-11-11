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

## November 11 changes (Claude Fable 5.2)

After the per-model stopping rule, three-set word loader, progress display, Claude's scorer 1.1 and `analyze_claude.py` were added, the full suite passed **48 tests** on Linux with Python 3.13.18 and NumPy 2.5.3. That NumPy is newer than the pinned 2.3.5; the pinned version was not re-tested in this environment.

New coverage:

- Study-phase issues are flagged and their slots closed without regeneration; an early issue does not stop a model; a model stops at the first point its issues pass 5% once 200 slots are closed; a changed identifier stops only that model; preflight still halts on any violation; an authentication failure still stops the run.
- The old 8 + 16 word layout is rejected and the three-label layout is accepted, with both model-made sets analysed as no-intent and the author label kept.
- Claude's analysis: all six tests on synthetic data with planted effects of known sign, Holm adjustment, determinism under the fixed seed, a missing model named beside the result, the known-word test left untested when that batch is absent, truncated responses excluded from the primary and kept in the sensitivity run, flagged records excluded, and the earliest duplicate kept.

A simulated full-size fresh batch (9,600 slots, in-memory stand-in) was also run to look at the progress display and the stopping rule. It is not part of the suite. With the minimum then set at 100, a stand-in model with a 2% issue rate was stopped by chance; that observation is why the minimum is 200.

Still unverified: everything listed above as unverified, plus the new code on Windows.

## GPT amendment and operational fixes, November 11, 2026

The complete offline suite passed **62 tests in 67.888 seconds** on Linux, Python **3.12.14** and the pinned **NumPy 2.3.5**:

```text
python -m unittest discover -s tests -v
Ran 62 tests
OK
```

New checks demonstrate:

- One-third source weights despite unequal eligible repetition counts; 50/25/25 sensitivity; both sets of missing bounds; fixed source composition under paired bootstrap; no reweighting away a missing source or required cell; matching weights in completion/inventory sensitivities.
- A deliberately constructed known/fresh example where the raw batch means differ solely because of intent composition, while the common-intent comparison correctly remains zero.
- Immediate identity stops when reasoning or malformed payloads occur simultaneously; stopping at a valid 200th closure; restart recovery of identity and threshold stops even after later in-flight successes lower the final issue fraction.
- Rejection of open-batch analysis before response access; selected-protocol, source/runtime and manifest checks; audits for wrong metadata, payloads, identities, issue flags and duplicate attempts.
- Claude model eligibility against the full frozen schedule when whole words have no eligible responses, plus report provenance and planned denominators.
- Combined-freeze rejection of a missing/stale Claude analyzer hash and acceptance of a matching synthetic commitment.

The synthetic two-batch integration still invokes the actual GPT analysis command with 50,000 bootstrap draws. Claude's entry point is exercised on synthetic data with explicitly reduced resampling counts recorded in its test report. No synthetic output is a study result or validation of the scorers' semantic interpretation.

The known-word dry run reports 800 trials per model across eight models and the unchanged committed known-word hash. `git diff --check` and every proposal-package SHA-256 check passed. The original GPT preregistration body is an unchanged byte prefix of its amended file. Claude's original preregistration, Amendment 1, both scorer versions, and the GPT scorer/specification/inventories are unchanged by this pass.

No paid API calls, actual study responses, private fresh-word file or credentials were used. Final private stimuli/hash, Fable's scientific choices and analyzer commitment, native Windows checks, live preflight and freeze remain outstanding. See [the final review handoff](fable-final-review.md).
