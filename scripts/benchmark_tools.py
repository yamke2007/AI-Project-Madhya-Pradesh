"""Run two open-source PDF tools on actual downloaded project PDFs."""
import csv
import importlib.metadata
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    from pypdf import PdfReader
    import pdfplumber
    rows=[]
    for name in ("mp_economic_survey.pdf","e_mandi_manual.pdf"):
        path=ROOT/"data/raw"/name
        for tool in ("pypdf","pdfplumber"):
            start=time.perf_counter()
            row=dict(tool=tool,version=importlib.metadata.version(tool),input="data/raw/"+name,
                     command="python scripts/benchmark_tools.py",pages=0,text_pages=0,characters=0,tables="not_measured",
                     seconds=0,status="failed",error="",quality_note="Character/page counts are not extraction accuracy")
            try:
                if tool=="pypdf":
                    pages=[p.extract_text() or "" for p in PdfReader(path).pages]
                else:
                    with pdfplumber.open(path) as pdf:
                        pages=[p.extract_text() or "" for p in pdf.pages]
                row.update(pages=len(pages),text_pages=sum(bool(p.strip()) for p in pages),characters=sum(len(p) for p in pages),status="executed")
            except Exception as exc:row["error"]=type(exc).__name__+": "+str(exc)
            row["seconds"]=time.perf_counter()-start
            rows.append(row)
    with (ROOT/"evidence/tool_benchmarks.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(json.dumps(rows,indent=2))

if __name__=="__main__":main()
