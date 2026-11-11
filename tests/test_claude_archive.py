"""Integrity and synthetic compatibility checks for the unmodified Claude files."""
import contextlib
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import run_bestiary as r
from test_collector import response

SCORER = r.ROOT / "prereg/claude_scorer.py"
spec = importlib.util.spec_from_file_location("frozen_claude_scorer", SCORER)
claude = importlib.util.module_from_spec(spec)
spec.loader.exec_module(claude)


class ClaudeArchiveTests(unittest.TestCase):
    def test_original_hashes_and_registered_commitment(self):
        hashes = {
            "CLAUDE_PREREG.md": "e679e793f2e4c57da0ff483bfe13d5d8b94d4e8913f9aa6fc41ec85d633a3669",
            "claude_scorer.py": "7244846fd96c884aa322d5b4d3a5c242dc048c67d825ceb94a03bf1a21fabd95",
        }
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((SCORER.parent / name).read_bytes()).hexdigest(), expected)
        self.assertIn(hashes["claude_scorer.py"], (SCORER.parent / "CLAUDE_PREREG.md").read_text())

    def test_review_examples_reproduce_frozen_behavior(self):
        # Last two cases document limitations, not desired semantic classifications.
        cases = [
            ("A flembrast is a bird. It eats seeds.", (1, 0, 1)),
            ("I don't recognize flembrast.", (0, 1, 0)),
            ("A flembrast is an imaginary bird.", (0, 0, 1)),
            ("A flembrast is perhaps a bird.", (1, 0, 1)),
            ("Here is more information: a flembrast is a fictional bird.", (1, 0, 1)),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                s = claude.score_text(text, "flembrast")
                self.assertEqual(tuple(s[k] for k in ("unmarked_description", "nonrec_no_description", "desc_form")), expected)

    def test_cli_reads_repaired_collector_export(self):
        model = next(m for m in r.MODELS if m["provider"] == "openai")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            collector = r.Collector(root, keys={v: "FAKE" for v in r.KEY_NAMES.values()},
                                    request=lambda m, body, key: response(m, text="A flembrast is a bird."))
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    collector.check([model])
                trial = r.build_trials("known", [("known-no-intent", "flembrast", "known-no-intent")])[0]
                collector.one(model, "known", trial, expected=model["id"])
                collector.export()
            finally:
                collector.ledger.db.close()
            out = root / "scores.csv"
            result = subprocess.run([sys.executable, str(SCORER), str(root / "data/raw/known"), "--out", str(out)],
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            with out.open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["trial_id"], trial["trial_id"])
            self.assertEqual(rows[0]["model_requested"], model["id"])
            self.assertEqual(rows[0]["unmarked_description"], "1")
            self.assertEqual(rows[0]["desc_form"], "1")
            self.assertEqual(rows[0]["request_settings"], "")
            self.assertEqual(rows[0]["visible_output_tokens"], "")


if __name__ == "__main__":
    unittest.main()
