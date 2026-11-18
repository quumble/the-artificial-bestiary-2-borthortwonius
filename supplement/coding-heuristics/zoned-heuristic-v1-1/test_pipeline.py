"""Input and freeze guards, using synthetic temporary files only."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_corpus as runner


class PipelineGuards(unittest.TestCase):
    def make_freeze(self, root):
        names = ["PLAN.md", "zoned_heuristic.py", "run_corpus.py", "test_zoned.py", "METHOD.md", "audit.py"]
        committed = {}
        lines = []
        for name in names:
            blob = f"synthetic {name}\n".encode()
            (root / name).write_bytes(blob)
            committed[name] = blob
            lines.append(f"{hashlib.sha256(blob).hexdigest()}  {name}\n")
        manifest = "".join(lines).encode()
        (root / "FREEZE.sha256").write_bytes(manifest)
        committed["FREEZE.sha256"] = manifest
        return committed

    def test_freeze_checks_working_files_and_commit_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            committed = self.make_freeze(root)
            def git_show(args, **kwargs):
                return committed[args[-1].split(":", 1)[1]]
            with patch.object(runner.subprocess, "check_output", side_effect=git_show):
                self.assertEqual(runner.verify_freeze("a" * 40, root, root),
                                 runner.sha(committed["FREEZE.sha256"]))
                (root / "zoned_heuristic.py").write_text("modified\n")
                with self.assertRaisesRegex(ValueError, "Frozen file changed"):
                    runner.verify_freeze("a" * 40, root, root)

    def test_different_committed_scorer_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            committed = self.make_freeze(root)
            committed["zoned_heuristic.py"] = b"different committed code"
            with patch.object(runner.subprocess, "check_output",
                              side_effect=lambda args, **kwargs: committed[args[-1].split(":", 1)[1]]):
                with self.assertRaisesRegex(ValueError, "Committed file differs"):
                    runner.verify_freeze("a" * 40, root, root)

    def test_full_sha_required_before_git(self):
        with patch.object(runner.subprocess, "check_output") as git:
            with self.assertRaisesRegex(ValueError, "full freeze commit"):
                runner.verify_freeze("main")
            git.assert_not_called()

    def test_raw_checksum_precedes_archive_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.zip"
            path.write_bytes(b"not the frozen archive")
            with self.assertRaisesRegex(ValueError, "Raw archive checksum"):
                runner.load_raw(path)

    def test_code_keys_must_be_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "codes.csv"
            path.write_text("key,value\nsame,0\nsame,1\n")
            with self.assertRaisesRegex(ValueError, "Duplicate code keys"):
                runner.read_codes(path)

    def test_modified_baseline_stops_before_scoring_or_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            old = repo / "supplement/coding-heuristics/zoned-heuristic-v1/results/response_codes.csv"
            old.parent.mkdir(parents=True)
            old.write_text("key,value\nmodified,1\n")
            out = repo / "output"
            with patch.object(runner, "verify_freeze", return_value="frozen"), \
                 patch.object(runner, "load_raw", return_value=([], "collection")), \
                 patch.object(runner, "score") as score:
                with self.assertRaisesRegex(ValueError, "Original code checksum"):
                    runner.run(repo / "data.zip", out, "a" * 40, repo)
                score.assert_not_called()
            self.assertFalse(out.exists())

    def test_csv_serialization_is_lf_and_preserves_quoted_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "codes.csv"
            rows = [{"key": "a", "value": 'a,b "quoted"'}, {"key": "b", "value": "plain"}]
            runner.write_csv(path, rows)
            self.assertNotIn(b"\r", path.read_bytes())
            self.assertEqual(runner.read_codes(path), {r["key"]: r for r in rows})
            with self.assertRaises(FileExistsError):
                runner.write_csv(path, rows)


if __name__ == "__main__":
    unittest.main()
