import csv
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from agriagent.pipeline import ROOT,process
from agriagent.storage import connect,dump
from agriagent.normalization import validate,MISSING,NA
from eval.matching import matches,counts,f1
from eval.compare_adapters import score_predictions
from eval.contamination import audit
from eval.scoring import scaled_credit

class ProjectTests(unittest.TestCase):
    def read_csv(self,path,encoding="utf-8"):
        with path.open(encoding=encoding,newline="") as f:
            return list(csv.DictReader(f))
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.tmp=Path(self.temp.name)
        self.cfg=dict(database=str(self.tmp/"database.sqlite"),automation_log=str(self.tmp/"automation.csv"),output_dir=str(self.tmp/"output"))
    def csv(self,body):
        p=self.tmp/"new.csv"; p.write_text("crop,location,period,variable,value,unit\n"+body,encoding="utf-8"); return p
    def test_unseen_value_not_hardcoded(self):
        r=process(self.csv("गेहूं,मध्य प्रदेश,2024-25,production,987.654,tonne\n"),self.cfg)
        self.assertEqual(r["status"],"complete"); self.assertEqual(r["records"][0]["value"],"987.654")
        self.assertEqual(r["records"][0]["crop"],"wheat")
    def test_directory_real(self):
        r=process(ROOT/"data/raw/icar_kvk.html",persist=False)
        self.assertEqual(len(r["records"]),162); self.assertEqual(r["status"],"complete")
    def test_scheme_real_missing_explicit(self):
        r=process(ROOT/"data/raw/msp_scheme.html",persist=False)
        self.assertEqual(len(r["records"]),23); self.assertEqual(r["status"],"partial")
        self.assertTrue(any(o["value"]==MISSING for o in r["records"]))
    def test_pdf_real_conservative(self):
        r=process(ROOT/"data/raw/mp_economic_survey.pdf",persist=False)
        self.assertEqual(r["status"],"partial"); self.assertEqual(r["records"][0]["value"],"352.7")
        self.assertTrue(r["records"][0]["locator"].startswith("page:7/"))
    def test_empty_csv(self):
        self.assertEqual(process(self.csv(""),self.cfg)["status"],"failed")
    def test_bad_headers(self):
        p=self.tmp/"bad.csv"; p.write_text("a,b\n1,2")
        self.assertEqual(process(p,self.cfg)["status"],"failed")
    def test_negative_invalid(self):
        r=process(self.csv("wheat,mp,2024,production,-5,tonne\n"),self.cfg)
        self.assertEqual(r["status"],"partial");self.assertIn("implausible:value",r["records"][0]["validation_errors"])
    def test_bad_date(self):
        r=process(self.csv("wheat,mp,2024-02-31,production,5,tonne\n"),self.cfg)
        self.assertIn("invalid:period",r["records"][0]["validation_errors"])
    def test_invalid_financial_year(self):
        r=process(self.csv("wheat,mp,2024-99,production,5,tonne\n"),self.cfg)
        self.assertIn("invalid:financial_year",r["records"][0]["validation_errors"])
    def test_unknown_unit(self):
        r=process(self.csv("wheat,mp,2024,production,5,bags\n"),self.cfg)
        self.assertEqual(r["status"],"partial")
    def test_growth_percentage_can_exceed_100(self):
        r=process(self.csv("MISSING:not_applicable,mp,2024,irrigation_capacity_growth,585,percent\n"),self.cfg)
        self.assertEqual(r["status"],"complete")
    def test_proportion_cannot_exceed_100(self):
        r=process(self.csv("MISSING:not_applicable,mp,2024,insured_share,585,percent\n"),self.cfg)
        self.assertEqual(r["status"],"partial")
    def test_missing_file_logged(self):
        r=process(self.tmp/"absent.csv",self.cfg)
        self.assertEqual(r["status"],"failed")
        self.assertEqual(len(self.read_csv(self.tmp/"automation.csv")),1)
    def test_dynamic_template_rejected(self):
        r=process(ROOT/"data/raw/evikas_calculator.html",persist=False)
        self.assertEqual(r["status"],"failed"); self.assertIn("Unrendered",r["errors"][0])
    def test_extraction_fault_contained(self):
        r=process(self.csv("wheat,mp,2024,production,5,tonne\n"),self.cfg,fault="extract")
        self.assertEqual(r["status"],"failed");self.assertEqual(r["records"],[])
    def test_database_fault_contained(self):
        r=process(self.csv("wheat,mp,2024,production,5,tonne\n"),self.cfg,fault="database")
        self.assertEqual(r["status"],"failed");self.assertIn("Storage",r["errors"][-1])
    def test_duplicate_and_retrieval(self):
        path=self.csv("wheat,mp,2024,production,5,tonne\n")
        process(path,self.cfg);r=process(path,self.cfg)
        self.assertEqual(r["storage"]["duplicates"],1)
        with connect(self.cfg["database"]) as db:
            self.assertEqual(db.execute("SELECT count(*) FROM observations").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT sum(duplicates) FROM attempts").fetchone()[0],1)
    def test_dump_roundtrip(self):
        process(self.csv("wheat,mp,2024,production,5,tonne\n"),self.cfg)
        dump(self.cfg["database"],self.tmp/"dump")
        db=sqlite3.connect(":memory:");db.executescript((self.tmp/"dump/agriagent.sql").read_text(encoding="utf-8"))
        self.assertEqual(db.execute("SELECT count(*) FROM observations").fetchone()[0],1);db.close()
    def record(self,**changes):
        r=dict(crop="wheat",location="mp",period="2024",variable="production",value="100.0",unit="tonne",value_kind="decimal");r.update(changes);return r
    def test_relative_tolerance_boundary(self):
        self.assertTrue(matches(self.record(value="101"),self.record()))
        self.assertFalse(matches(self.record(value="101.01"),self.record()))
    def test_integer_exact(self):
        self.assertFalse(matches(self.record(value="100.5"),self.record(value="100",value_kind="integer")))
    def test_code_exact(self):
        self.assertFalse(matches(self.record(value="01",unit="text"),self.record(value="1",unit="text",value_kind="code")))
    def test_unit_conversion_and_wrong_unit(self):
        self.assertTrue(matches(self.record(value="100000",unit="kg"),self.record()))
        self.assertFalse(matches(self.record(unit="hectare"),self.record()))
    def test_wrong_context(self):
        for k,v in (("crop","rice"),("location","indore"),("period","2023")):
            self.assertFalse(matches(self.record(**{k:v}),self.record()))
    def test_zero_tolerance(self):
        self.assertFalse(matches(self.record(value="0.001"),self.record(value="0")))
    def test_no_duplicate_credit(self):
        self.assertEqual(counts([self.record(),self.record()],[self.record()]),(1,1,0))
    def test_f1_missing_penalized(self):
        self.assertEqual(f1(*counts([],[self.record()])),0)
    def test_case_counts_and_hashes(self):
        index=json.loads((ROOT/"eval/case_index.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(index),40)
        for agent in ("directory","scheme","statistics"):
            self.assertEqual(sum(c["agent"]==agent for c in index),10)
        self.assertGreaterEqual(sum(c["agent"]=="tables" for c in index),10)
        for c in index:
            self.assertEqual(hashlib.sha256((ROOT/c["input"]).read_bytes()).hexdigest(),c["input_sha256"])
    def test_references_match_sources_and_pipeline(self):
        index=json.loads((ROOT/"eval/case_index.json").read_text(encoding="utf-8"))
        for c in index:
            ref=json.loads((ROOT/c["reference"]).read_text(encoding="utf-8"))["records"]
            actual=process(ROOT/c["input"],persist=False)["records"]
            self.assertEqual(counts(actual,ref),(len(ref),0,0),c["case_id"])
    def test_source_map_count(self):
        inv=self.read_csv(ROOT/"Source_Inventory/source_inventory.csv","utf-8-sig")
        mapping=self.read_csv(ROOT/"docs/source_agent_map.csv")
        self.assertEqual(len(inv),len(mapping));self.assertEqual(len(mapping),23)
    def test_phase1_preserved(self):
        rows=json.loads((ROOT/"evidence/phase1_baseline.json").read_text())
        for r in rows:
            self.assertEqual(hashlib.sha256((ROOT/r["preserved"]).read_bytes()).hexdigest(),r["sha256"],r["original"])
    def test_manifest_covers_corpus(self):
        rows=self.read_csv(ROOT/"data/manifest.csv")
        required={p.relative_to(ROOT).as_posix() for folder in ("data/raw","data/derived","eval/cases") for p in (ROOT/folder).iterdir() if p.is_file() and not p.name.startswith(".")}  # ignore macOS .DS_Store
        self.assertEqual({r["file"] for r in rows},required)
        for r in rows:self.assertEqual(hashlib.sha256((ROOT/r["file"]).read_bytes()).hexdigest(),r["sha256"])
    def test_contamination_empty_and_overlap(self):
        (self.tmp/"eval/cases").mkdir(parents=True); (self.tmp/"data/raw").mkdir(parents=True)
        (self.tmp/"eval/cases/x").write_text("same")
        self.assertEqual(audit(self.tmp)["status"],"no_local_training_files")
        (self.tmp/"data/train").mkdir();(self.tmp/"data/train/x").write_text("same")
        self.assertEqual(audit(self.tmp)["status"],"overlap_detected")
    def test_adapter_requires_identical_cases(self):
        p=self.tmp/"pred.json";p.write_text("{}")
        index=json.loads((ROOT/"eval/case_index.json").read_text())
        with self.assertRaises(ValueError):score_predictions(p,index)
    def test_scoring_lower_is_better(self):
        self.assertEqual(scaled_credit(.5,.5,.1),0)
        self.assertAlmostEqual(scaled_credit(.3,.5,.1),.5)
        self.assertEqual(scaled_credit(0,.1,0),1)
    def test_optional_model_runner_blocked(self):
        r=subprocess.run([sys.executable,str(ROOT/"eval/infer_adapter.py"),"--model",str(self.tmp/"absent"),"--output",str(self.tmp/"pred.json")],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertEqual(json.loads(r.stdout)["status"],"blocked")
    def test_adapter_missing_outputs_blocked(self):
        target=self.tmp/"comparison.csv"
        r=subprocess.run([sys.executable,str(ROOT/"eval/compare_adapters.py"),"--output",str(target)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0);rows=self.read_csv(target)
        self.assertTrue(all(x["status"]=="blocked" and x["f1"]=="" for x in rows))
    def test_lgd_cannot_be_invented(self):
        record=self.record(source="s",source_type="Database",agent="statistics",run_id="r",locator="l",lgd_code="999")
        self.assertIn("unverified:lgd_code",validate(record))
    def test_page_limit(self):
        r=process(ROOT/"data/raw/mp_economic_survey.pdf",dict(max_pdf_pages=1),persist=False)
        self.assertEqual(r["status"],"failed")
    def test_unsupported_audio(self):
        p=self.tmp/"x.wav";p.write_bytes(b"RIFF")
        self.assertEqual(process(p,persist=False)["status"],"failed")
    def test_root_cli_complete(self):
        cfg=self.tmp/"config.json";cfg.write_text(json.dumps(self.cfg))
        p=self.csv("wheat,mp,2024,production,123,tonne\n")
        r=subprocess.run([sys.executable,str(ROOT/"run.py"),"--input",str(p),"--config",str(cfg)],capture_output=True,text=True,cwd=self.tmp)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)

if __name__=="__main__":unittest.main()
