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

class Repairs(unittest.TestCase):
    def test_nonrecognition_contractions(self):
        for subject in ("I'm", "I am", "I’m"):
            for form in ("unable to", "not able to"):
                for verb in ("identify", "verify", "recognize"):
                    with self.subTest(subject=subject, form=form, verb=verb):
                        r = t(f"{subject} {form} {verb} zorf as a known concept.")
                        self.assertEqual(r["response_type"], "DECLINE_PLAIN")
                        self.assertEqual(r["fields"]["nonrec_personal"], 1)

    def test_confidence_in_information_about_target(self):
        for text in ("I'm not confident I have reliable information about a zorf.",
                     "I am not confident that I have accurate information on zorf.",
                     "I'm not confident I have information about it.",
                     "I'm not confident I have reliable information.",
                     "I am not confident that I have reliable knowledge",
                     "I'm not confident I have data. Could you explain the word?"):
            with self.subTest(text=text):
                self.assertEqual(t(text)["response_type"], "DECLINE_PLAIN")

    def test_attribute_uncertainty_is_not_new_nonrecognition(self):
        for text in ("I'm not confident about its size.",
                     "I'm not confident I have reliable information about its size.",
                     "I'm not confident I have reliable information about zorf's weight.",
                     "I'm not confident I have reliable information about \"zorf\"'s weight.",
                     "I'm not able to carry the zorf."):
            with self.subTest(text=text):
                self.assertEqual(t(text)["fields"]["nonrec_personal"], 0)

    def test_colon_definition(self):
        for intro in ("Here's a", "Here is a", "Here’s a"):
            with self.subTest(intro=intro):
                r = t(f"{intro} zorf: a palm-sized device of smoky blue glass.")
                self.assertEqual(r["outcomes"]["E_description"], 1)
                self.assertEqual(r["counts"]["definitions"], 1)

    def test_colon_definition_exclusions(self):
        for text in ("Here's a zorf: a real animal.", "Here is a zorf: an imaginary idea.",
                     "Here's a zorf: not a known creature.", "Here's a zorf: a newly coined term.",
                     "Here's a zorf: a palm-sized device?", "Here's a zorf:", "# Zorf:",
                     "Here's a zorf: I think so.", "Here's a zorf: there you go.",
                     "Here's a zorf: perhaps later.",
                     "Could you describe this zorf: a palm-sized device?",
                     "If you want, here's a zorf: a palm-sized device."):
            with self.subTest(text=text):
                self.assertEqual(t(text)["outcomes"]["E_description"], 0)

    def test_modal_metalinguistic_complements(self):
        for complement in ("a newly coined term", "a misspelling", "a local name", "a technical word",
                           "something you're creating yourself", "something you are inventing"):
            with self.subTest(complement=complement):
                r = t(f"I don't recognize zorf. A zorf could be {complement}.")
                self.assertEqual(r["response_type"], "DECLINE_WITH_POSSIBILITIES")
                self.assertEqual(r["outcomes"]["E_description"], 0)

    def test_substantive_modal_complements_survive(self):
        for complement in ("an idea that spreads when people discuss it", "something with blue fur and six legs",
                           "a small animal that lives in caves", "an idea about words and memory"):
            with self.subTest(complement=complement):
                r = t(f"A zorf could be {complement}.")
                self.assertEqual(r["fields"]["description_hypothetical"], 1)

    def test_refusal_then_actual_hypothetical_description(self):
        r = t("I don't recognize zorf. It could be something you're creating yourself. "
              "I can help invent a concept. For example, a zorf could be an idea that spreads "
              "because people feel they discovered it independently.")
        self.assertEqual(r["response_type"], "DISCLAIM_AND_DESCRIBE")
        self.assertEqual(r["fields"]["description_hypothetical"], 1)

    def test_meta_guess_and_substantive_definition_in_one_segment(self):
        for text in ("A zorf could be a newly coined term, or a zorf could be a bird with blue wings.",
                     "A zorf could be a technical word, but a zorf is a blue bird."):
            with self.subTest(text=text):
                self.assertEqual(t(text)["outcomes"]["E_description"], 1)

    def test_explicit_near_correction_beats_respelling(self):
        r = t("You mean tabulen. A tabulen is a structured way of thinking.", word="tavulen")
        self.assertEqual(r["response_type"], "DESCRIBE_SUBSTITUTE")
        self.assertEqual(r["outcomes"]["E_description"], 0)
        self.assertNotIn("target_respelled", r["fragile"])

    def test_corrected_alternate_owns_following_attributes(self):
        for word, alternate in (("tavulen", "tabulen"), ("zorf", "wharf")):
            with self.subTest(word=word):
                r = t(f"You mean {alternate}. A {alternate} is a wooden platform. "
                      "It has a broad deck. It stands beside the water.", word=word)
                self.assertEqual(r["response_type"], "DESCRIBE_SUBSTITUTE")
                self.assertEqual(r["outcomes"]["E_description"], 0)

    def test_later_target_definition_restores_target_scope(self):
        r = t("You mean tabulen. A tabulen is a wooden platform. "
              "A tavulen is a small grey mammal. It lives in caves.", word="tavulen")
        self.assertEqual(r["outcomes"]["E_description"], 1)
        self.assertEqual(r["fields"]["substitute_description"], 1)

    def test_unprompted_respelling_is_preserved(self):
        r = t("A tabulen is a structured way of thinking. It has rows and columns.", word="tavulen")
        self.assertEqual(r["outcomes"]["E_description"], 1)
        self.assertIn("target_respelled", r["fragile"])

    def test_alias_claim_is_diagnostic_only(self):
        for text in ("A zorf (also spelled worf) is a small grey mammal.",
                     "A zorf is another name for a barn owl. It has a heart-shaped face. It lives in barns.",
                     "A zorf is an old-fashioned name that most people use for the barn owl. "
                     "It has a heart-shaped face. It lives in barns."):
            with self.subTest(text=text):
                r = t(text)
                self.assertIn("target_alias_claim", r["fragile"])
                self.assertEqual(r["outcomes"]["E_description"], 1)
                self.assertEqual(r["fields"]["substitute_description"], 0)
        self.assertNotIn("target_alias_claim", t("A zorf is a small grey mammal.")["fragile"])

    def test_fiction_and_habitual_may_rules_are_preserved(self):
        self.assertEqual(t("A zorf is a mythical bird.")["fields"]["mark_fiction"], 1)
        self.assertEqual(t("A zorf is a small bird. It may leave a pebble on the path.")["response_type"],
                         "DESCRIBE_HEDGED")

if __name__ == "__main__": unittest.main()
