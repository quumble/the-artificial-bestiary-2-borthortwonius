import unittest
import bestiary_scorer as s


class ScorerTests(unittest.TestCase):
    def score(self,text):return s.score(text,"zuvem","Describe a zuvem. It is an imaginary animal.")

    def test_basic_contract(self):
        self.assertEqual(self.score("I don’t recognize it.")["features"]["M03"]["count"],1)
        self.assertEqual(self.score("recognize")["features"]["M03"]["count"],0)
        self.assertEqual(self.score("A **zuvem** is imaginary.")["features"]["M09"]["any"],1)
        result=self.score("Zuvem is not a recognized word.")
        self.assertEqual(result["features"]["M09"]["any"],1)
        self.assertEqual(result["features"]["M03"]["any"],1)

    def test_negative_quoted_phrases_retained(self):
        result=self.score('This is not fictional. "fictional" `fictional`.')
        matches=[m for m in result["matches"] if m["family"]=="M01"]
        self.assertEqual(len(matches),3)
        self.assertTrue(matches[0]["local_negation"])
        self.assertTrue(all(m["quotation_overlap"] for m in matches[1:]))

    def test_local_scope_not_inferred(self):
        result=self.score("It lives underground. It may eat insects.")
        self.assertEqual(result["features"]["M10"]["count"],1)
        self.assertEqual(result["features"]["M02"]["count"],1)
        self.assertEqual(result["features"]["M18"]["segments"],2)
        self.assertEqual(result["features"]["M14"]["count"],1)

    def test_definition_cue_order(self):
        self.assertEqual(self.score("Perhaps a zuvem is blue. This description is invented.")["features"]["M13"]["state"],"cue_first")
        self.assertEqual(self.score("A zuvem is blue. This description is invented.")["features"]["M13"]["state"],"definition_first")
        self.assertEqual(self.score("A zuvem is blue.")["features"]["M13"]["state"],"definition_only")
        self.assertEqual(self.score("Blue.")["features"]["M13"]["state"],"neither")

    def test_longest_and_cross_family_matches(self):
        self.assertEqual(self.score("I am not familiar with it.")["features"]["M03"]["count"],1)
        result=self.score("Could you provide some context?")
        self.assertEqual(result["features"]["M02"]["any"],1)
        self.assertEqual(result["features"]["M07"]["any"],1)

    def test_word_boundaries_contractions_hyphens(self):
        self.assertEqual(self.score("fictionality")["features"]["M01"]["count"],0)
        self.assertEqual(self.score("made-up")["features"]["M01"]["count"],1)
        self.assertEqual(self.score("couldn't")["features"]["M02"]["count"],0)
        self.assertEqual(self.score("zuvems are blue. zuvem's tail. prezuvem is blue.")["features"]["M09"]["count"],0)

    def test_raw_spans_unicode_expansion_crlf(self):
        raw="ＦＩＣＴＩＯＮＡＬ\r\nI don’t recognize it."
        result=self.score(raw)
        for match in result["matches"]:
            a,b=match["raw_span"]
            self.assertEqual(raw[a:b],match["raw_text"])
        normalized,mapping=s.normalize("ß\r\n")
        self.assertEqual(normalized,"ss\n")
        self.assertEqual(mapping,[(0,1),(0,1),(1,3)])
        self.assertEqual(result["features"]["M18"]["segments"],2)

    def test_prompt_does_not_enter_matching(self):
        result=self.score("Blue.")
        self.assertEqual(result["features"]["M01"]["any"],0)
        self.assertIsNone(result["features"]["M11"]["C"]["word_index"])

    def test_empty_and_punctuation(self):
        for raw in [None,"","  "]:
            self.assertFalse(self.score(raw)["usable"])
            self.assertIsNone(self.score(raw)["features"]["M01"])
        result=self.score("!!!")
        self.assertTrue(result["usable"])
        self.assertEqual(result["features"]["M01"]["any"],0)
        self.assertIsNone(result["features"]["M01"]["density"])

    def test_format_numbers_and_units(self):
        result=self.score("# Heading\n\n1. It weighs 1.5 kg.\n- Blue?\n")
        self.assertEqual(result["features"]["M19"],dict(headings=1,unordered_items=1,ordered_items=1,paragraphs=2))
        self.assertEqual(result["features"]["M23"]["number_unit_pairs"],1)
        self.assertEqual(result["features"]["M20"]["count"],1)

    def test_similarity_and_duplicate_denominators(self):
        self.assertIsNone(s.cell_features(["Hi"])["M26"])
        self.assertIsNone(s.cell_features(["Hi","Bye"])["M27"]["mean"])
        result=s.cell_features(["One two three.","one  TWO three."])
        self.assertEqual(result["M26"]["normalized"]["excess_fraction"],.5)
        self.assertEqual(result["M26"]["raw"]["excess_fraction"],0)
        self.assertEqual(result["M27"]["mean"],1)
        result=s.reuse_features({"zuvem":dict(word_set="a",responses=["A zuvem is blue"]),"fepal":dict(word_set="a",responses=["A fepal is blue"])})
        self.assertEqual(result["word_pairs"][0]["mean"],1)

    def test_length_prefix_and_prompt_exclusion(self):
        short=self.score("short")
        self.assertIsNone(short["features"]["M29"]["50"]["2"])
        result=self.score("animal creature wing")
        self.assertEqual(result["features"]["M31"]["components"]["animal"]["count"],2)
        self.assertEqual(len(result["features"]),32)

    def test_source_shapes(self):
        result=self.score("According to (smith, 2025), see https://example.org/a. DOI 10.1234/example.")
        self.assertEqual(result["features"]["M24"]["counts"],dict(urls=1,dois=1,author_year=1))


if __name__=="__main__":unittest.main()
