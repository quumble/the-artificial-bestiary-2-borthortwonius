"""Offline review probes for the c00aab0 runner. No network or real keys.

Usage: python offline_review_checks.py /path/to/run_bestiary.py
PASS means a review observation was reproduced, not that the bug is fixed.
All writes use a temporary directory. The supplied source is not changed.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runner", type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("runner_under_review", args.runner)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    results = []

    def record(name, observation, passed):
        results.append(dict(check=name, reproduced=bool(passed), observation=observation))

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        mod.ROOT = root
        mod.DATA = root / "data" / "raw"
        mod.STIM = root / "stimuli"
        mod.STIM.mkdir()
        mod.VARIANTS_FILE = mod.DATA / "request-settings.json"
        mod.load_keys = lambda: {"OPENAI_API_KEY": "FAKE", "ANTHROPIC_API_KEY": "FAKE"}
        mod.say = lambda *a, **k: None
        mod.post_json = lambda *a, **k: (_ for _ in ()).throw(AssertionError("unmocked request"))

        words = [("known-animal-intent", "borthorpunius"), ("known-no-intent", "flembrast")]
        trials = mod.build_trials("known", words, 10)
        record("trial construction", {"trials": len(trials), "unique_ids": len({t["trial_id"] for t in trials}),
               "vowel_prompt": mod.build_prompt("avelo", "imaginary", "animal")},
               len(trials) == 200 and len({t["trial_id"] for t in trials}) == 200
               and mod.build_prompt("avelo", "imaginary", "animal") == "Describe an avelo. It is an imaginary animal.")

        captured = []
        def stub(url, headers, body):
            captured.append(body)
            return 200, {"id": "synthetic-refusal", "model": "gpt-6-sol", "status": "completed",
                         "output": [{"type": "message", "content": [
                             {"type": "refusal", "refusal": "I cannot help with that request."}]}],
                         "usage": {"input_tokens": 10, "output_tokens": 9}}, {}
        mod.post_json = stub
        model = mod.MODEL_BY_ID["gpt-6-sol"]
        status, fields = mod.call_model(model, model["variants"][0], "synthetic prompt", "FAKE")
        record("structured refusal discarded", fields, fields["response"] == "" and fields["error"] is None)
        mod.call_model(model, model["variants"][-1], "synthetic prompt", "FAKE")
        record("reasoning fallback cap is total 5120", captured[-1], captured[-1]["max_output_tokens"] == 5120)

        def failed_stub(*a, **k):
            return 200, {"id": "synthetic-failed", "model": "gpt-6-sol", "status": "failed",
                         "error": {"code": "server_error", "message": "synthetic"}, "output": []}, {}
        mod.post_json = failed_stub
        _, fields = mod.call_model(model, model["variants"][0], "synthetic prompt", "FAKE")
        record("HTTP 200 failed status marked error-free", fields,
               fields["error"] is None and fields["stop_reason"] == "failed")

        tail = root / "tail.jsonl"
        tail.write_text('{"trial_id":"cut', encoding="utf-8")
        with tail.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"trial_id": "new", "error": None}) + "\n")
        rows = mod.read_records(tail)
        record("append after torn tail hides next record", {"parsed_records": rows}, rows == [])

        mod.STIM.joinpath("fresh-words.txt").write_text("unrecognized-set changedword\n", encoding="utf-8")
        loaded, digest = mod.load_words("fresh")
        record("wrong fresh hash and composition accepted", {"words": loaded, "sha256": digest},
               loaded == [("unrecognized-set", "changedword")])

        def synthetic_call(*a, **k):
            return 200, {"response": "ready", "model_returned": "gpt-6-sol", "response_id": "synthetic-ready",
                         "reasoning_tokens": 0, "thinking_blocks": None, "input_tokens": 5,
                         "output_tokens": 1, "visible_output_tokens": 1, "stop_reason": "completed",
                         "truncated": False, "error": None, "est_cost_usd": 0.01, "cap_sent": 1024}
        mod.call_model = synthetic_call
        mod.cmd_check(SimpleNamespace(models=["gpt-6-sol"]))
        record("preflight cost absent from ledger", mod.spend_on_disk(), mod.spend_on_disk()["openai"] == 0)

        out = mod.DATA / "known"
        out.mkdir()
        mod.STIM.joinpath("known-words.txt").write_text("known-no-intent flembrast\n")
        ts = mod.build_trials("known", [("known-no-intent", "flembrast")], 1)
        wrong = [dict(t, prompt="STALE PROMPT", error=None, request_settings="STALE SETTINGS",
                      model_requested="gpt-6-sol", response="synthetic", provider="openai") for t in ts]
        (out / "gpt-6-sol.jsonl").write_text("".join(json.dumps(t) + "\n" for t in wrong))
        calls = []
        mod.call_model = lambda *a, **k: calls.append(1) or synthetic_call()
        mod.cmd_run(SimpleNamespace(batch="known", reps=1, models=["gpt-6-sol"], dry_run=False,
                                   limit=None, spend_cap=20, workers=1, status_every=999))
        record("resume skips records with stale prompt and settings", {"new_calls": len(calls)}, len(calls) == 0)

        changed = {"gpt-6-sol": {"variant": "reasoning-low", "checked_utc": "OLD",
                                  "model_returned": "old-returned-id", "reasoning_observed": True}}
        mod.VARIANTS_FILE.write_text(json.dumps(changed))
        mod.cmd_check(SimpleNamespace(models=["gpt-6-sol"]))
        locked = mod.load_variants()
        record("check overwrites settings despite existing study files", locked,
               locked["gpt-6-sol"]["variant"] == "reasoning-none+temperature-1.0")

    print(json.dumps(results, indent=2))
    return 0 if all(r["reproduced"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
