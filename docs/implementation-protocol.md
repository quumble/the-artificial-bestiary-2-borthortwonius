# Implementation protocol and pending analyst comparison

Status: pre-collection implementation. No study calls were made while developing this change. The source baseline is `c00aab0e9902ee000b2e9d256dcf09b20c21c823`.

The original GPT proposal and review are preserved unchanged in `docs/gpt-proposal/`. Its literal 32-family scorer and analysis are implemented by `bestiary_scorer.py` and `analyze_bestiary.py`. This file records implementation details and does not claim that the investigator has adopted this protocol over Claude's independent proposal. `freeze --protocol gpt-v1` explicitly selects the implemented proposal and records exact source and test hashes before study collection. No freeze or model request is performed merely by installing or testing this code.

## Collector corrections

- SQLite is the authoritative durable attempt ledger. A reservation commits before every dispatch, and a result commits afterward. JSONL files are derived atomic exports. A torn export can be regenerated from SQLite. Do not remove the SQLite database or its WAL/SHM sidecars while a collector is running. Back up the data directory with the collector stopped.
- The collector uses a process lock with Linux `flock` or Windows `msvcrt.locking`. One collector operates a data directory at a time. The OS releases the lock after a crash. A stale file is harmless and should not be deleted to bypass an active lock.
- All provider payloads are retained, with visible refusal text extracted and block boundaries preserved by newline joins. Only known terminal statuses are accepted. API failures do not become successful outcomes merely because HTTP returned 200.
- One compliant request configuration per model is supported. There are no reasoning-on or temperature-removal fallbacks. Documented date-suffixed snapshots may resolve aliases during preflight. Any later model-identifier change or observed reasoning causes a persistent protocol halt. Do not clear that halt by hand; retain the evidence and document an amendment.
- Preflight is idempotent and billed in the ledger. Re-running it does not overwrite accepted settings or make another successful check call. Study retries are capped at six attempts per slot across restarts, preflight at four. Valid refusals, empty answers and truncations are terminal and are not regenerated. Hard errors require review, except authentication failures may be retried after credentials are corrected.
- Costs use integer nanodollars, rounded upward. Unknown transport/HTTP charges retain their full reservation across restarts. `reconcile ATTEMPT_ID --usd AMOUNT --note "billing evidence"` creates an audit entry. It does not reopen a provider already stopped by its budget.
- The input reservation is the UTF-8 request-byte count plus a conservative 4,096-token framing allowance, not a provider-certified mathematical token bound. Usage exceeding it causes a halt. The output reserve is 1,024 tokens. The $20 stop is based on a conservative accounting estimate, not a guarantee about provider invoicing or undisclosed price changes. Verify prices and account billing before launch.
- A budget stop is permanent for the registered collection. Exhausted retries remain missing slots. Fresh closes only after its lanes finish or budget-stop; known cannot start earlier. A technical interruption leaves the batch open for identical-manifest resume. A lane failure cancels further dispatch while in-flight calls are saved.
- Existing legacy JSONL data without the new database triggers a migration error. This patch does not guess costs or silently import old outcomes. The supplied baseline was pre-run, so no migration was needed here.
- The private fresh file's exact committed hash is mandatory. Its eight-member source set is mapped to `fresh-animal-intent`, its sixteen-member set to `fresh-no-intent`; original source labels remain recorded. This handles private label spelling without changing committed bytes or guessing word membership. Known labels are checked literally. The private file was unavailable during development.
- Frozen files, stimulus bytes, model configurations and Python/NumPy versions must match on resume and analysis. The private manifest contains every ordered trial and is itself hashed. All `data/` and `analysis/` outputs are ignored by Git until deliberate release.

## Measurement implementation clarifications

The normative definitions are the unmodified GPT proposal, measurement appendix and inventories. Group measures M26–M28 are emitted at cell/word-pair level, not invented as response-level values. Match records and raw spans remain available. Per-term dictionaries are sparse (absent entry means zero within a usable response); numeric summary tables exclude those sparse dictionaries and retain the full entry counts in response-level data.

Number-plus-unit pairs (M23) do not bridge sentence-like segment boundaries. This is a conservative clarification of the appendix's consecutive-token rule and is recorded before collection. Prefix sensitivity measures cut at the end of the 50th/100th token and retain only responses long enough for that window.

All eight fresh primary estimates use the specified equal model/category/source-set/word weighting. Missing required cells make the corresponding full-panel estimate null. Bounds still cover all planned slots. Bootstrap intervals are paired, stratified word-resampling intervals, not a claim of representative sampling. Only the eight primary fresh contrasts use the adjusted 99.375% intervals. Known-word estimates and the remaining analyses are descriptive. Empty outputs are null behavioral observations, while a usable incomplete prefix has valid observed matches and a preserved incompletion flag.

## Claude proposal: original files received and reviewed

The Bestiary-specific files are now preserved byte for byte at `prereg/CLAUDE_PREREG.md` and `prereg/claude_scorer.py`. The scorer's SHA-256 matches the commitment in the preregistration. Both original files are included in the collection freeze manifest as provenance. Their inclusion does not adopt Claude's hypothesis tests or change the implemented `gpt-v1` analysis.

The [review of the actual files](claude-review.md) supersedes the earlier summary-only assessment. It records synthetic scorer checks, the missing hypothesis-analysis script, H4's unresolved equivalence procedure, denominator ambiguities, and limits on confabulation/exposure interpretations. Reported historical development metrics have not been independently reproduced.

The two proposals retain their own measures, denominators and multiplicity procedures. Before a joint confirmatory registration, specify whether error control applies separately to each family or to all adopted claims together. Two families controlled separately at five percent do not provide five-percent error control for their union. No new-study output was inspected during this review, and neither frozen proposal was edited.

## Commands (native Windows or other Python environment)

```text
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -v
python run_bestiary.py run known --dry-run
python run_bestiary.py check
python run_bestiary.py freeze --protocol gpt-v1
python run_bestiary.py run fresh
python run_bestiary.py run known
python analyze_bestiary.py
```

`check` makes paid content-neutral calls. The two `run` commands make paid study calls. Tests and `--dry-run` make none. Do not run the paid commands until protocol selection is settled and the private stimulus file and provider keys are present locally. Keys remain in environment variables or ignored `keys.local`. The frozen manifest records installed dependency versions. A fresh installation should use the same pinned NumPy version as the tested environment listed in `requirements-analysis.txt`.

The full attempt ledger, request payloads, raw responses and fresh-word manifest stay private until both batches finish or are formally stopped. Public release is a separate explicit action. No semantic labels or experimental results were generated during implementation.
