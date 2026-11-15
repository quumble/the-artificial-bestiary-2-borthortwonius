"""Test category logic with controlled, synthetic scorer outputs.

These fixtures do not validate upstream regexes; an optional real-scorer smoke
check can be enabled with BESTIARY2_REPO=/path/to/repo.
"""
import csv
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from coding_heuristic import (
    GPT_PRIMARY, classify_fable, code_one, definition_agreement, load_upstream,
    split_condition,
)
import code_responses


class FakeGPT:
    VERSION = "gpt-bestiary-2-v1.0"

    @staticmethod
    def score(response, word, prompt):
        raw = response.lower()
        text = response
        needle = word.lower() + " is"
        tests = {
            "M01": "imaginary" in raw,
            "M02": "might" in raw,
            "M03": "don't recognize" in raw or "not a recognized" in raw,
            "M09": needle in raw,
            "M04": "let's imagine" in raw,
            "M05": "sounds like" in raw,
            "M07": "could you provide" in raw,
            "M08": "would you like" in raw,
            "M10": "it has" in raw,
            "M32": "typo" in raw,
        }
        f = {k: {"any": int(v)} for k, v in tests.items()}
        f["M02"]["components"] = {"modal": {"any": int("might" in raw)}}
        f["M13"] = {"state": "definition_only" if tests["M09"] else "neither"}
        f["M31"] = {"components": {k: {"any": 0} for k in ("animal", "object", "idea")}}
        matches = []
        for family, phrase in (("M01", "imaginary"), ("M02", "might"),
                               ("M03", "not a recognized"), ("M09", needle),
                               ("M10", "it has")):
            at = raw.find(phrase)
            if at >= 0:
                matches.append({"family": family, "entry": phrase,
                                "raw_span": [at, at + len(phrase)], "raw_text": text[at:at + len(phrase)],
                                "local_negation": family == "M09" and "not" in raw,
                                "quotation_overlap": raw.startswith('"')})
        return {"version": FakeGPT.VERSION, "usable": True, "features": f, "matches": matches}


class FakeFable:
    SCORER_VERSION = "claude-fable-5-2/1.1"

    @staticmethod
    def normalize(response):
        return response.lower()

    @staticmethod
    def find_all(norm, family):
        cues = {"nonrec": "not a recognized" if "not a recognized" in norm else "don't recognize",
                "fiction": "imaginary", "construct": "let's imagine", "interp": "sounds like"}
        phrase = cues[family]
        at = norm.find(phrase)
        return [(at, at + len(phrase), phrase)] if at >= 0 else []

    @staticmethod
    def definition_forms(norm, word):
        needle = word.lower() + " is"
        m = norm.find(needle)
        if m < 0:
            return [], []
        span = (m, m + len(needle), needle)
        return ([], [span]) if " is not " in norm else ([span], [])

    @staticmethod
    def score_text(text, word):
        raw = text.lower()
        nonrec = int("don't recognize" in raw or "not a recognized" in raw)
        fic = int("imaginary" in raw)
        construct = int("let's imagine" in raw)
        interp = int("sounds like" in raw)
        attr = raw.count("it has")
        pos, neg = FakeFable.definition_forms(raw, word)
        e = int(bool(pos) or attr >= 2)
        cue = int(bool(nonrec or fic or construct or interp))
        return {"desc_form": e, "unmarked_description": int(e and not cue),
                "nonrec_no_description": int(nonrec and not e),
                "cue_any": cue, "any_nonrec": nonrec, "any_fiction": fic,
                "any_construct": construct, "any_interp": interp,
                "any_hedge": int("might" in raw), "n_def": len(pos),
                "n_def_negated": len(neg), "n_attr": attr}


G = FakeGPT()
F = FakeFable()


def fixture(text, condition="real_animal", **kwargs):
    return {"word": "zorf", "prompt": f"Describe a zorf ({condition})", "response": text,
            "batch": "fresh", "model_requested": "gpt-6-luna", "word_set": "fresh-no-intent",
            "source_set_label": "fresh-no-intent-gpt", "condition": condition,
            "rep": 0, "terminal": True, "complete": True, "truncated": False, **kwargs}


