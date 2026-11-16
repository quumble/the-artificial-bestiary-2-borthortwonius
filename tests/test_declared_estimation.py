"""Scientific regression tests for the exploratory word-level estimators."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

import numpy as np

DIRECTORY = Path(__file__).resolve().parents[1] / "supplement/coding-heuristics/declared-contrasts"
sys.path.insert(0, str(DIRECTORY))
from estimation import Estimator, NONIMAGINARY, interpretation, row_value
from contrasts import build_contrasts

BO = "fresh-animal-intent"
CLAUDE = "fresh-no-intent-claude"
GPT = "fresh-no-intent-gpt"
MODEL = "gpt-5.4-mini"


def row(word="one", condition="real_animal", value=0, source=BO, model=MODEL, **zoned):
    values = {"E": value, "N": value, "U": value, "R": 0}
    return dict(source=source, batch="known" if source.startswith("known") else "fresh",
                word=word, condition=condition, model=model,
                A=dict(values), B=dict(values), C=dict(values),
                zoned=dict(response_type="DESCRIBE_UNMARKED", marking_position="none",
                           grounding_claim=0, **zoned))


def select(arm="A", **kwargs):
    return dict(arm=arm, field="E", bank="fresh", models=[MODEL],
                conditions=["real_animal"], **kwargs)


def spec(*terms):
    return dict(id="synthetic", terms=[dict(coefficient=c, selection=s) for c, s in terms])


class DeclaredEstimationTests(unittest.TestCase):
    def estimate(self, rows, specification, draws=200):
        return Estimator(rows, draws=draws).evaluate(specification)

    def test_equal_conditions_not_pooled_repetitions(self):
        rows = [row(value=1)] + [row(condition="real_object", value=0) for _ in range(9)]
        selected = select(); selected["conditions"] += ["real_object"]
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertEqual(result["estimate"], .5)

    def test_neutral_is_one_of_seven_conditions(self):
        rows = [row(condition=c, value=int(c == "neutral")) for c in NONIMAGINARY]
        selected = select(); selected["conditions"] = list(NONIMAGINARY)
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertAlmostEqual(result["estimate"], 1 / 7)

    def test_endpoints_are_equally_weighted_after_cells(self):
        rows = [row(value=1)] + [row(model="gpt-6-sol", value=0) for _ in range(9)]
        selected = select(); selected["models"] += ["gpt-6-sol"]
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertEqual(result["estimate"], .5)

    def test_source_masses_do_not_depend_on_number_of_words(self):
        rows = [row(word=str(i), value=1) for i in range(4)] + [row(source=CLAUDE, value=0)]
        result, _ = self.estimate(rows, spec((1, select())))
        self.assertEqual(result["estimate"], .5)

    def test_h4_equal_intent_standardization(self):
        rows = []
        for source in (BO, CLAUDE, GPT, "known-animal-intent", "known-no-intent"):
            for model, current in ((MODEL, False), ("gpt-6-sol", True)):
                for condition in NONIMAGINARY:
                    rows.append(row(source=source, model=model, condition=condition,
                                    value=int(current and source in (BO, "known-animal-intent"))))
        selected = next(s for s in build_contrasts() if s["id"] == "H4.N.A")
        result, draws = self.estimate(rows, selected)
        self.assertAlmostEqual(result["estimate"], 0)
        self.assertTrue(np.allclose(draws, 0))

    def test_h1_is_an_alias_not_another_estimate(self):
        specs = build_contrasts()
        self.assertEqual(len(specs), 66)
        self.assertFalse(any(s["id"].startswith("H1") for s in specs))
        for arm in "ABC":
            self.assertEqual(next(s for s in specs if s["id"] == f"G1.E.{arm}")["aliases"], [f"H1.E.{arm}"])

    def test_empty_cells_drop_without_zero_imputation(self):
        rows = [row(value=None), row(condition="real_object", value=1)]
        selected = select(); selected["conditions"] += ["real_object"]
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertEqual(result["estimate"], 1)
        support = result["components"][0]["support"]
        self.assertEqual(support["omitted_cells"], 1)
        self.assertEqual(support["null_responses"], 1)

    def test_within_word_contrast_uses_both_sides(self):
        rows = [row("one", value=0), row("one", "type_of_animal", 1),
                row("two", value=1), row("two", "type_of_animal", None)]
        minus = select(); minus["conditions"] = ["type_of_animal"]
        result, _ = self.estimate(rows, spec((1, select()), (-1, minus)))
        self.assertEqual(result["estimate"], -1)
        self.assertEqual(result["components"][0]["support"]["words_by_source"][BO]["retained_after_within_word_pairing"], 1)
        self.assertGreater(result["bootstrap_undefined"], 0)

    def test_empty_required_stratum_is_undefined(self):
        result, _ = self.estimate([row(value=1), row(source=CLAUDE, value=None)], spec((1, select())))
        self.assertIsNone(result["estimate"])
        self.assertIsNone(result["ci95"])
        self.assertEqual(result["bootstrap_defined"], 0)

    def test_instrument_differences_keep_each_native_support_and_paired_draws(self):
        rows = [row("one", value=0), row("two", value=1)]
        rows[1]["A"]["E"] = None
        engine = Estimator(rows, draws=200)
        a, ad = engine.evaluate(spec((1, select("A"))))
        b, bd = engine.evaluate(spec((1, select("B"))))
        gap, gd = engine.evaluate(spec((1, select("A")), (-1, select("B"))))
        self.assertEqual(gap["estimate"], -.5)
        self.assertAlmostEqual(gap["estimate"], a["estimate"] - b["estimate"])
        np.testing.assert_allclose(gd, ad - bd, equal_nan=True)

    def test_identical_estimators_have_zero_paired_uncertainty(self):
        rows = [row("one", value=0), row("two", value=1)]
        result, values = self.estimate(rows, spec((1, select("A")), (-1, select("B"))))
        self.assertEqual(result["ci95"], [0, 0])
        self.assertTrue((values == 0).all())
        self.assertEqual(Estimator(rows, 200).bootstrap_metadata(), Estimator(rows, 200).bootstrap_metadata())

    def test_conditional_estimate_is_ratio_of_weighted_rates(self):
        rows = [row("one", value=1) for _ in range(4)]
        rows += [row("two", value=int(i == 0)) for i in range(4)]
        rows[0]["zoned"]["grounding_claim"] = rows[4]["zoned"]["grounding_claim"] = 1
        selected = select("C", denominator="E"); selected["field"] = "described_grounding"
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertAlmostEqual(result["estimate"], .4)
        self.assertNotAlmostEqual(result["estimate"], (.25 + 1) / 2)

    def test_zero_conditional_denominator_draws_are_counted(self):
        rows = [row("one", value=1), row("two", value=0)]
        rows[0]["zoned"]["grounding_claim"] = 1
        selected = select("C", denominator="E"); selected["field"] = "described_grounding"
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertEqual(result["estimate"], 1)
        self.assertGreater(result["bootstrap_undefined"], 0)
        self.assertEqual(result["bootstrap_undefined"], result["components"][0]["bootstrap_zero_denominator_draws"])
        self.assertEqual(result["interval_status"], "conditional_on_defined_draws")

    def test_consistency_averages_cell_proportions_not_pair_counts(self):
        rows = [row(value=0), row(value=0)]
        rows += [row(condition="real_object", value=v) for v in (0, 0, 1, 1)]
        selected = select(statistic="pair_agreement"); selected["conditions"] += ["real_object"]
        result, _ = self.estimate(rows, spec((1, selected)))
        self.assertAlmostEqual(result["estimate"], 2 / 3)
        support = result["components"][0]["support"]
        self.assertAlmostEqual(support["matching_pairs"] / support["resolved_pairs"], 3 / 7)

    def test_late_marking_requires_description_and_positioned_cue(self):
        r = row(value=1)
        r["zoned"]["mark_hedge"] = 1
        self.assertEqual(row_value(r, "C", "described_mark"), 0)
        r["zoned"]["marking_position"] = "after"
        self.assertEqual(row_value(r, "C", "described_late_mark"), 1)
        r["C"]["E"] = 0
        self.assertEqual(row_value(r, "C", "described_mark"), 0)

    def test_uncertainty_is_not_automatically_instrument_dependence(self):
        arms = [dict(estimate=.1, ci95=[-.1, .3]) for _ in range(3)]
        result = interpretation(arms, [dict(id="A-B", ci95=[-.2, .2])])
        self.assertEqual(result["status"], "direction_unresolved")
        self.assertEqual(result["paired_differences_excluding_zero"], [])
        self.assertFalse(result["mixed_point_estimate_directions"])


if __name__ == "__main__":
    unittest.main()
