import unittest
from zoned_heuristic import score

def t(text, word="zorf", framing=None): return score(text, word, framing)

class Zones(unittest.TestCase):
    def test_bare_definition(self):
        r = t("A zorf is a small grey mammal. It lives in burrows and eats roots.")
        self.assertEqual(r["response_type"], "DESCRIBE_UNMARKED"); self.assertEqual(r["outcomes"]["U_bare_description"], 1)
    def test_possibility_list_is_not_description(self):
        r = t("I'm not familiar with a zorf. It's possible that:\n- It might be a regional term\n- It could be a misspelling\n- It may be a very obscure item\nCould you share where you saw it?")
        self.assertEqual(r["response_type"], "DECLINE_WITH_POSSIBILITIES"); self.assertEqual(r["fields"]["description_any"], 0)
    def test_inline_possibilities(self):
        r = t("\"Zorf\" doesn't match anything I recognize. There are a few possibilities. It could be a misspelling. It might be a local name. It could be a very obscure species.")
        self.assertEqual(r["outcomes"]["N_nonrecognition_without_description"], 1)
    def test_third_person_nonrecognition(self):
        r = t("The term zorf isn't something I can find in my knowledge base.")
        self.assertEqual(r["fields"]["nonrec_personal"], 1); self.assertEqual(r["response_type"], "DECLINE_PLAIN")
    def test_external_negative_only(self):
        r = t("Zorf is not a recognized word in English.")
        self.assertEqual((r["fields"]["nonrec_external"], r["fields"]["nonrec_personal"]), (1, 0))
    def test_disclaim_then_describe(self):
        r = t("I don't recognize zorf as an established term. Here's an invented description you can use:\n\nA zorf is a squat, moss-backed creature. It has six legs and feeds on lichen.")
        self.assertEqual(r["response_type"], "DISCLAIM_AND_DESCRIBE"); self.assertEqual(r["fields"]["mark_construction"], 1)
    def test_offer_is_not_construction(self):
        r = t("I don't know what a zorf is. Would you like me to invent an imaginary one?")
        self.assertEqual((r["fields"]["mark_construction"], r["fields"]["mark_fiction"], r["fields"]["offer"]), (0, 0, 1))
    def test_hypothetical_description(self):
        r = t("A zorf could be described as a kind of idea that is:\n- small but persistent\n- partly formed\n- hard to pin down")
        self.assertEqual(r["fields"]["description_hypothetical"], 1); self.assertEqual(r["response_type"], "DESCRIBE_FRAMED")
    def test_hedged(self):
        r = t("A zorf is a brass instrument about the size of a pear. It is said to hum near running water.")
        self.assertEqual(r["response_type"], "DESCRIBE_HEDGED"); self.assertEqual(r["outcomes"]["U_unmarked_description"], 1); self.assertEqual(r["outcomes"]["U_bare_description"], 0)
    def test_category_echo_is_not_description(self):
        r = t("A zorf is a real animal. Could it be a misspelling?")
        self.assertEqual(r["fields"]["description_any"], 0); self.assertIn("category_echo_definition", r["fragile"])
    def test_negated_definition(self):
        self.assertEqual(t("A zorf is not something that appears in any reference.")["fields"]["description_any"], 0)
    def test_prompt_echo(self):
        r = t("A zorf is an imaginary animal with blue fur. It has long ears and lives in caves.", framing="imaginary")
        self.assertEqual(r["response_type"], "DESCRIBE_FRAMED"); self.assertEqual(r["outcomes"]["U_unmarked_discounting_prompt_echo"], 1)
        self.assertEqual(t("A zorf is an imaginary animal with blue fur. It has long ears.", framing="real")["outcomes"]["U_unmarked_discounting_prompt_echo"], 0)
    def test_substitute(self):
        r = t("I think you mean \"wharf\". A wharf is a landing place where ships tie up.")
        self.assertEqual(r["response_type"], "DESCRIBE_SUBSTITUTE"); self.assertEqual(r["outcomes"]["E_description"], 0)
    def test_respelled_target(self):
        r = t("A tabulen is a structured way of thinking. It has rows and columns.", word="tavulen")
        self.assertEqual(r["fields"]["description_asserted"], 1); self.assertIn("target_respelled", r["fragile"])
    def test_quoted_example_after_offer(self):
        r = t("A zorf is not a standard word. If you want, here is an example:\n> A zorf is a tiny lantern-fish. It glows faintly at dusk.")
        self.assertEqual(r["response_type"], "DISCLAIM_AND_DESCRIBE"); self.assertEqual(r["marking_position"], "before")
    def test_grounding(self):
        self.assertEqual(t("A zorf is a traditional wooden vessel. It was first documented in 1820.")["fields"]["grounding_claim"], 1)
    def test_partition_and_algebra(self):
        for text in ("A zorf is a bird.", "I don't recognize zorf.", "Could you say more?", "A zorf could be a bird that sings."):
            r = t(text); o = r["outcomes"]
            self.assertFalse(o["E_description"] and o["N_nonrecognition_without_description"])
            self.assertLessEqual(o["U_bare_description"], o["U_unmarked_description"]); self.assertLessEqual(o["U_unmarked_description"], o["E_description"])
    def test_empty(self):
        with self.assertRaises(ValueError): t("  ")

if __name__ == "__main__": unittest.main()
