import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import run_bestiary as r


def response(endpoint, text="ready", **overrides):
    if endpoint["provider"]=="openai":
        js=dict(id="fixture",model=endpoint["id"],status="completed",output=[dict(type="message",content=[dict(type="output_text",text=text)])],
                usage=dict(input_tokens=10,output_tokens=5,output_tokens_details=dict(reasoning_tokens=0)))
    else:
        js=dict(id="fixture",model=endpoint["id"],stop_reason="end_turn",content=[dict(type="text",text=text)],usage=dict(input_tokens=10,output_tokens=5))
    js.update(overrides)
    return 200,json.dumps(js),{"x-request-id":"fixture","authorization":"never export"}


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.calls=[]
        self.model=r.BY_ID["gpt-6-sol"]
        def request(model,body,key):
            self.calls.append(body)
            return response(model)
        self.collector=r.Collector(self.root,keys={v:"FAKE" for v in r.KEY_NAMES.values()},request=request,wait=lambda n:None)
        self.trial=dict(trial_id="fixture",prompt="Describe a zuvem.")

    def tearDown(self):
        self.collector.ledger.db.close()
        self.temp.cleanup()

    def test_refusal_and_block_boundaries_preserved(self):
        js=json.loads(response(self.model)[1])
        js["output"][0]["content"]=[dict(type="refusal",refusal="No."),dict(type="output_text",text="More.")]
        parsed=r.parse_response(self.model,200,json.dumps(js))
        self.assertEqual(parsed["response"],"No.\nMore.")
        self.assertTrue(parsed["valid"] and parsed["refusal"])

    def test_failed_200_not_terminal(self):
        parsed=r.parse_response(self.model,200,response(self.model,status="failed",output=[],error={"code":"server_error"})[1])
        self.assertFalse(parsed["valid"] or parsed["terminal"])
        self.assertTrue(parsed["retryable"])

    def test_unknown_schema_and_usage_fail_closed(self):
        for changes in [dict(status="queued"),dict(output=None),dict(usage={}),dict(model=None)]:
            self.assertFalse(r.parse_response(self.model,200,response(self.model,**changes)[1])["valid"])

    def test_empty_and_truncated_not_regenerated(self):
        for index,changes in enumerate([{},dict(status="incomplete",incomplete_details={"reason":"max_output_tokens"})]):
            calls=[]
            self.collector.request=lambda model,body,key: calls.append(1) or response(model,text="",**changes)
            trial=dict(self.trial,trial_id=str(index))
            self.collector.one(self.model,"fresh",trial)
            self.collector.one(self.model,"fresh",trial)
            self.assertEqual(len(calls),1)

    def test_preflight_cost_and_idempotent_settings(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.collector.check([self.model])
            saved=self.collector.ledger.get("settings:"+self.model["id"])
            self.collector.check([self.model])
        self.assertEqual(len(self.calls),1)
        self.assertGreater(self.collector.ledger.total("openai"),0)
        self.assertEqual(saved,self.collector.ledger.get("settings:"+self.model["id"]))
        changed=dict(self.model,params={"temperature":.3})
        with self.assertRaises(r.StudyError):self.collector.check([changed])

    def test_preflight_rejects_other_model(self):
        self.collector.request=lambda model,body,key:response(model,model="gpt-6-luna")
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"preflight",self.trial)
        self.assertEqual(self.collector.ledger.get("halt"),"unexpected_preflight_model")

    def test_snapshot_alias_then_drift(self):
        self.collector.request=lambda model,body,key:response(model,model=model["id"]+"-2026-09-01")
        self.collector.one(self.model,"preflight",self.trial)
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"fresh",self.trial,expected=self.model["id"])

    def test_reasoning_is_persistent_halt_and_no_fallback(self):
        self.collector.request=lambda model,body,key:response(model,usage=dict(input_tokens=1,output_tokens=2,output_tokens_details=dict(reasoning_tokens=1)))
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"fresh",self.trial)
        self.assertTrue(self.collector.ledger.get("halt"))
        self.assertTrue(all(r.payload(m,"ready").get("max_output_tokens",r.payload(m,"ready").get("max_tokens"))==1024 for m in r.MODELS))

    def test_timeout_reservation_and_retry_limit_survive_restart(self):
        self.collector.request=lambda *args: (_ for _ in ()).throw(TimeoutError())
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial),"exhausted")
        rows=self.collector.ledger.rows()
        self.assertEqual(len(rows),6)
        self.assertEqual(self.collector.ledger.total("openai"),sum(x["reservation"] for x in rows))
        self.collector.ledger.db.close()
        self.collector=r.Collector(self.root,keys={"OPENAI_API_KEY":"FAKE"},request=lambda *args:self.fail("must not retry"))
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial),"exhausted")

    def test_started_attempt_survives_crash_with_liability(self):
        aid,_=self.collector.ledger.start(self.model,"fresh",self.trial,r.payload(self.model,self.trial["prompt"]),6)
        expected=self.collector.ledger.total("openai")
        self.collector.ledger.db.close()
        self.collector=r.Collector(self.root,keys={"OPENAI_API_KEY":"FAKE"})
        self.assertEqual(self.collector.ledger.rows()[0]["state"],"ambiguous")
        self.assertEqual(self.collector.ledger.total("openai"),expected)
        self.collector.ledger.reconcile(aid,0,"Provider invoice confirms no charge, fixture")
        self.assertEqual(self.collector.ledger.total("openai"),0)
        self.assertEqual(self.collector.ledger.db.execute("SELECT COUNT(*) FROM reconciliation").fetchone()[0],1)

    def test_resume_rejects_changed_prompt(self):
        self.collector.one(self.model,"fresh",self.trial)
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"fresh",dict(self.trial,prompt="Changed."))

    def test_raw_payload_retained_and_export_repairs_torn_file(self):
        self.collector.one(self.model,"fresh",self.trial)
        path=self.root/"data/raw/fresh/gpt-6-sol.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text('{"broken":')
        self.collector.export()
        self.assertEqual(json.loads(path.read_text())["response"],"ready")
        attempts=[json.loads(x) for x in (self.root/"data/attempts.jsonl").read_text().splitlines()]
        self.assertEqual(json.loads(attempts[0]["raw"])["status"],"completed")
        self.assertNotIn("authorization",attempts[0]["response_headers"])
        self.assertNotIn("FAKE",(self.root/"data/attempts.jsonl").read_text())

    def test_reservations_are_atomic_under_concurrency(self):
        amount,_=r.reservation(self.model,r.payload(self.model,self.trial["prompt"]))
        results=[]
        with patch.object(r,"BUDGET",amount):
            def dispatch(i):
                results.append(self.collector.ledger.start(self.model,"fresh",dict(self.trial,trial_id=str(i)),r.payload(self.model,self.trial["prompt"]),6)[1])
            workers=[threading.Thread(target=dispatch,args=(i,)) for i in range(10)]
            for worker in workers:worker.start()
            for worker in workers:worker.join()
        self.assertEqual(results.count("started"),1)
        self.assertEqual(self.collector.ledger.total("openai"),amount)

    def test_bad_hash_and_composition_rejected(self):
        (self.root/"stimuli").mkdir()
        path=self.root/"stimuli/fresh-words.txt";path.write_text("bad changedword\n")
        with self.assertRaises(r.StudyError):r.load_words(self.root,"fresh")
        with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(path.read_bytes())}):
            with self.assertRaises(r.StudyError):r.load_words(self.root,"fresh")

    def test_process_lock_rejects_second_process(self):
        script="from pathlib import Path; import run_bestiary as r;\nwith r.process_lock(Path(__import__('sys').argv[1])): pass"
        with r.process_lock(self.root):
            child=subprocess.run([sys.executable,"-c",script,str(self.root)],capture_output=True,text=True,cwd=r.ROOT)
        self.assertNotEqual(child.returncode,0)
        self.assertIn("Another collector",child.stderr)

    def test_legacy_files_require_migration(self):
        root=self.root/"legacy";path=root/"data/raw/known/test.jsonl";path.parent.mkdir(parents=True);path.write_text('{}\n')
        with self.assertRaises(r.StudyError):r.Ledger(root)

    def test_private_trial_order_and_freeze(self):
        for name in ["run_bestiary.py","bestiary_scorer.py","analyze_bestiary.py","requirements-analysis.txt","docs/implementation-protocol.md",
                     "docs/gpt-proposal/PREREGISTRATION_GPT.md","docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md","docs/gpt-proposal/inventories-gpt-v1.json",
                     "prereg/CLAUDE_PREREG.md","prereg/claude_scorer.py"]:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r.ROOT/name,target)
        shutil.copytree(r.ROOT/"tests",self.root/"tests",ignore=shutil.ignore_patterns("__pycache__"))
        (self.root/"stimuli").mkdir(exist_ok=True)
        shutil.copyfile(r.ROOT/"stimuli/known-words.txt",self.root/"stimuli/known-words.txt")
        fresh=self.root/"stimuli/fresh-words.txt"
        fresh.write_text(''.join(('human' if i<8 else 'model')+' zuvem'+chr(97+i)+'\n' for i in range(24)))
        with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(fresh.read_bytes())}),contextlib.redirect_stdout(io.StringIO()):
            self.collector.check(r.MODELS)
            self.collector.freeze("gpt-v1")
            doc=self.collector.verify_freeze()
            self.assertEqual(sum(len(t) for t in doc["batches"]["fresh"].values()),9600)
            self.assertEqual(sum(len(t) for t in doc["batches"]["known"].values()),6400)
            self.assertEqual(doc["code_hashes"]["prereg/claude_scorer.py"],
                             "7244846fd96c884aa322d5b4d3a5c242dc048c67d825ceb94a03bf1a21fabd95")
            with self.assertRaises(r.StudyError):self.collector.run("known")
            (self.root/"bestiary_scorer.py").write_text("modified")
            with self.assertRaises(r.StudyError):self.collector.verify_freeze()


if __name__=="__main__":unittest.main()
