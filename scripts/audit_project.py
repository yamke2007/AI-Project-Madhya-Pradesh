"""Structural/evidence audit, not certification of blocked Phase 2 gates."""
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agriagent.pipeline import ROOT,LOG_COLUMNS
from eval.run_eval import COLUMNS

REQUIRED=["README.md","run.py","requirements.txt","config.json","docs/source_agent_map.csv","docs/challenge.md",
 "docs/demo_guide.md","docs/phase2_implementation_status.md","eval/case_index.json","eval/run_eval.py","eval/phase2_metrics.csv",
 "eval/adapter_comparison.csv","logs/automation_log.csv","db/schema.sql","db/dictionary.md","db/dump/agriagent.sql",
 "db/dump/observations.json","data/manifest.csv","docs/evaluation_protocol.pdf","evidence/test_report.json"]

def read_csv(path):
    with Path(path).open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f);return r.fieldnames,list(r)

def main():
    checks=[]
    def check(name,ok,detail):checks.append(dict(check=name,passed=bool(ok),detail=detail))
    check("required_paths",all((ROOT/p).is_file() for p in REQUIRED),[p for p in REQUIRED if not (ROOT/p).is_file()])
    _,mapping=read_csv(ROOT/"docs/source_agent_map.csv");_,original=read_csv(ROOT/"Source_Inventory/source_inventory.csv")
    check("inventory_cardinality",len(mapping)==len(original)==23,len(mapping))
    mapped_agents = sorted({agent.strip() for row in mapping for agent in row["agent"].split(",") if agent.strip()})
    check("agent_cards",all((ROOT/"docs/agents"/(agent+".md")).is_file() for agent in mapped_agents),mapped_agents)
    index=json.loads((ROOT/"eval/case_index.json").read_text(encoding="utf-8"))
    check("case_counts",len(index)>=30 and all(sum(c["agent"]==a for c in index)>=10 for a in ("directory","scheme","statistics")),len(index))
    check("reference_separation",all((ROOT/c["reference"]).is_file() and c["reference"]!=c["input"] for c in index),"Reference values kept separate from input")
    fields,metrics=read_csv(ROOT/"eval/phase2_metrics.csv")
    check("provisional_metrics_schema",fields==COLUMNS and {r["metric_id"] for r in metrics}=={"M"+str(i) for i in range(1,19)},"Official separate CSV header unavailable; audit checks only declared provisional schema")
    fields,logs=read_csv(ROOT/"logs/automation_log.csv")
    check("automation_schema",fields==LOG_COLUMNS and len({r["run_id"] for r in logs})==len(logs),len(logs))
    _,manifest=read_csv(ROOT/"data/manifest.csv")
    # Ignore OS metadata files; these are packaging artefacts, not source inputs.
    actual={p.relative_to(ROOT).as_posix() for folder in ("data/raw","data/derived","eval/cases") for p in (ROOT/folder).iterdir() if p.is_file() and p.name != ".DS_Store" and not p.name.startswith("._")}
    check("manifest_complete",{r["file"] for r in manifest}==actual,len(manifest))
    check("manifest_hashes",all(hashlib.sha256((ROOT/r["file"]).read_bytes()).hexdigest()==r["sha256"] for r in manifest),"SHA-256")
    baseline=json.loads((ROOT/"evidence/phase1_baseline.json").read_text())
    check("phase1_preserved",all(hashlib.sha256((ROOT/r["preserved"]).read_bytes()).hexdigest()==r["sha256"] for r in baseline),len(baseline))
    db=sqlite3.connect(":memory:")
    db.executescript((ROOT/"db/dump/agriagent.sql").read_text(encoding="utf-8"))
    integrity=db.execute("PRAGMA integrity_check").fetchone()[0]
    check("dump_restore",integrity=="ok" and not db.execute("PRAGMA foreign_key_check").fetchall(),integrity)
    rows=db.execute("SELECT count(*) FROM observations").fetchone()[0];db.close()
    check("real_data_dump",rows>0,rows)
    report=dict(status="structural_checks_passed" if all(c["passed"] for c in checks) else "failed",checks=checks,
      caveat="Structural checks do not certify independent held-out evaluation, official CSV layout, adapter comparison, live surprise inputs, LGD or multi-agent gates.")
    (ROOT/"evidence/audit_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
    return 0 if all(c["passed"] for c in checks) else 1

if __name__=="__main__":raise SystemExit(main())
