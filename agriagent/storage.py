import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript((ROOT / "db/schema.sql").read_text(encoding="utf-8"))
    return db

def store(path, result):
    with connect(path) as db:
        db.execute("INSERT OR IGNORE INTO sources VALUES (?,?,?,?)",(result["source"],result["source_url"],result["input_sha256"],result["input"]))
        db.execute("UPDATE sources SET input_path=?,url=CASE WHEN url='unknown' THEN ? ELSE url END WHERE source=?",(result["input"],result["source_url"],result["source"]))
        db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?)",(result["run_id"],result["source"],result["started_at"],result["status"],result["agent"],json.dumps(result["errors"])))
        inserted = 0
        for r in result["records"]:
            values = [str(r[k]) for k in ("source","source_type","agent","run_id","locator","crop","location","period","variable","value","unit","validation_status")]
            cur = db.execute("INSERT OR IGNORE INTO observations (source,source_type,agent,run_id,locator,crop,location,period,variable,value,unit,validation_status,payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",values+[json.dumps(r,ensure_ascii=False)])
            inserted += cur.rowcount
            if not cur.rowcount:
                key=[r[k] for k in ("source","locator","crop","location","period","variable")]
                existing=db.execute("SELECT id,payload FROM observations WHERE source=? AND locator=? AND crop=? AND location=? AND period=? AND variable=?",key).fetchone()
                payload=json.loads(existing[1])
                # Revalidate the same immutable source observation under current declared rules.
                # Keep its original insertion run; retain the recheck run separately.
                payload.update(validation_status=r["validation_status"],validation_errors=r["validation_errors"],validation_rechecked_run_id=result["run_id"])
                db.execute("UPDATE observations SET validation_status=?,payload=? WHERE id=?",(r["validation_status"],json.dumps(payload,ensure_ascii=False),existing[0]))
        db.execute("INSERT INTO attempts VALUES (?,?,?,?)",(result["run_id"],len(result["records"]),inserted,len(result["records"])-inserted))
    return {"inserted":inserted,"duplicates":len(result["records"])-inserted}

def dump(path, target):
    target = Path(target)
    target.mkdir(parents=True,exist_ok=True)
    with connect(path) as db:
        (target/"agriagent.sql").write_text("\n".join(db.iterdump()),encoding="utf-8")
        rows = [json.loads(r[0]) for r in db.execute("SELECT payload FROM observations ORDER BY id")]
        (target/"observations.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
