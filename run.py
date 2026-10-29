import argparse
import json
from pathlib import Path
from agriagent.pipeline import process

SUPPORTED = {".csv", ".pdf", ".html", ".htm", ".xlsx", ".xlsm", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}

def expand(inputs):
    out = []
    for p in inputs:
        if p.is_dir():
            out += sorted(f for f in p.rglob("*") if f.is_file() and f.suffix.lower() in SUPPORTED)
        else:
            out.append(p)
    return out

def main():
    parser = argparse.ArgumentParser(description="Extract local agriculture sources with provenance")
    parser.add_argument("--input",required=True,type=Path,nargs="+",help="file(s) or folder(s); a folder runs every supported file")
    parser.add_argument("--config",type=Path)
    parser.add_argument("--source-url",default="unknown")
    parser.add_argument("--fault",choices=["extract","database"])
    parser.add_argument("--inject-tool-fault",default=None,help="tool name to fail once (supervisor retries), e.g. pdfplumber.extract_tables")
    parser.add_argument("--manual-interventions",type=int,default=0)
    parser.add_argument("--trace",action="store_true",help="print the agent/tool trace for each input")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8")) if args.config else {}
    codes = []
    for path in expand(args.input):
        result = process(path,config,args.source_url,fault=args.fault,manual_interventions=args.manual_interventions,
                         inject_tool=args.inject_tool_fault)
        print(json.dumps({k:result.get(k) for k in ("run_id","agent","status","errors","warnings","latency_seconds")},ensure_ascii=True))
        print("records="+str(len(result["records"])))
        if args.trace:
            print("  plan:",result.get("agents"),"engine:",result.get("orchestrator"),"retries:",result.get("retries"))
            for t in result.get("agent_trace",[]):
                print(f"  [{'ok ' if t['ok'] else 'ERR'}] {t['agent']:>10} -> {t['tool']:<28} {t['summary']}")
            for h in result.get("handoffs",[]):
                print("  hand-off:",h)
            for r in result["records"][:5]:
                print(f"    {r['variable']} = {r['value']} {r['unit']} | {r['crop']} | {r['location']} | {r['period']} @ {r['locator']}")
        codes.append(1 if result["status"]=="failed" else 2 if result["status"]=="partial" else 0)
    return max(codes) if codes else 1

if __name__ == "__main__":
    raise SystemExit(main())
