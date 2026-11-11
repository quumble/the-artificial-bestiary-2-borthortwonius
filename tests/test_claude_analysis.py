import copy
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

import numpy as np

import analyze_claude as a
import run_bestiary as r

CONDITIONS = ["neutral"] + a.REAL + a.IMAG + a.TYPE


def words():
    fresh = [("fresh-animal-intent", "zuvem" + c, "fresh-animal-intent") for c in "abcdefgh"]
    fresh += [("fresh-no-intent", "fepal" + c, "fresh-no-intent-claude") for c in "abcdefgh"]
    fresh += [("fresh-no-intent", "dorix" + c, "fresh-no-intent-gpt") for c in "abcdefgh"]
    known = [("known-animal-intent", "kanim" + c, "known-animal-intent") for c in "abcd"]
    known += [("known-no-intent", "knone" + c, "known-no-intent") for c in "abcd"]
    return {"fresh": fresh, "known": known}


def text(model, batch, word, word_set, source, condition):
    describe = "A %s is a small thing. It has a handle." % word
    deflect = "I don't recognize %s." % word
    current, openai = model in a.CURRENT, model in a.OPENAI
    if condition in a.IMAG:
        return describe
    if condition in a.TYPE:
        if current:
            return deflect                                  # H5: current models describe less
        if word_set.endswith("animal-intent"):
            return describe                                 # H3: animal-intent words draw more unmarked description
        return "It might be many things." if openai else deflect   # H2: OpenAI drops bare non-recognition under type-of
    if condition in a.REAL and batch == "known" and current:
        return describe                                     # H4: known words lose non-recognition on current models
    if condition == "neutral" and source.endswith("-claude") and not openai:
        return describe                                     # H6: Claude-made words on Anthropic models
    return deflect


def save_manifest(root, manifest):
    manifest.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = r.digest(r.canonical(manifest).encode())
    (root / "data" / "freeze.json").write_text(json.dumps(manifest), encoding="utf-8")


def write_attempts(root, attempts):
    (root / "data" / "attempts.jsonl").write_text(
        "".join(json.dumps(attempt) + "\n" for attempt in attempts), encoding="utf-8")


def build(root, skip_model=None, with_known=True, truncate_imaginary=False, keep_fresh_words=None):
    """A complete frozen schedule with synthetic attempt-ledger records, never provider calls."""
    (root / "data").mkdir(parents=True, exist_ok=True)
    names = ["run_bestiary.py", "bestiary_scorer.py", "analyze_bestiary.py", "requirements-analysis.txt",
             "docs/implementation-protocol.md", "docs/gpt-proposal/PREREGISTRATION_GPT.md",
             "docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md", "docs/gpt-proposal/inventories-gpt-v1.json",
             "prereg/CLAUDE_PREREG.md", "prereg/claude_scorer.py"] + r.CLAUDE_FILES
    for name in names:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(r.ROOT / name, target)
    manifest = dict(protocol="gpt-v1+claude-v1.1", python=sys.version, numpy=np.__version__,
                    code_hashes={name: r.digest((root / name).read_bytes()) for name in names},
                    batches={}, settings={model["id"]: dict(model_config=model, model_returned=model["id"])
                                         for model in r.MODELS})
    attempts = []
    for batch, bank in words().items():
        trials = r.build_trials(batch, bank)
        manifest["batches"][batch] = {}
        kept = {entry[1] for entry in bank[:keep_fresh_words]} if keep_fresh_words is not None else None
        for model in r.MODELS:
            manifest["batches"][batch][model["id"]] = trials
            if model["id"] == skip_model or batch == "known" and not with_known:
                continue
            for trial in trials:
                if batch == "fresh" and kept is not None and trial["word"] not in kept:
                    continue
                body = r.payload(model, trial["prompt"])
                ordinal = len(attempts) + 1
                truncated = truncate_imaginary and trial["condition"] in a.IMAG
                attempts.append(dict(id=ordinal, attempt_id=str(ordinal), phase=batch, model=model["id"],
                                     trial_id=trial["trial_id"], trial=trial, request=body,
                                     request_hash=r.digest(r.canonical(body).encode()),
                                     fields=dict(terminal=True, valid=True, error=None, model_returned=model["id"],
                                                 truncated=truncated, complete=not truncated,
                                                 response=text(model["id"], batch, trial["word"], trial["word_set"],
                                                               trial["source_set_label"], trial["condition"]))))
    save_manifest(root, manifest)
    write_attempts(root, attempts)
    # An empty known batch may be formally closed after a budget/model stop.
    (root / "data" / "collection-status.json").write_text(json.dumps({batch: {"closed_utc": "synthetic"} for batch in a.REPS}))
    return manifest, attempts


class ClaudeAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scorer = a.load_scorer("claude_scorer_v1_1.py")

    def tearDown(self):
        self.temp.cleanup()

    def run_family(self, **kwargs):
        include = kwargs.pop("include_truncated", False)
        manifest, _ = build(self.root, **kwargs)
        rows, audit = a.load_rows(self.root, self.scorer)
        self.manifest = manifest
        return a.confirmatory(a.Data(rows, manifest, include_truncated=include), permutations=2000, bootstraps=400), rows, audit

    def test_six_tests_have_registered_directions_and_holm(self):
        res, rows, audit = self.run_family()
        self.assertEqual(len(rows), 8 * (24 * 10 * 5 + 8 * 10 * 10))
        self.assertEqual(audit["ineligible"], 0)
        self.assertEqual(sorted(res), ["H1", "H2", "H3", "H4", "H5", "H6"])
        self.assertAlmostEqual(res["H1"]["estimate"], 1.0)
        self.assertEqual(res["H1"]["n_words"], 24)
        self.assertLess(res["H2"]["estimate"], 0)
        self.assertGreater(res["H3"]["estimate"], 0)
        self.assertLess(res["H4"]["estimate"], 0)
        self.assertLess(res["H5"]["estimate"], 0)
        self.assertLess(res["H6"]["estimate"], 0)
        for key in res:
            self.assertGreaterEqual(res[key]["p_holm"], res[key]["p"])
            self.assertLessEqual(res[key]["ci95"][0], res[key]["ci95"][1])
        self.assertTrue(res["H1"]["confirmed_at_0.05"])
        again, _, _ = (a.confirmatory(a.Data(rows, self.manifest), permutations=2000, bootstraps=400), None, None)
        self.assertEqual(again["H3"]["p"], res["H3"]["p"])            # deterministic under the fixed seed

    def test_missing_model_is_named_and_known_absent_leaves_h4_untested(self):
        res, _, _ = self.run_family(skip_model="gpt-6-luna", with_known=False)
        self.assertIn("gpt-6-luna", res["H1"]["models_missing"])
        self.assertIsNotNone(res["H1"]["estimate"])
        self.assertIsNone(res["H4"]["estimate"])
        self.assertIn("untested", res["H4"]["note"])
        self.assertIsNone(res["H4"]["p_holm"])

    def test_truncated_excluded_from_primary_and_kept_in_sensitivity(self):
        res, rows, _ = self.run_family(truncate_imaginary=True)
        self.assertIsNone(res["H1"]["estimate"])                      # every imaginary response was cut off
        sens = a.confirmatory(a.Data(rows, self.manifest, include_truncated=True), permutations=500, bootstraps=200)
        self.assertAlmostEqual(sens["H1"]["estimate"], 1.0)

    def test_flagged_records_are_ineligible_and_earliest_duplicate_wins(self):
        _, attempts = build(self.root)
        first = attempts[0]
        flagged = copy.deepcopy(first)
        flagged.update(id=0, attempt_id="flagged")
        flagged["fields"]["issue"] = "reasoning_observed_in_reasoning_off_run"
        later = copy.deepcopy(first)
        later.update(id=len(attempts) + 1, attempt_id="later")
        later["fields"]["response"] = "A %s is a small thing. It has a handle." % first["trial"]["word"]
        write_attempts(self.root, attempts + [flagged, later])
        rows, audit = a.load_rows(self.root, self.scorer)
        self.assertEqual(audit["ineligible"], 1)
        self.assertEqual(audit["duplicates"], 1)
        self.assertEqual(len(rows), 8 * (24 * 10 * 5 + 8 * 10 * 10))
        retained = next(row for row in rows if row["model"] == first["model"] and row["word"] == first["trial"]["word"]
                        and row["condition"] == first["trial"]["condition"] and row["rep"] == first["trial"]["rep"])
        self.assertEqual(retained["N"], 1)

    def test_rejects_either_open_batch_before_reading_or_scoring(self):
        build(self.root)
        for batch in a.REPS:
            with self.subTest(batch=batch):
                closed = {b: {"closed_utc": "synthetic"} for b in a.REPS}
                closed[batch] = None
                (self.root / "data/collection-status.json").write_text(json.dumps(closed))
                scorer = Mock()
                with patch.object(a.integrity, "read_jsonl") as read, self.assertRaisesRegex(ValueError, "Both batches"):
                    a.load_rows(self.root, scorer)
                read.assert_not_called()
                scorer.score_text.assert_not_called()

    def test_rejects_unselected_protocol_and_changed_freeze_sources_runtime(self):
        manifest, _ = build(self.root)
        variants = []
        wrong_protocol = copy.deepcopy(manifest)
        wrong_protocol["protocol"] = "gpt-v1"
        variants.append((wrong_protocol, "requires the frozen"))
        wrong_runtime = copy.deepcopy(manifest)
        wrong_runtime["python"] = "different Python"
        variants.append((wrong_runtime, "runtime differs"))
        missing_source = copy.deepcopy(manifest)
        missing_source["code_hashes"].pop("analyze_claude.py")
        variants.append((missing_source, "absent from freeze"))
        for variant, message in variants:
            with self.subTest(message=message):
                save_manifest(self.root, variant)
                with patch.object(a.integrity, "read_jsonl") as read, self.assertRaisesRegex(ValueError, message):
                    a.load_inputs(self.root)
                read.assert_not_called()
        save_manifest(self.root, manifest)
        changed = self.root / "prereg/claude_scorer_v1_1.py"
        changed.write_text(changed.read_text() + "\n# synthetic corruption\n")
        with self.assertRaisesRegex(ValueError, "Frozen source changed"):
            a.load_inputs(self.root)
        shutil.copyfile(r.ROOT / "prereg/claude_scorer_v1_1.py", changed)
        manifest["manifest_sha256"] = "wrong"
        (self.root / "data/freeze.json").write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "manifest integrity"):
            a.load_inputs(self.root)

    def test_audits_metadata_payload_identity_and_unplanned_slot(self):
        _, attempts = build(self.root)
        bad = []
        for index, reason in enumerate(("trial_metadata_mismatch", "request_mismatch", "returned_model_mismatch", "unplanned_slot")):
            attempt = copy.deepcopy(attempts[index])
            if reason == "trial_metadata_mismatch":
                attempt["trial"]["source_set_label"] = "wrong-origin"
            elif reason == "request_mismatch":
                attempt["request"]["max_tokens"] = 7
            elif reason == "returned_model_mismatch":
                attempt["fields"]["model_returned"] = "unapproved-model"
            else:
                attempt["trial_id"] = "unplanned"
            bad.append(attempt)
        write_attempts(self.root, bad + attempts[4:])
        rows, audit = a.load_rows(self.root, self.scorer)
        self.assertEqual({item["reason"] for item in audit["exclusions"]},
                         {"trial_metadata_mismatch", "request_mismatch", "returned_model_mismatch", "unplanned_slot"})
        self.assertEqual(len(rows), 16_000 - 4)
        self.assertEqual(audit["planned_slots"], 16_000)

    def test_whole_missing_words_cannot_shrink_model_denominator(self):
        manifest, _ = build(self.root, keep_fresh_words=14)
        rows, _ = a.load_rows(self.root, self.scorer)
        data = a.Data(rows, manifest)
        self.assertEqual(len(data.words["fresh"]), 24)
        self.assertEqual(data.models_in("fresh", a.ALL), [])     # 700/1200, not 700/700
        fresh = [row for row in data.model_eligibility() if row["batch"] == "fresh"]
        self.assertTrue(all(row["planned"] == 1200 and row["eligible"] == 700 for row in fresh))
        # Retaining 15 full words clears 60%, but all nine missing words are still reported.
        manifest, _ = build(self.root, keep_fresh_words=15)
        rows, _ = a.load_rows(self.root, self.scorer)
        data = a.Data(rows, manifest)
        self.assertEqual(data.models_in("fresh", a.ALL), a.ALL)
        result = a.confirmatory(data, permutations=100, bootstraps=50)
        self.assertEqual(result["H1"]["n_words"], 15)
        self.assertEqual(result["H1"]["dropped_words"], 9)

    def test_cli_reports_frozen_provenance_and_planned_denominators(self):
        manifest, _ = build(self.root)
        with patch.object(sys, "argv", ["analyze_claude.py", "--root", str(self.root),
                                         "--permutations", "100", "--bootstraps", "50"]), contextlib.redirect_stdout(io.StringIO()):
            a.main()
        report = json.loads((self.root / "analysis/claude/claude_results.json").read_text())
        self.assertEqual(report["manifest_sha256"], manifest["manifest_sha256"])
        self.assertEqual(report["attempts_sha256"], r.digest((self.root / "data/attempts.jsonl").read_bytes()))
        self.assertEqual(report["v1.1"]["scorer_sha256"], r.digest((r.ROOT / "prereg/claude_scorer_v1_1.py").read_bytes()))
        self.assertEqual({row["planned"] for row in report["v1.1"]["model_eligibility_primary"]}, {800, 1200})

    def test_floor_rule_and_holm(self):
        self.assertEqual(a.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": None}), {"a": 0.03, "c": 0.06, "b": 0.06})

    def test_combined_protocol_freezes_claude_files(self):
        self.assertEqual(r.PROTOCOLS["gpt-v1"], [])
        for name in r.PROTOCOLS["gpt-v1+claude-v1.1"]:
            self.assertTrue((r.ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
