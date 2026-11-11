import copy
import json
import tempfile
from pathlib import Path
import unittest
import numpy as np
import analyze_bestiary as a
import run_bestiary as r
import bestiary_scorer as s


def fixture():
    words=[("fresh-animal-intent","zuvema","human"),("fresh-animal-intent","zuvemb","human")]
    words += [("fresh-no-intent","fepal"+suffix,"model") for suffix in "abcd"]
    manifest=dict(batches={"fresh":{}},settings={})
    planned={};selected={};counts={}
    ordinal=0
    for model in r.MODELS:
        trials=r.build_trials("fresh",words)
        # Deliberately unequal usable repetitions across source sets.
        manifest["batches"]["fresh"][model["id"]]=trials
        manifest["settings"][model["id"]]=dict(model_config=model,model_returned=model["id"])
        for trial in trials:
            key=("fresh",model["id"],trial["trial_id"])
            planned[key]=trial
            if trial["word_set"].endswith("no-intent") and trial["rep"]>1:continue
            response="This is fictional." if trial["word_set"].endswith("animal-intent") and trial["reality"]=="imaginary" else "Blue."
            ordinal+=1
            selected[key]=dict(id=ordinal,attempt_id=str(ordinal),fields=dict(response=response,complete=True,truncated=False,refusal=False))
            counts[key]=1
    cells,rows=a.make_cells(planned,selected,counts)
    return manifest,planned,selected,counts,cells,rows


class AnalysisTests(unittest.TestCase):
    def test_equal_word_source_and_model_weights(self):
        manifest,_,_,_,cells,_=fixture()
        result=a.summarize_primary(cells,"fresh",manifest,draws=100)
        first=result["contrasts"][0]
        self.assertAlmostEqual(first["effect"],.5)
        self.assertAlmostEqual(first["alternative_word_count_weight"],1/3)
        self.assertTrue(first["bootstrap_degenerate"])
        self.assertFalse(first["confirmatory_direction"])
        self.assertAlmostEqual(first["bounds"][0],.1)
        self.assertAlmostEqual(first["bounds"][1],.9)

    def test_missing_required_cell_nulls_pool_but_bounds_remain(self):
        manifest,_,_,_,cells,_=fixture()
        key=next(k for k in cells if k[3]=="real_animal")
        cells[key]["primary"]["M01"]=None
        result=a.summarize_primary(cells,"fresh",manifest,draws=100)["contrasts"][0]
        self.assertIsNone(result["effect"])
        self.assertIsNone(result["ci95"])
        self.assertEqual(len(result["bounds"]),2)

    def test_bounds_and_complete_only_eligibility(self):
        self.assertEqual(a.bound_cell([1,0,None,None,None],5),[.2,.8])
        manifest,planned,selected,counts,_,_=fixture()
        key=next(iter(selected));selected[key]["fields"].update(response="Blue.",complete=False,truncated=True)
        cells,rows=a.make_cells(planned,selected,counts)
        c=cells[(key[0],key[1],planned[key]["word"],planned[key]["condition"])]
        self.assertEqual(c["primary"]["M01"],0)
        self.assertEqual(c["completion_bounds"]["M01"],[0,.2])
        sensitivity=a.sensitivities(rows,cells,manifest)
        eligibility=sensitivity["complete_only"]["eligibility"]
        item=next(e for e in eligibility if (e["batch"],e["model"],e["word"],e["condition"])==(key[0],key[1],planned[key]["word"],planned[key]["condition"]))
        self.assertEqual(item["eligible"],4)

    def test_audit_duplicate_and_wrong_request(self):
        model=r.MODELS[-1];trial=r.build_trials("fresh",[("fresh-animal-intent","zuvem","human")])[0]
        manifest=dict(batches={"fresh":{model["id"]:[trial]}},settings={model["id"]:dict(model_config=model,model_returned=model["id"])})
        body=r.payload(model,trial["prompt"])
        rec=dict(id=1,attempt_id="first",phase="fresh",model=model["id"],trial_id=trial["trial_id"],trial=trial,request=body,
                 request_hash=r.digest(r.canonical(body).encode()),fields=dict(valid=True,terminal=True,model_returned=model["id"],error=None,response="Blue."))
        second=copy.deepcopy(rec);second.update(id=2,attempt_id="second")
        wrong=copy.deepcopy(rec);wrong.update(id=3,attempt_id="wrong");wrong["request"]["temperature"]=0
        _,selected,audit,counts=a.select_records(manifest,[wrong,second,rec])
        self.assertEqual(next(iter(selected.values()))["attempt_id"],"first")
        self.assertEqual({x["reason"] for x in audit},{"duplicate_terminal","request_mismatch"})
        self.assertEqual(next(iter(counts.values())),3)

    def test_jsonl_corruption_is_not_silently_dropped(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"broken.jsonl";p.write_text('{}\n{"bad":')
            with self.assertRaises(ValueError):a.read_jsonl(p)

    def test_all_secondary_outputs_serialize_and_bootstrap_repeats(self):
        manifest,_,_,_,cells,rows=fixture()
        primary=a.summarize_primary(cells,"fresh",manifest,draws=100)
        self.assertEqual(primary,a.summarize_primary(cells,"fresh",manifest,draws=100))
        tables,summaries,reuse=a.secondary_tables(rows,cells)
        contrasts=a.planned_secondary_contrasts(cells,manifest)
        repetition=a.repetition_summaries(cells)
        json.dumps(dict(primary=primary,tables=tables,summaries=summaries,reuse=reuse,contrasts=contrasts,repetition=repetition),allow_nan=False)
        self.assertTrue(any(r["features"] for r in repetition))
        self.assertTrue(any(c["kind"]=="generation_frame_interaction" for c in contrasts["contrasts"]))


if __name__=="__main__":unittest.main()
