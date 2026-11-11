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
        for changes in [dict(status="queued"),dict(output=None),dict(usage={}),dict(model=None),dict(model={"id":"gpt-6-sol"})]:
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
        # In a study phase a changed identifier closes the slot and stops that lane only.
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial,expected=self.model["id"]),"identity")
        self.assertTrue(self.collector.lane_should_stop(self.model,"fresh","identity"))
        self.assertFalse(self.collector.ledger.get("halt"))
        self.assertEqual(self.collector.one(self.model,"fresh",dict(trial_id="next",prompt="Describe a zuvem."),expected=self.model["id"]),"lane_stopped")
        other=r.BY_ID["gpt-6-luna"]
        self.collector.request=lambda model,body,key:response(model)
        self.assertEqual(self.collector.one(other,"fresh",self.trial,expected=other["id"]),"terminal")

    def test_reasoning_is_persistent_halt_and_no_fallback(self):
        self.collector.request=lambda model,body,key:response(model,usage=dict(input_tokens=1,output_tokens=2,output_tokens_details=dict(reasoning_tokens=1)))
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"preflight",self.trial)
        self.assertTrue(self.collector.ledger.get("halt"))
        self.assertTrue(all(r.payload(m,"ready").get("max_output_tokens",r.payload(m,"ready").get("max_tokens"))==1024 for m in r.MODELS))

    def test_identity_drift_wins_over_reasoning_and_stops_without_caller_check(self):
        self.collector.request=lambda model,body,key:response(model,model="gpt-6-luna",
            usage=dict(input_tokens=1,output_tokens=2,output_tokens_details=dict(reasoning_tokens=1)))
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial,expected=self.model["id"]),"identity")
        fields=json.loads(self.collector.ledger.rows("fresh",self.model["id"])[0]["fields"])
        self.assertEqual(fields["protocol_violation"],"returned_model_changed")
        self.assertEqual(fields["reasoning_tokens"],1)
        self.assertFalse(fields["valid"])
        self.assertEqual(self.collector.ledger.get("lane_stopped:"+self.model["id"])["closed"],1)
        self.collector.request=lambda *args:self.fail("identity drift must prevent another dispatch")
        self.assertEqual(self.collector.one(self.model,"fresh",dict(self.trial,trial_id="next")),"lane_stopped")

    def test_identity_drift_in_malformed_payload_still_stops_lane(self):
        self.collector.request=lambda model,body,key:response(model,model="gpt-6-luna",output=None)
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial,expected=self.model["id"]),"identity")
        fields=json.loads(self.collector.ledger.rows("fresh",self.model["id"])[0]["fields"])
        self.assertEqual(fields["error"],"schema_error")
        self.assertEqual(fields["issue"],"returned_model_changed")
        self.assertTrue(self.collector.ledger.get("lane_stopped:"+self.model["id"]))

    def test_issue_threshold_is_checked_when_the_200th_closure_is_valid(self):
        def request(model,body,key):
            index=int(body["input"][0]["content"].split()[-1])
            return response(model,usage=dict(input_tokens=1,output_tokens=2,
                output_tokens_details=dict(reasoning_tokens=int(index<11))))
        self.collector.request=request
        for i in range(200):
            outcome=self.collector.one(self.model,"fresh",dict(trial_id=str(i),prompt="Fixture "+str(i)))
            if i<199:
                self.assertFalse(self.collector.ledger.get("lane_stopped:"+self.model["id"]))
        self.assertEqual(outcome,"terminal")
        stop=self.collector.ledger.get("lane_stopped:"+self.model["id"])
        self.assertEqual((stop["issues"],stop["closed"]),(11,200))
        self.collector.request=lambda *args:self.fail("threshold stop must prevent another dispatch")
        self.assertEqual(self.collector.one(self.model,"fresh",dict(trial_id="next",prompt="Fixture next")),"lane_stopped")

    def test_restart_recovers_threshold_crossing_before_later_inflight_completions(self):
        # Simulate committed results whose in-memory stop update was interrupted.
        # The final 11/221 rate is below 5%, but the closure-200 decision still binds.
        with patch.object(self.collector,"observe",return_value=None):
            for i in range(221):
                self.collector.request=lambda model,body,key,i=i:response(model,usage=dict(input_tokens=1,
                    output_tokens=2,output_tokens_details=dict(reasoning_tokens=int(i<11))))
                self.collector.one(self.model,"fresh",dict(trial_id=str(i),prompt="Fixture"))
        self.assertFalse(self.collector.ledger.get("lane_stopped:"+self.model["id"]))
        self.collector.ledger.db.close()
        self.collector=r.Collector(self.root,keys={"OPENAI_API_KEY":"FAKE"},request=lambda *args:self.fail("must not dispatch after recovery"))
        stop=self.collector.ledger.get("lane_stopped:"+self.model["id"])
        self.assertEqual((stop["issues"],stop["closed"]),(11,200))
        self.assertIn("recovered_utc",stop)
        self.assertEqual(self.collector.one(self.model,"fresh",dict(trial_id="next",prompt="Fixture")),"lane_stopped")

    def test_restart_recovers_identity_stop_after_committed_result(self):
        self.collector.request=lambda model,body,key:response(model,model="gpt-6-luna")
        with patch.object(self.collector,"observe",side_effect=RuntimeError("simulated interruption")):
            with self.assertRaisesRegex(RuntimeError,"simulated interruption"):
                self.collector.one(self.model,"fresh",self.trial,expected=self.model["id"])
        self.collector.ledger.db.close()
        self.collector=r.Collector(self.root,keys={"OPENAI_API_KEY":"FAKE"},request=lambda *args:self.fail("must not dispatch after recovery"))
        self.assertEqual(self.collector.ledger.get("lane_stopped:"+self.model["id"])["reason"],"returned model identifier changed")
        self.assertEqual(self.collector.one(self.model,"fresh",dict(self.trial,trial_id="next")),"lane_stopped")

    def test_study_issues_are_flagged_and_lane_stops_past_five_percent(self):
        reasoning=dict(usage=dict(input_tokens=1,output_tokens=2,output_tokens_details=dict(reasoning_tokens=1)))
        bad=set(range(0,200,25))                                  # 8 of the first 200 = 4%, under the rule
        state=dict(n=0)
        def request(model,body,key):
            i=state["n"];state["n"]+=1
            return response(model,**reasoning) if i in bad or i>=200 else response(model)
        self.collector.request=request
        outcomes=[]
        for i in range(260):
            trial=dict(trial_id="t%03d"%i,prompt="Describe a zuvem.")
            outcome=self.collector.one(self.model,"fresh",trial)
            outcomes.append(outcome)
            if outcome in {"issue","identity"} and self.collector.lane_should_stop(self.model,"fresh",outcome):
                break
        self.assertFalse(self.collector.ledger.get("halt"))
        self.assertEqual(outcomes[:200].count("issue"),8)          # tolerated, run continued
        self.assertEqual(outcomes[0],"issue")                      # an early issue does not stop a lane
        closed=len(outcomes);issues=outcomes.count("issue")
        self.assertTrue(issues>0.05*closed and (issues-1)<=0.05*(closed-1))   # stopped at the first crossing
        stop=self.collector.ledger.get("lane_stopped:"+self.model["id"])
        self.assertIn("5%",stop["reason"])
        calls=state["n"]
        self.assertEqual(self.collector.one(self.model,"fresh",dict(trial_id="t000",prompt="Describe a zuvem.")),"lane_stopped")
        self.assertEqual(state["n"],calls)                         # nothing regenerated
        flagged=[json.loads(row["fields"]) for row in self.collector.ledger.rows("fresh",self.model["id"],"t000")]
        self.assertEqual(flagged[0]["issue"],"reasoning_observed_in_reasoning_off_run")
        self.assertFalse(flagged[0]["valid"])

    def test_issue_slot_is_closed_across_restart_and_other_errors_count(self):
        self.collector.request=lambda model,body,key:(400,json.dumps({"error":{"message":"bad"}}),{})
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial),"issue")
        self.collector.request=lambda model,body,key:response(model)
        self.assertEqual(self.collector.one(self.model,"fresh",self.trial),"issue_closed")
        self.collector.request=lambda model,body,key:(401,json.dumps({"error":{"message":"key"}}),{})
        with self.assertRaises(r.StudyError):self.collector.one(self.model,"fresh",dict(trial_id="auth",prompt="Describe a zuvem."))

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
        path.write_text(''.join(('human' if i<8 else 'model')+' zuvem'+chr(97+i)+'\n' for i in range(24)))   # the old 8/16 layout
        with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(path.read_bytes())}):
            with self.assertRaises(r.StudyError):r.load_words(self.root,"fresh")
        path.write_text(''.join(('fresh-animal-intent','fresh-no-intent-claude','fresh-no-intent-gpt')[i//8]+' zuvem'+chr(97+i)+'\n' for i in range(24)))
        with patch.dict(r.EXPECTED_HASH,{"fresh":r.digest(path.read_bytes())}):
            words,_=r.load_words(self.root,"fresh")
        self.assertEqual([w[0] for w in words].count("fresh-no-intent"),16)
        self.assertEqual({w[2] for w in words},set(r.FRESH_SETS))

    def test_process_lock_rejects_second_process(self):
        script="from pathlib import Path; import run_bestiary as r;\nwith r.process_lock(Path(__import__('sys').argv[1])): pass"
        with r.process_lock(self.root):
            child=subprocess.run([sys.executable,"-c",script,str(self.root)],capture_output=True,text=True,cwd=r.ROOT)
        self.assertNotEqual(child.returncode,0)
        self.assertIn("Another collector",child.stderr)

    def test_legacy_files_require_migration(self):
        root=self.root/"legacy";path=root/"data/raw/known/test.jsonl";path.parent.mkdir(parents=True);path.write_text('{}\n')
        with self.assertRaises(r.StudyError):r.Ledger(root)

    def test_combined_freeze_requires_matching_registered_claude_analyzer_hash(self):
        paths=["run_bestiary.py","bestiary_scorer.py","analyze_bestiary.py","requirements-analysis.txt","docs/implementation-protocol.md",
               "docs/gpt-proposal/PREREGISTRATION_GPT.md","docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md","docs/gpt-proposal/inventories-gpt-v1.json",
               "prereg/CLAUDE_PREREG.md","prereg/claude_scorer.py"]+r.CLAUDE_FILES
        for name in paths:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r.ROOT/name,target)
        (self.root/"tests").mkdir()
        (self.root/"tests/test_fixture.py").write_text("# synthetic freeze fixture\n")
        analyzer=self.root/"analyze_claude.py"
        analyzer.write_text("# synthetic analyzer fixture\n")
        amendment=self.root/"prereg/CLAUDE_PREREG_AMENDMENT_1.md"
        amendment.write_text("`analyze_claude.py`, SHA-256 `"+"0"*64+"`\n")
        with self.assertRaisesRegex(r.StudyError,"Claude analyzer SHA-256 does not match"):
            self.collector.freeze("gpt-v1+claude-v1.1")
        amendment.write_text("`analyze_claude.py`, SHA-256 `"+r.digest(analyzer.read_bytes())+"`\n")
        # A matching commitment clears that gate and reaches the separate preflight gate.
        with self.assertRaisesRegex(r.StudyError,"Check all eight models"):
            self.collector.freeze("gpt-v1+claude-v1.1")

    def test_private_trial_order_and_freeze(self):
        for name in ["run_bestiary.py","bestiary_scorer.py","analyze_bestiary.py","requirements-analysis.txt","docs/implementation-protocol.md",
                     "docs/gpt-proposal/PREREGISTRATION_GPT.md","docs/gpt-proposal/MEASUREMENT_SPEC_GPT.md","docs/gpt-proposal/inventories-gpt-v1.json",
                     "prereg/CLAUDE_PREREG.md","prereg/claude_scorer.py"]:
            target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r.ROOT/name,target)
        shutil.copytree(r.ROOT/"tests",self.root/"tests",ignore=shutil.ignore_patterns("__pycache__"))
        (self.root/"stimuli").mkdir(exist_ok=True)
        shutil.copyfile(r.ROOT/"stimuli/known-words.txt",self.root/"stimuli/known-words.txt")
        fresh=self.root/"stimuli/fresh-words.txt"
        fresh.write_text(''.join(('fresh-animal-intent','fresh-no-intent-claude','fresh-no-intent-gpt')[i//8]+' zuvem'+chr(97+i)+'\n' for i in range(24)))
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
