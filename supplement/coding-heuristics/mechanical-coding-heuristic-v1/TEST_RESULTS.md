# Test report

Date: 2026-11-15

Command: `python -m unittest discover -s tests -v`

**13 synthetic tests passed; 1 optional upstream-integration test skipped** because the repository's original source files were not present in the build container. Unit tests use deliberately controlled fake scorer outputs to test the *new coding algebra and I/O*, **not** to claim any independently validated pattern recognition accuracy.

Recommended after downloading the original repository:

```bash
BESTIARY2_REPO=/path/to/the-artificial-bestiary-2-borthortwonius python -m unittest discover -s tests -v
python code_responses.py --repo /path/to/the-artificial-bestiary-2-borthortwonius --input examples/synthetic_input.jsonl --out example-coded --verify-embedded
```

For the real 16,000-response run, replace the synthetic input with the released `analysis/response-features.jsonl`. The original preregistered analysis outputs must remain the inferential reference.
