"""Independent checks on published-input joins and historical reproduction."""
from __future__ import annotations

import csv
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "supplement/coding-heuristics/declared-contrasts"))
from inputs import index_unique, load_inputs
from reproduce_comparisons import (
    agreement, compare_nested, label_values, reproduce, sampling_weights,
    score_against_labels,
)


class PublishedReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_inputs(ROOT)
        cls.result = reproduce(cls.dataset, ROOT)

    def test_complete_released_panel(self):
        validation = self.dataset.provenance["validation"]
        self.assertEqual(validation["rows"], 16000)
        self.assertEqual(validation["complete_cells"], 2560)
        self.assertEqual(validation["null_outcomes_A"], {"E": 11, "N": 5, "U": 1531, "R": 0})
        self.assertEqual(sum(r["category"] is None for r in self.dataset.rows), 1600)
        self.assertTrue(validation["used_archives_match_published_checksums"])

    def test_all_historical_result_fields_reproduced(self):
        checks = self.result["verification"]
        self.assertTrue(checks["all_matched"])
        self.assertEqual(checks["three_way"]["compared_leaves"], 477)
        self.assertEqual(checks["human_pass"]["compared_leaves"], 73)
        self.assertEqual(checks["three_way"]["maximum_absolute_numeric_difference"], 0)
        self.assertEqual(checks["human_pass"]["maximum_absolute_numeric_difference"], 0)

    def test_reader_agreement_derived_from_labels(self):
        expected = {"description": 80, "nonrecognition": 82,
                    "nonrec_without_description": 83, "unmarked_description": 77}
        for name, correct in expected.items():
            with self.subTest(name=name):
                self.assertEqual(self.result["reader_agreement"][name]["correct"], correct)
                self.assertEqual(self.result["reader_agreement"][name]["n"], 84)
        self.assertEqual(self.result["marking_agreement"]["correct"], 26)
        self.assertEqual(self.result["marking_agreement"]["n"], 34)
        self.assertEqual(self.result["holdout_sampling"]["population_n"], 15989)

    def test_B_metadata_corruption_is_rejected(self):
        original_read = Path.read_bytes

        def corrupt(path):
            blob = original_read(path)
            if path.name != "coded_responses.csv":
                return blob
            records = list(csv.DictReader(io.StringIO(blob.decode("utf-8"))))
            records[0]["provider_group"] = "OpenAI"
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
            return buffer.getvalue().encode("utf-8")

        with patch.object(Path, "read_bytes", corrupt):
            with self.assertRaisesRegex(ValueError, "Endpoint-group mismatch"):
                load_inputs(ROOT)

    def test_missing_B_trial_is_rejected(self):
        original_read = Path.read_bytes

        def remove_last_trial(path):
            blob = original_read(path)
            return b"\n".join(blob.splitlines()[:-1]) + b"\n" if path.name == "coded_responses.csv" else blob

        with patch.object(Path, "read_bytes", remove_last_trial):
            with self.assertRaisesRegex(ValueError, "different trial keys"):
                load_inputs(ROOT)

    def test_archive_tampering_is_rejected(self):
        original_read = Path.read_bytes

        def append_byte(path):
            blob = original_read(path)
            return blob + b"x" if path.name == "Bestiary_2_Context_Heuristic_v1.zip" else blob

        with patch.object(Path, "read_bytes", append_byte):
            with self.assertRaisesRegex(ValueError, "Context archive does not match"):
                load_inputs(ROOT)


class StatisticalReproductionTests(unittest.TestCase):
    def test_duplicate_keys_cannot_silently_overwrite(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            index_unique([{"key": "x"}, {"key": "x"}], lambda row: row["key"], "test")

    def test_agreement_uses_pairwise_resolved_denominator(self):
        result = agreement([1, 0, None, 1], [1, 1, 0, 0])
        self.assertEqual(result["n"], 3)
        self.assertEqual(result["agree"], 1 / 3)
        self.assertAlmostEqual(result["kappa"], -0.5)
        self.assertEqual(result["x_only"], 1)
        self.assertEqual(result["y_only"], 1)

    def test_undefined_kappa_and_empty_agreement(self):
        self.assertIsNone(agreement([1, 1], [1, 1])["kappa"])
        with self.assertRaisesRegex(ValueError, "No jointly resolved"):
            agreement([None], [1])

    def test_hypothetical_substitute_and_echo_crosswalk(self):
        self.assertEqual(label_values("H", "N", "E")["description"], 1)
        self.assertEqual(label_values("H", "N", "E")["unmarked_description"], 0)
        self.assertEqual(label_values("H", "N", "E")["unmarked_echo"], 1)
        self.assertEqual(label_values("S", "N", "")["description"], 0)
        self.assertEqual(label_values("Y", "Y", "N")["unmarked_description"], 0)
        with self.assertRaises(ValueError):
            label_values("N", "N", "Y")

    def test_weighted_accuracy_drops_null_prediction_from_denominator(self):
        result = score_against_labels(
            ["a", "b", "c"], {"a": 1, "b": 0, "c": None},
            {"a": 1, "b": 1, "c": 1}, {"a": 3, "b": 1, "c": 100}, historical_names=False)
        self.assertEqual(result, {"n": 2, "correct": 1, "weighted": .75, "fp": 0, "fn": 1})

    def test_sampling_weights_restore_pool_strata(self):
        rows = [{"key": str(i), "A": {"E": a}, "B": {"E": b}}
                for i, (a, b) in enumerate([(0, 0), (0, 0), (0, 0), (1, 1), (None, 1)])]
        weights, strata = sampling_weights(rows, ["0", "3"])
        self.assertEqual(weights, {"0": 1.5, "3": .5})
        self.assertEqual(strata, {"(0, 0)": [1, 3], "(1, 1)": [1, 1]})
        with self.assertRaisesRegex(ValueError, "cover every"):
            sampling_weights(rows, ["0"])

    def test_comparison_checks_structure_and_exact_integer_counts(self):
        self.assertTrue(compare_nested({"a": [0.1 + 0.2]}, {"a": [.3]})["matched"])
        self.assertFalse(compare_nested({"n": 10 ** 15}, {"n": 10 ** 15 + 1})["matched"])
        self.assertFalse(compare_nested({"a": [1, 2]}, {"a": [1]})["matched"])
        self.assertFalse(compare_nested({"a": None}, {"b": None})["matched"])


if __name__ == "__main__":
    unittest.main()
