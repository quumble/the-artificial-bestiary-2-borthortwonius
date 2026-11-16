"""Contract tests for the declared populations, estimands and outcome tiers."""
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (Path(__file__).resolve().parents[1] / "supplement" /
               "coding-heuristics" / "declared-contrasts" / "questions.py")
SPEC = importlib.util.spec_from_file_location("declared_questions", MODULE_PATH)
questions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(questions)


class DeclaredQuestionTests(unittest.TestCase):
    def setUp(self):
        self.specs = questions.build_questions()
        self.by_id = {row["id"]: row for row in self.specs}

    def test_declared_scope_is_complete_and_ids_unique(self):
        expected = {1: 10, 2: 26, 3: 6, 4: 11, 5: 24, 6: 12, 7: 64, 8: 6}
        self.assertEqual(len(self.specs), 159)
        self.assertEqual(len(self.by_id), len(self.specs))
        for question, count in expected.items():
            subset = [row for row in self.specs if row["metadata"]["question"] == question]
            self.assertEqual(len(subset), count, question)
            self.assertTrue(all(row["block"] == 2 for row in subset))
            expected_tier = "secondary" if question in (3, 5, 8) else "primary"
            self.assertTrue(all(row["tier"] == expected_tier for row in subset))

    def test_provider_and_generation_comparisons_use_fixed_endpoint_groups(self):
        for row in self.specs:
            if ".Anthropic_minus_OpenAI" in row["id"]:
                first, second = row["terms"]
                self.assertEqual(first["selection"]["models"], questions.ANTHROPIC)
                self.assertEqual(second["selection"]["models"], questions.OPENAI)
                self.assertEqual([first["coefficient"], second["coefficient"]], [1, -1])
            if ".current_minus_historical" in row["id"]:
                first, second = row["terms"]
                self.assertEqual(first["selection"]["models"], questions.CURRENT)
                self.assertEqual(second["selection"]["models"], questions.HISTORICAL)
        self.assertEqual(set(questions.CURRENT) & set(questions.HISTORICAL), set())
        self.assertEqual(set(questions.ANTHROPIC) & set(questions.OPENAI), set())
        self.assertEqual(set(questions.CURRENT + questions.HISTORICAL), set(questions.MODELS))

    def test_decline_and_late_marking_include_neutral_once(self):
        for row in self.specs:
            q = row["metadata"]["question"]
            if q == 1 or (q == 8 and row["metadata"]["framing"] == "nonimaginary"):
                for term in row["terms"]:
                    conditions = term["selection"]["conditions"]
                    self.assertEqual(len(conditions), 7)
                    self.assertEqual(conditions.count("neutral"), 1)
                    self.assertEqual(set(conditions), set(questions.REAL_TYPE + ["neutral"]))

    def test_conditional_rates_have_correct_nested_numerators(self):
        for row in self.specs:
            q = row["metadata"]["question"]
            for term in row["terms"]:
                select = term["selection"]
                if q == 1:
                    self.assertEqual(select["field"], "type:DECLINE_WITH_POSSIBILITIES")
                    self.assertEqual(select["denominator"], "decline")
                elif q == 4:
                    self.assertEqual(select["field"], "described_grounding")
                    self.assertEqual(select["denominator"], "E")
                elif q == 8:
                    self.assertEqual(select["field"], "described_late_mark")
                    self.assertEqual(select["denominator"], "described_mark")

    def test_description_composition_is_a_four_class_partition(self):
        rows = [row for row in self.specs
                if row["metadata"]["question"] == 3 and row["metadata"]["kind"] == "rate"]
        fields = {row["terms"][0]["selection"]["field"] for row in rows}
        self.assertEqual(fields, {
            "type:DESCRIBE_UNMARKED", "type:DESCRIBE_HEDGED",
            "type:DESCRIBE_FRAMED", "type:DISCLAIM_AND_DESCRIBE",
        })
        for row in rows:
            select = row["terms"][0]["selection"]
            self.assertEqual(select["denominator"], "E")
            self.assertEqual(select["conditions"], questions.REAL_TYPE)
        # Never substitute U for bare: U includes hedged descriptions.
        for row in self.specs:
            if row["metadata"]["question"] == 3:
                self.assertNotIn("U", [term["selection"]["field"] for term in row["terms"]])

    def test_prompt_echo_is_unconditional_and_difference_direction_is_fixed(self):
        for model in questions.MODELS:
            row = self.by_id[f"Q5.unmarked_echo.discounted_minus_counted.{model}"]
            plus, minus = row["terms"]
            self.assertEqual(plus["selection"]["field"], "U_unmarked_discounting_prompt_echo")
            self.assertEqual(minus["selection"]["field"], "U")
            for term in row["terms"]:
                select = term["selection"]
                self.assertNotIn("denominator", select)
                self.assertEqual(select["conditions"], questions.IMAGINARY)
                self.assertEqual(select["models"], [model])

    def test_category_contrasts_pair_same_two_frames(self):
        for row in self.specs:
            if row["metadata"]["question"] != 6:
                continue
            plus, minus = (term["selection"] for term in row["terms"])
            category = row["metadata"]["category"]
            self.assertEqual(plus["conditions"], [f"real_{category}", f"type_of_{category}"])
            self.assertEqual(minus["conditions"], ["real_animal", "type_of_animal"])
            self.assertEqual(plus["models"], minus["models"])
            self.assertEqual(plus["arm"], minus["arm"])
            self.assertIn(plus["arm"], ("B", "C"))
            self.assertEqual(plus["field"], "E")
            self.assertNotIn("denominator", plus)

    def test_consistency_is_within_cell_and_keeps_banks_separate(self):
        for row in self.specs:
            if row["metadata"]["question"] != 7:
                continue
            self.assertEqual(len(row["terms"]), 1)
            select = row["terms"][0]["selection"]
            self.assertEqual(select["statistic"], "pair_agreement")
            self.assertEqual(len(select["models"]), 1)
            self.assertEqual(set(select["conditions"]), set(questions.ALL_CONDITIONS))
            self.assertEqual(len(select["conditions"]), 10)
            self.assertEqual(select["bank"], row["metadata"]["bank"])
            if select["field"] == "response_type":
                self.assertEqual(select["arm"], "C")
            else:
                self.assertEqual(select["field"], "E")
            self.assertNotIn("denominator", select)

    def test_rate_components_do_not_alias_mutable_selections(self):
        first = self.specs[0]["terms"][0]["selection"]
        first["conditions"].append("invalid")
        self.assertTrue(all("invalid" not in term["selection"]["conditions"]
                            for row in self.specs[1:] for term in row["terms"]))
        self.assertNotIn("invalid", questions.NONIMAGINARY)


if __name__ == "__main__":
    unittest.main()
