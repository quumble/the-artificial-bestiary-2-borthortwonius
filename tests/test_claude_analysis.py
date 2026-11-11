import json
import shutil
import tempfile
import unittest
from pathlib import Path

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


def build(root, skip_model=None, with_known=True, truncate_imaginary=False):
    for batch, bank in words().items():
        if batch == "known" and not with_known:
            continue
        folder = root / "data" / "raw" / batch
        folder.mkdir(parents=True)
        for model in r.MODELS:
            if model["id"] == skip_model:
                continue
            lines = []
            for word_set, word, source in bank:
                for condition in CONDITIONS:
                    for rep in range(1, a.REPS[batch] + 1):
                        lines.append(json.dumps(dict(
                            trial_id="%s|%s|%s|%02d" % (batch, word, condition, rep), batch=batch, word=word, word_set=word_set,
                            source_set_label=source, condition=condition, rep=rep, model_requested=model["id"], attempt_ordinal=1,
                            terminal=True, valid=True, error=None, truncated=truncate_imaginary and condition in a.IMAG,
                            response=text(model["id"], batch, word, word_set, source, condition))))
            (folder / (model["id"] + ".jsonl")).write_text("\n".join(lines) + "\n")
    (root / "data" / "collection-status.json").write_text(json.dumps({"fresh": {"closed_utc": "x"}, "known": {"closed_utc": "x"} if with_known else None}))


class ClaudeAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scorer = a.load_scorer("claude_scorer_v1_1.py")

    def tearDown(self):
        self.temp.cleanup()

    def run_family(self, **kwargs):
        include = kwargs.pop("include_truncated", False)
        build(self.root, **kwargs)
        rows, audit = a.load_rows(self.root, self.scorer)
        return a.confirmatory(a.Data(rows, include_truncated=include), permutations=2000, bootstraps=400), rows, audit

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
        again, _, _ = (a.confirmatory(a.Data(rows), permutations=2000, bootstraps=400), None, None)
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
        sens = a.confirmatory(a.Data(rows, include_truncated=True), permutations=500, bootstraps=200)
        self.assertAlmostEqual(sens["H1"]["estimate"], 1.0)

    def test_flagged_records_are_ineligible_and_earliest_duplicate_wins(self):
        build(self.root)
        path = self.root / "data/raw/fresh/gpt-6-sol.jsonl"
        lines = path.read_text().splitlines()
        first = json.loads(lines[0])
        flagged = dict(first, trial_id="flagged", valid=False, issue="reasoning_observed_in_reasoning_off_run", protocol_violation="x")
        later = dict(first, attempt_ordinal=2, response="A %s is a small thing. It has a handle." % first["word"])
        path.write_text("\n".join(lines + [json.dumps(flagged), json.dumps(later)]) + "\n")
        rows, audit = a.load_rows(self.root, self.scorer)
        self.assertEqual(audit["ineligible"], 1)
        self.assertEqual(audit["duplicates"], 1)
        self.assertEqual(len(rows), 8 * (24 * 10 * 5 + 8 * 10 * 10))

    def test_floor_rule_and_holm(self):
        self.assertEqual(a.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": None}), {"a": 0.03, "c": 0.06, "b": 0.06})

    def test_combined_protocol_freezes_claude_files(self):
        self.assertEqual(r.PROTOCOLS["gpt-v1"], [])
        for name in r.PROTOCOLS["gpt-v1+claude-v1.1"]:
            self.assertTrue((r.ROOT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
