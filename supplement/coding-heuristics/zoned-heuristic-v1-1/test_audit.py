"""Synthetic checks of audit sampling, masking, validation, and weighted scoring."""
import copy
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

import audit


def codes(n=6):
    old, new = {}, {}
    for endpoint in range(8):
        for bank in ("fresh", "known"):
            for changed in (False, True):
                for rep in range(n):
                    key = f"{bank}|model-{endpoint}|{bank}|word|{'changed' if changed else 'same'}|{rep}"
                    row = {"key": key, "model": f"model-{endpoint}", "batch": bank, "word": "word",
                           "source": "synthetic", "condition": "neutral", "framing": "neutral", "rep": str(rep),
                           "response_sha256": audit.digest(key.encode()), "response_type": "NO_DESCRIPTION_OTHER",
                           **{field: 0 for field in audit.OUTCOMES.values()}}
                    old[key] = row
                    new[key] = {**row, "nonrec_any": int(changed)}
    return old, new


def two_item_fixture():
    manifest = {"schema": audit.MANIFEST_SCHEMA, "audit_id": "synthetic", "selected_count": 2,
                "eligible_population": 10, "strata": [{"stratum": "a", "population": 9, "selected": 1},
                                                       {"stratum": "b", "population": 1, "selected": 1}], "items": []}
    labels = {"schema": audit.LABEL_SCHEMA, "audit_id": "synthetic", "items": []}
    for i, stratum in enumerate(("a", "b")):
        manifest["items"].append({"item_id": f"item-{i}", "stratum": stratum, "imaginary": False,
                                  "predictions": {"1.0": {o: 0 for o in audit.OUTCOMES},
                                                  "1.1": {o: 1 for o in audit.OUTCOMES}}})
        labels["items"].append({"item_id": f"item-{i}", "nonrecognition": "N", "description": "Y" if i == 0 else "N",
                                 "mark": "N" if i == 0 else None, "flagged_unsure": False, "ms": 10, "notes": ""})
    return manifest, labels


