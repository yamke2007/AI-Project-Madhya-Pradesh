"""Tests for the Phase 2 upgrades: general table agent, supervisor hand-offs and
retries, local-model header mapping, and the new evaluation helpers.
Fixtures in tests/fixtures_tables/ are SYNTHETIC (made by make_table_fixtures.py)."""
import json
import os
import shutil
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from agriagent import llm
from agriagent.pipeline import ROOT, process

F = ROOT / "tests" / "fixtures_tables"


def has_tesseract(lang="eng"):
    try:
        import pytesseract
        return shutil.which("tesseract") is not None and lang in pytesseract.get_languages(config="")
    except Exception:
        return False


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        t = Path(self.temp.name)
        self.cfg = dict(database=str(t / "db.sqlite"), automation_log=str(t / "log.csv"), output_dir=str(t / "out"))
        os.environ["AGRIAGENT_LLM"] = "off"
        llm._state.clear()

    def keyset(self, records):
        return {(r["variable"], r["value"], r["unit"], r["crop"], r["location"], r["period"]) for r in records}

    def test_lgd_code_copied_only_from_registry(self):
        reg = Path(self.temp.name) / "lgd.json"
        reg.write_text(json.dumps({"1001": "Sehore", "1002": "Vidisha"}), encoding="utf-8")  # test registry, not real codes
        cfg = dict(self.cfg, lgd_registry=str(reg))
        r = process(F / "synthetic_district_apy.pdf", cfg, persist=False)
        codes = {x["location"]: x.get("lgd_code") for x in r["records"]}
        self.assertEqual(codes.get("sehore"), "1001")
        self.assertTrue(all(x["validation_status"] == "valid" for x in r["records"]))
        self.assertTrue(all(v is None for k, v in codes.items() if k not in ("sehore", "vidisha")))
        r2 = process(F / "synthetic_district_apy.pdf", self.cfg, persist=False)
        self.assertTrue(all("lgd_code" not in x for x in r2["records"]))

    def test_pdf_table_handoff_and_total_row(self):
        r = process(F / "synthetic_district_apy.pdf", self.cfg)
        self.assertEqual(r["status"], "complete")
        self.assertEqual(r["agents"], ["statistics", "tables"])
        self.assertTrue(r["handoffs"][0].startswith("statistics"))
        self.assertEqual(len(r["records"]), 9)  # Total row skipped
        self.assertIn(("production", "1120450", "tonne", "wheat", "sehore", "2022-23"), self.keyset(r["records"]))
        self.assertIn(("area", "268900", "hectare", "wheat", "narmadapuram", "2022-23"), self.keyset(r["records"]))
        self.assertTrue(all(x["locator"].startswith("page:1/table:1/row:") for x in r["records"]))

    def test_xlsx_mp_only(self):
        r = process(F / "synthetic_mandi_prices.xlsx", self.cfg)
        self.assertEqual(len(r["records"]), 6)  # Rajasthan row dropped
        self.assertIn(("modal_price", "4400", "INR/quintal", "soybean", "indore", "2024-10-14"), self.keyset(r["records"]))

    def test_html_and_generic_csv(self):
        r = process(F / "synthetic_prices.html", self.cfg)
        self.assertEqual((r["agent"], len(r["records"])), ("tables", 6))
        c = process(F / "synthetic_agmarknet.csv", self.cfg)
        self.assertIn(("modal_price", "6200", "INR/quintal", "chickpea", "sehore", "2024-10-14"), self.keyset(c["records"]))

    @unittest.skipUnless(has_tesseract("eng"), "tesseract not installed")
    def test_scanned_english_table(self):
        r = process(F / "synthetic_scan_en.png", self.cfg)
        self.assertIn(("production", "880.4", "'000 tonnes", "wheat", "dhar", "2021-22"), self.keyset(r["records"]))

    @unittest.skipUnless(has_tesseract("hin"), "Hindi OCR model not installed")
    def test_scanned_hindi_table(self):
        r = process(F / "synthetic_scan_hi.png", self.cfg)
        self.assertIn(("min_price", "5900", "INR/quintal", "chickpea", "sehore", "2024-10-15"), self.keyset(r["records"]))

    def test_tool_fault_retried(self):
        r = process(F / "synthetic_district_apy.pdf", self.cfg, inject_tool="pdfplumber.extract_tables")
        self.assertEqual((r["status"], r["retries"], len(r["records"])), ("complete", 1, 9))
        self.assertFalse(r["agent_trace"][2]["ok"])

    def test_failed_run_keeps_trace(self):
        r = process(ROOT / "data/raw/des_apy.html", self.cfg)
        self.assertEqual(r["status"], "failed")

    def test_model_header_mapping(self):
        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"models":[]}')

            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                body = json.dumps({"message": {"content": json.dumps({"3": "modal_price"})}}).encode()
                self.send_response(200); self.end_headers(); self.wfile.write(body)
        srv = HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        os.environ["AGRIAGENT_LLM"] = "on"
        llm.URL = f"http://127.0.0.1:{srv.server_port}"
        llm._state.clear()
        p = Path(self.temp.name) / "bhav.csv"
        p.write_text("District,Commodity,Date,Bhav (Rs/Qtl)\nIndore,Soyabean,14/10/2024,4400\n", encoding="utf-8")
        r = process(p, self.cfg)
        self.assertIn("llm.header_mapping", [t["tool"] for t in r["trajectory"]])
        self.assertEqual(r["records"][0]["column_mapped_by"], "model")
        self.assertEqual((r["records"][0]["variable"], r["records"][0]["value"]), ("modal_price", "4400"))

    def test_model_unavailable_does_not_guess(self):
        p = Path(self.temp.name) / "bhav.csv"
        p.write_text("District,Commodity,Date,Bhav (Rs/Qtl)\nIndore,Soyabean,14/10/2024,4400\n", encoding="utf-8")
        r = process(p, self.cfg)
        self.assertEqual(r["status"], "failed")
        self.assertNotIn("llm.header_mapping", [t["tool"] for t in r.get("trajectory", [])])

    def test_groundedness_and_agentevals(self):
        from eval.agent_metrics import grounded, trajectory_match
        r = process(F / "synthetic_prices.html", self.cfg)
        self.assertTrue(all(grounded(x) for x in r["records"]))
        self.assertTrue(trajectory_match(r["trajectory"], r["trajectory"], "strict"))
        self.assertFalse(grounded(dict(r["records"][0], value="99999")))


if __name__ == "__main__":
    unittest.main()
