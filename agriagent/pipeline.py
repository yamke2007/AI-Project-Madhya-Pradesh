import csv
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from . import extractors, normalization as n, orchestrator, storage

ROOT = Path(__file__).resolve().parents[1]
LOG_COLUMNS = ["run_id","started_at","input","input_sha256","agent","status","records","tool_calls","reference_calls","retries","manual_interventions","latency_seconds","error","agents","handoffs","llm_calls","orchestrator"]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def process(path, config=None, source_url="unknown", persist=True, fault=None, manual_interventions=0, inject_tool=None):
    cfg = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    cfg.update(config or {})
    path = Path(path).resolve()
    try:
        input_name = path.relative_to(ROOT).as_posix()
    except ValueError:
        input_name = str(path)
    start = time.perf_counter()
    result = dict(run_id=str(uuid.uuid4()),started_at=datetime.now(timezone.utc).isoformat(),input=input_name,
        input_sha256="unavailable",source="unavailable",source_url=source_url,agent="unrouted",source_type="unknown",
        status="failed",records=[],errors=[],warnings=[],trajectory=[],retries=0,manual_interventions=manual_interventions)
    try:
        if not path.is_file():
            raise extractors.ExtractionError("Input file does not exist")
        if path.stat().st_size > cfg["max_bytes"]:
            raise extractors.ExtractionError("Input exceeds configured byte limit")
        digest = sha(path)
        result.update(input_sha256=digest,source="sha256:"+digest)
        # Metadata contributes lineage only, never extracted answers or routing decisions.
        manifest = ROOT/"data/manifest.csv"
        lineage = None
        if manifest.exists():
            with manifest.open(encoding="utf-8",newline="") as stream:
                lineage = next((r for r in csv.DictReader(stream) if r["sha256"]==digest),None)
            if lineage:
                if source_url == "unknown":
                    result["source_url"] = lineage["url"]
                result["inventory_source"] = lineage["source"]
        if fault == "extract":
            extractors.detect(path)
            raise extractors.ExtractionError("Injected extraction failure")
        # Supervisor: plans specialists, retries transient tool faults, hands off on "no data".
        out = orchestrator.run(path, cfg, digest, inject_tool=inject_tool)
        result.update(agent="+".join(out["producers"]) or out["plan"][0], source_type=out["group"],
                      trajectory=out["trajectory"], agent_trace=out["agent_trace"], handoffs=out["handoffs"],
                      agents=out["plan"], retries=out["retries"], llm_calls=out["llm_calls"],
                      notes=out["notes"], orchestrator=out["engine"], useful_calls=out["useful_calls"])
        records, warnings = out["records"], out["warnings"]
        result["warnings"] = warnings
        lgd = None
        if cfg.get("lgd_registry"):
            lgd = json.loads(Path(cfg["lgd_registry"]).read_text(encoding="utf-8"))
        by_name = {}
        for code, name in (lgd or {}).items():
            by_name.setdefault(n.location(name), []).append(str(code))
        for record in records:
            record.update({k:result[k] for k in ("source","source_type","run_id")})
            record.setdefault("agent",result["agent"])
            record["crop"] = n.crop(record.get("crop",n.MISSING))
            record["location"] = n.location(record.get("location",n.MISSING))
            record["period"] = n.period(record.get("period",n.MISSING))
            if lineage and lineage.get("parent_file"):
                record["parent_file"] = lineage["parent_file"]
            if lgd and not record.get("lgd_code") and len(by_name.get(record["location"], [])) == 1:
                record["lgd_code"] = by_name[record["location"]][0]  # copied from the official registry, never guessed
            record["validation_errors"] = n.validate(record,lgd)
            record["validation_status"] = "invalid" if record["validation_errors"] else "valid"
        result["records"] = records
        result["status"] = "complete" if records and not warnings and all(r["validation_status"]=="valid" for r in records) else "partial"
        if not records:
            result["errors"].append("No records produced")
    except Exception as exc:
        result["status"] = "failed"
        result["errors"].append(type(exc).__name__+": "+str(exc))
        for k, v in getattr(exc, "details", {}).items():
            result[k] = v
    if persist and result["source"] != "unavailable":
        try:
            if fault == "database":
                raise OSError("Injected database failure")
            result["storage"] = storage.store(ROOT/cfg["database"],result)
        except Exception as exc:
            result["status"] = "failed"
            result["errors"].append("Storage: "+str(exc))
    result["latency_seconds"] = time.perf_counter()-start
    result["tool_calls"] = len(result["trajectory"])
    result["reference_calls"] = result.get("useful_calls",0)
    if persist:
        out = ROOT/cfg["output_dir"]
        out.mkdir(parents=True,exist_ok=True)
        (out/(result["run_id"]+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
        log = ROOT/cfg["automation_log"]
        log.parent.mkdir(parents=True, exist_ok=True)
        # Migrate older CSV schemas before appending; preserve history and leave
        # new fields blank for historical rows that cannot be reconstructed.
        if log.exists() and log.stat().st_size:
            with log.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                old_fields = reader.fieldnames or []
                old_rows = list(reader)
            if old_fields != LOG_COLUMNS:
                temp_log = log.with_suffix(log.suffix + ".migrating")
                with temp_log.open("w", encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=LOG_COLUMNS, extrasaction="ignore")
                    writer.writeheader()
                    for old_row in old_rows:
                        writer.writerow({field: old_row.get(field, "") or "" for field in LOG_COLUMNS})
                temp_log.replace(log)
        exists = log.exists() and log.stat().st_size
        with log.open("a",encoding="utf-8",newline="") as stream:
            writer = csv.DictWriter(stream,fieldnames=LOG_COLUMNS)
            if not exists:
                writer.writeheader()
            row = {k:result.get(k,"") for k in LOG_COLUMNS}
            row.update(input=input_name,records=len(result["records"]),error="; ".join(result["errors"]),
                       agents="+".join(result.get("agents",[])),handoffs=" | ".join(result.get("handoffs",[])))
            writer.writerow(row)
    return result
