"""Content-neutral in-memory API stand-ins; never touches a provider endpoint."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import run_bestiary as r
from test_collector import response


class IntegrationTests(unittest.TestCase):
    def test_check_freeze_both_batches_and_analysis_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ["run_bestiary.py","bestiary_scorer.py","analyze_bestiary.py","requirements-analysis.txt","docs/implementation-protocol.md",
                         "docs/gpt-proposal/PREREGISTRATION_GPT.md","docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md","docs/gpt-proposal/inventories-gpt-v1.json"]:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r.ROOT/name,target)
            shutil.copytree(r.ROOT/"tests",root/"tests",ignore=shutil.ignore_patterns("__pycache__"))
            (root/"stimuli").mkdir()
            shutil.copyfile(r.ROOT/"stimuli/known-words.txt",root/"stimuli/known-words.txt")
            fresh=root/"stimuli/fresh-words.txt"
            fresh.write_text(''.join(('human' if i<8 else 'model')+' zuvem'+chr(97+i)+'\n' for i in range(24)))
            def request(model,body,key):
                prompt=(body.get("input") or body.get("messages"))[0]["content"]
                text="This is fictional. It has blue fur." if "imaginary" in prompt else "I don't recognize that word."
                return response(model,text=text)
            worker=r.Collector(root,keys={v:"FAKE" for v in r.KEY_NAMES.values()},request=request)
            try:
                with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(fresh.read_bytes())}),patch.dict(r.REPS,{"fresh":1,"known":1}),contextlib.redirect_stdout(io.StringIO()):
                    worker.check(r.MODELS)
                    worker.freeze("gpt-v1")
                    worker.run("fresh")
                    worker.run("known")
                self.assertEqual(len(worker.ledger.rows()),2568)
                before=len(worker.ledger.rows())
                with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(fresh.read_bytes())}),contextlib.redirect_stdout(io.StringIO()):
                    worker.run("fresh")
                self.assertEqual(len(worker.ledger.rows()),before)
            finally:
                worker.ledger.db.close()
            # Actual entry point, full 50,000 bootstrap draws; all text is synthetic.
            result=subprocess.run([sys.executable,"analyze_bestiary.py"],cwd=root,capture_output=True,text=True,timeout=120)
            self.assertEqual(result.returncode,0,result.stderr)
            primary=json.loads((root/"analysis/primary.json").read_text())
            self.assertEqual(len(primary["fresh"]["contrasts"]),8)
            self.assertEqual(primary["fresh"]["contrasts"][0]["effect"],1)
            self.assertEqual(primary["fresh"]["contrasts"][0]["bootstrap_degenerate"],True)
            self.assertEqual(json.loads((root/"analysis/audit.json").read_text()),[])
            secondary=json.loads((root/"analysis/secondary-contrasts.json").read_text())
            self.assertTrue(any(c["kind"]=="generation_batch_interaction" for c in secondary["contrasts"]))


if __name__=="__main__":unittest.main()
