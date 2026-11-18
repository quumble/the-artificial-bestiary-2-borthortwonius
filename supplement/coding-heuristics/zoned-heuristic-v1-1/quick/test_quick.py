"""Checks for the streamlined page and core subset. Synthetic labels only; nothing here is saved as a result."""
import json
import random
import re
import unittest

import quick
from quick import audit


class Core(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = json.loads(quick.FULL_MANIFEST.read_text(encoding="utf-8"))
        cls.core = json.loads(quick.CORE_MANIFEST.read_text(encoding="utf-8"))
        cls.html = quick.QUICK_PAGE.read_text(encoding="utf-8")
        found = re.search(r'<script id="audit-data" type="application/json">(.*?)</script>', cls.html, re.S)
        cls.payload = json.loads(found.group(1))

    def test_rebuild_is_byte_identical(self):
        manifest, payload, parent = quick.load_full()
        keep = quick.core_ids(manifest)
        self.assertEqual(audit.canonical(quick.subset_manifest(manifest, keep, parent)),
                         audit.canonical(self.core))
        page = audit.page_html(quick.page_payload(manifest, payload, keep),
                               quick.TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(page, self.html)

    def test_core_composition(self):
        items = self.core["items"]
        self.assertEqual(len(items), 41)
        self.assertEqual(self.core["audit_id"], self.full["audit_id"])
        self.assertEqual(self.core["eligible_population"], self.full["eligible_population"])
        changed_full = {i["item_id"] for i in self.full["items"] if i["stratum"].endswith("|changed")}
        self.assertTrue(changed_full <= {i["item_id"] for i in items})
        unchanged = [i for i in items if i["stratum"].endswith("|unchanged")]
        self.assertEqual(len(unchanged), len({i["stratum"] for i in unchanged}))
        for s in self.core["strata"]:
            self.assertTrue(s["population"] == 0 or s["selected"] > 0)
        # Each control is the lowest-ranked selected item in its stratum.
        for item in unchanged:
            peers = [i for i in self.full["items"] if i["stratum"] == item["stratum"]]
            best = min(peers, key=lambda i: audit.rank(self.full["selection_seed"], i["key"]))
            self.assertEqual(best["item_id"], item["item_id"])

    def test_page_order_and_concealment(self):
        ids = [i["item_id"] for i in self.payload["items"]]
        core = {i["item_id"] for i in self.core["items"]}
        frozen = [i["item_id"] for i in self.full["items"]]
        self.assertEqual(self.payload["core_count"], 41)
        self.assertEqual(set(ids[:41]), core)
        self.assertEqual(ids[:41], [i for i in frozen if i in core])
        self.assertEqual(ids[41:], [i for i in frozen if i not in core])
        for item in self.payload["items"]:
            self.assertEqual(set(item), {"item_id", "prompt", "response", "imaginary", "word"})
            self.assertIn(item["word"], item["prompt"])
        for item in self.full["items"]:
            self.assertNotIn(item["key"], self.html)
            self.assertNotIn(item["stratum"], self.html)
        for leak in ("predictions", "|changed", "|unchanged", "response_sha256"):
            self.assertNotIn(leak, self.html)

    def test_core_scores_with_frozen_scorer_and_paired_difference_is_unchanged(self):
        rng = random.Random(20261118)
        items = []
        for item in self.full["items"]:
            d = rng.choice("YHSN")
            mark = rng.choice("YEN" if item["imaginary"] else "YN") if d in "YH" else None
            items.append({"item_id": item["item_id"], "nonrecognition": rng.choice("YN"), "description": d,
                          "mark": mark, "flagged_unsure": rng.random() < 0.1, "ms": 1000, "notes": ""})
        labels = {"schema": audit.LABEL_SCHEMA, "audit_id": self.full["audit_id"], "items": items}
        full = audit.score_labels(self.full, labels)
        core = audit.score_labels(self.core, quick.labels_for(labels, self.core))
        self.assertEqual(core["n"], 41)
        for outcome in ("E", "R", "N", "U", "S"):
            a = full["all_labels"]["outcomes"][outcome]
            b = core["all_labels"]["outcomes"][outcome]
            self.assertAlmostEqual(a["weight_denominator"], b["weight_denominator"], places=9)
            self.assertAlmostEqual(a["paired_weighted_correctness_difference"],
                                   b["paired_weighted_correctness_difference"], places=12)
            self.assertEqual(a["new_only_correct"], b["new_only_correct"])
            self.assertEqual(a["old_only_correct"], b["old_only_correct"])

    def test_core_labels_also_validate_against_full_manifest(self):
        item = self.core["items"][0]
        label = {"item_id": item["item_id"], "nonrecognition": "N", "description": "N", "mark": None,
                 "flagged_unsure": False, "ms": 5, "notes": ""}
        labels = {"schema": audit.LABEL_SCHEMA, "audit_id": self.full["audit_id"], "items": [label]}
        self.assertEqual(len(audit.validate_labels(self.full, labels, complete=False)), 1)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            audit.score_labels(self.core, labels)


if __name__ == "__main__":
    unittest.main()