class CategorizationTest(unittest.TestCase):
    def test_every_exclusive_class(self):
        cases = [(1, 0, 0, "D0_UNMARKED"),
                 (1, 1, 1, "D1_NONREC_MARKED"),
                 (1, 0, 1, "D2_OTHER_MARKED"),
                 (0, 1, 1, "N0_NONRECOGNITION"),
                 (0, 0, 1, "O0_CUED_OTHER"),
                 (0, 0, 0, "O1_UNMARKED_OTHER")]
        for a, b, c, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(classify_fable(a, b, c), expected)
        with self.assertRaises(ValueError):
            classify_fable(1, 1, 0)

    def test_condition_split(self):
        self.assertEqual(split_condition("neutral"), ("neutral", "none"))
        self.assertEqual(split_condition("type_of_idea"), ("type_of", "idea"))
        with self.assertRaises(ValueError):
            split_condition("imagined_animal")

    def test_unmarked_definition(self):
        got, _ = code_one(fixture("Zorf is a creature."), G, F)
        self.assertEqual(got["response_class"], "D0_UNMARKED")
        self.assertEqual([got[k] for k in ("F_E", "F_U", "F_N")], [1, 1, 0])
        self.assertEqual(got["gpt_definition_fable_E"], "BOTH")

    def test_marked_and_imaginary_inventory_sensitivity(self):
        got, evidence = code_one(fixture("Zorf is an imaginary animal.", "imaginary_animal"), G, F)
        self.assertEqual(got["response_class"], "D2_OTHER_MARKED")
        self.assertEqual((got["M01"], got["M01_without_imaginary"]), (1, 0))
        self.assertEqual(got["S_PROMPT_IMAGINARY_OVERLAP"], 1)
        self.assertTrue(evidence["gpt_matches"])

    def test_nonrecognition_without_description(self):
        got, _ = code_one(fixture("I don't recognize the word zorf."), G, F)
        self.assertEqual(got["response_class"], "N0_NONRECOGNITION")
        self.assertEqual((got["F_E"], got["F_N"]), (0, 1))

    def test_negated_definition_disagreement(self):
        got, evidence = code_one(fixture("Zorf is not a recognized species."), G, F)
        self.assertEqual(got["M09"], 1)
        self.assertEqual(got["F_E"], 0)
        self.assertEqual(got["F_def_negated_n"], 1)
        self.assertEqual(got["gpt_definition_fable_E"], "GPT_ONLY")
        self.assertEqual(got["response_class"], "N0_NONRECOGNITION")
        self.assertTrue(any(x["family"] == "definition_negated" for x in evidence["fable_matches_normalized"]))

    def test_attribute_only_fable_description(self):
        got, _ = code_one(fixture("It has blue fur. It has four legs."), G, F)
        self.assertEqual(got["F_E"], 1)
        self.assertEqual(got["M09"], 0)
        self.assertEqual(got["gpt_definition_fable_E"], "FABLE_ONLY")

    def test_empty_unusable_not_zero(self):
        got, ev = code_one(fixture("  "), G, F)
        self.assertEqual(got["response_class"], "X_UNUSABLE")
        self.assertEqual(got["M01"], "")
        self.assertEqual(got["F_E"], "")
        self.assertEqual(got["gpt_primary_eligible"], 0)
        self.assertEqual(ev["gpt_matches"], [])

    def test_truncation_exclusion_without_erasure(self):
        row = fixture("Zorf is an imaginary animal.")
        row["truncated"] = True
        got, _ = code_one(row, G, F)
        self.assertEqual(got["gpt_primary_eligible"], 1)
        self.assertEqual(got["fable_primary_eligible"], 0)
        self.assertEqual(got["F_E"], 1)

    def test_unknown_truncation_not_treated_as_false(self):
        row = fixture("Zorf is a creature.")
        del row["truncated"]
        got, _ = code_one(row, G, F)
        self.assertEqual(got["fable_primary_eligible"], "")

    def test_embedded_gpt_score_preserved(self):
        row = fixture("Zorf is an imaginary animal.")
        row["scoring"] = G.score(row["response"], row["word"], row["prompt"])
        got, _ = code_one(row, G, F, verify_embedded=True)
        self.assertEqual(got["gpt_scorer_origin"], "published_embedded")
        row["scoring"]["features"]["M01"]["any"] = 0
        with self.assertRaises(ValueError):
            code_one(row, G, F, verify_embedded=True)

    def test_derived_rates_exclude_truncation(self):
        inputs = [fixture("Zorf is a creature."), fixture("Zorf is an imaginary animal.")]
        inputs[1]["truncated"] = True
        inputs[1]["rep"] = 1
        coded = [code_one(i, G, F, index=j)[0] for j, i in enumerate(inputs)]
        _, results = code_responses.summaries(coded)
        self.assertEqual(results[0]["n_records"], 2)
        self.assertEqual(results[0]["n_fable_eligible"], 1)
        self.assertEqual(results[0]["F_E_rate"], 1.0)
        self.assertEqual(results[0]["M01_rate"], 0.5)

    def test_cli_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            infile = root / "input.jsonl"
            rows = [fixture("Zorf is a creature."), fixture("I don't recognize zorf.")]
            rows[1]["rep"] = 1
            infile.write_text("".join(json.dumps(v) + "\n" for v in rows), encoding="utf-8")
            with patch.object(code_responses, "load_upstream", return_value=(G, F, {"test": "fixture-only"})):
                audit = code_responses.run(infile, root, root / "out")
            self.assertEqual(audit["n_usable"], 2)
            with (root / "out" / "coded_responses.csv").open(newline="", encoding="utf-8") as f:
                coded = list(csv.DictReader(f))
            self.assertEqual([x["response_class"] for x in coded], ["D0_UNMARKED", "N0_NONRECOGNITION"])
            self.assertTrue((root / "out" / "descriptive_by_word_cell.csv").is_file())
            self.assertTrue((root / "out" / "coding_audit.json").is_file())


@unittest.skipUnless(os.environ.get("BESTIARY2_REPO"), "Set BESTIARY2_REPO for integration against the repository's actual scorers")
class OptionalUpstreamSmokeTest(unittest.TestCase):
    def test_actual_matchers(self):
        gpt, fable, prov = load_upstream(Path(os.environ["BESTIARY2_REPO"]))
        self.assertEqual(gpt.VERSION, "gpt-bestiary-2-v1.0")
        self.assertTrue(prov["source_hash_sha256"])
        row = fixture("Zorf is not a recognized word. It might be a typo.")
        result, _ = code_one(row, gpt, fable)
        self.assertEqual(result["M09"], 1)
        self.assertEqual(result["F_E"], 0)
        self.assertEqual(result["gpt_definition_fable_E"], "GPT_ONLY")


if __name__ == "__main__":
    unittest.main()