class SamplingTests(unittest.TestCase):
    def test_full_strata_have_three_and_deterministic_order(self):
        old, new = codes()
        selected, strata = audit.select_sample(old, new, set())
        self.assertEqual(len(selected), 96)
        self.assertEqual({s["selected"] for s in strata}, {3})
        self.assertEqual(selected, audit.select_sample(dict(reversed(list(old.items()))), new, set())[0])
        self.assertEqual([i["key"] for i in selected], sorted((i["key"] for i in selected), key=lambda k: audit.rank(audit.ORDER_SEED, k)))

    def test_exclusion_and_reallocation(self):
        old, new = codes(7)
        excluded = {k for k, r in old.items() if r["model"] == "model-0" and r["batch"] == "fresh"}
        selected, strata = audit.select_sample(old, new, excluded)
        self.assertEqual(len(selected), 96)
        self.assertFalse({i["key"] for i in selected} & excluded)
        self.assertEqual(sum(s["selected"] == 4 for s in strata), 6)
        self.assertEqual(sum(s["population"] for s in strata), len(old) - len(excluded))
        self.assertAlmostEqual(sum(s["selected"] * s["weight"] for s in strata if s["selected"]), len(old) - len(excluded))

    def test_diagnostic_flag_does_not_change_stratum_but_type_does(self):
        old, new = codes()
        new = copy.deepcopy(old)
        key = next(iter(new))
        new[key]["fragile"] = "new_alias_diagnostic"
        _, strata = audit.select_sample(old, new, set())
        self.assertEqual(sum(s["population"] for s in strata if s["stratum"].endswith("|changed")), 0)
        new[key]["response_type"] = "DESCRIBE_SUBSTITUTE"
        _, strata = audit.select_sample(old, new, set())
        self.assertEqual(sum(s["population"] for s in strata if s["stratum"].endswith("|changed")), 1)

    def test_rejects_metadata_or_key_drift(self):
        old, new = codes()
        new[next(iter(new))]["response_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            audit.select_sample(old, new, set())


class HumanLabelTests(unittest.TestCase):
    def test_conditional_mark_and_human_definitions(self):
        manifest, labels = two_item_fixture()
        self.assertEqual(len(audit.validate_labels(manifest, labels)), 2)
        label = {"nonrecognition": "Y", "description": "S", "mark": None}
        self.assertEqual(audit.human_outcomes(label), {"E": 0, "R": 1, "N": 1, "U": 0, "S": 1})
        label.update(description="H", mark="E")
        self.assertEqual(audit.human_outcomes(label), {"E": 1, "R": 1, "N": 0, "U": 0, "S": 0})

    def test_rejects_incomplete_duplicate_unknown_stale_and_invalid_marks(self):
        manifest, labels = two_item_fixture()
        mutations = [lambda x: x["items"].pop(),
                     lambda x: x["items"].append(dict(x["items"][0])),
                     lambda x: x["items"][0].update(item_id="unknown"),
                     lambda x: x.update(audit_id="stale"),
                     lambda x: x["items"][0].update(mark=None),
                     lambda x: x["items"][0].update(mark="E"),
                     lambda x: x["items"][1].update(mark="N"),
                     lambda x: x["items"][0].update(ms=float("nan")),
                     lambda x: x["items"][0].update(flagged_unsure=1)]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                invalid = copy.deepcopy(labels)
                mutation(invalid)
                with self.assertRaises(ValueError):
                    audit.validate_labels(manifest, invalid)
        labels["items"].pop()
        self.assertEqual(len(audit.validate_labels(manifest, labels, complete=False)), 1)

    def test_weights_and_paired_difference(self):
        manifest, labels = two_item_fixture()
        result = audit.score_labels(manifest, labels)["all_labels"]["outcomes"]["E"]
        self.assertEqual(result["versions"]["1.0"]["raw_accuracy"], .5)
        self.assertEqual(result["versions"]["1.1"]["weighted_accuracy"], .9)
        self.assertEqual(result["versions"]["1.0"]["weighted_accuracy"], .1)
        self.assertEqual(result["paired_weighted_correctness_difference"], .8)
        self.assertEqual(result["weight_denominator"], 10)

    def test_unsure_bounds_and_retained_weights(self):
        manifest, labels = two_item_fixture()
        labels["items"][0]["flagged_unsure"] = True
        result = audit.score_labels(manifest, labels)
        main = result["all_labels"]["outcomes"]["E"]
        self.assertEqual(main["unsure_truth_weighted_paired_difference_bounds"], [-1, .8])
        self.assertEqual(main["versions"]["1.1"]["unsure_truth_weighted_accuracy_bounds"], [0, .9])
        sensitivity = result["excluding_unsure_sensitivity"]["outcomes"]["E"]
        self.assertEqual(sensitivity["weight_denominator"], 1)
        self.assertEqual(sensitivity["versions"]["1.0"]["weighted_accuracy"], 1)
        manifest["items"][0]["predictions"]["1.1"]["E"] = 0
        bounds = audit.score_labels(manifest, labels)["all_labels"]["outcomes"]["E"]["unsure_truth_weighted_paired_difference_bounds"]
        self.assertEqual(bounds, [-.1, -.1])


class ArtifactTests(unittest.TestCase):
    def test_json_script_cannot_be_closed_by_response(self):
        payload = {"audit_id": "synthetic", "items": [{"item_id": "item-1", "prompt": "Synthetic prompt", "response": "</script><script>alert(1)</script>\u2028", "imaginary": False}]}
        template = '<script type="application/json">__AUDIT_PAYLOAD__</script>'
        html = audit.page_html(payload, template)
        self.assertEqual(html.count("</script>"), 1)
        extracted = html.split('>', 1)[1].rsplit('</script>', 1)[0]
        self.assertEqual(json.loads(extracted), payload)
        for hidden in ("predictions", "response_sha256", "stratum", "model", "source", "key"):
            self.assertNotIn('"' + hidden + '":', html)

    def test_raw_loader_checks_hashes_and_returns_full_selected_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.zip"
            row = {"batch": "fresh", "model_requested": "synthetic", "trial_id": "fresh|word|neutral|01",
                   "prompt": "Describe a word.", "response": "Full synthetic\nresponse."}
            key = "fresh|synthetic|" + row["trial_id"]
            record = {"response_sha256": audit.digest(row["response"].encode()), "framing": "neutral"}
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("data/raw/fresh/synthetic.jsonl", json.dumps(row))
            found = audit.load_selected_texts(path, [{"key": key}], {key: record})
            self.assertEqual(found[key]["response"], row["response"])
            record["response_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                audit.load_selected_texts(path, [{"key": key}], {key: record})

    def test_committed_freeze_rejects_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ["PLAN.md", "METHOD.md", "zoned_heuristic.py", "run_corpus.py", "audit.py", "audit-template.html"]
            for name in names:
                (root / name).write_text("Synthetic fixture\n")
            manifest = root / "FREEZE.sha256"
            manifest.write_text("".join(f"{audit.digest((root / n).read_bytes())}  {n}\n" for n in names))
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL).decode().strip()
            git("init")
            git("add", ".")
            git("-c", "user.name=Audit Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Synthetic freeze")
            commit = git("rev-parse", "HEAD")
            self.assertEqual(audit.check_freeze(root, manifest, commit)["commit"], commit)
            (root / "audit.py").write_text("Changed after freeze")
            with self.assertRaises(ValueError):
                audit.check_freeze(root, manifest, commit)


if __name__ == "__main__":
    unittest.main()
