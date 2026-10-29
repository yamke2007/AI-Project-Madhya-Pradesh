"""Build the LoRA training set (M18) from real Agmarknet records that the
evaluation never uses.

Training years: 2008, 2009, 2010 (soybean, wheat, maize). Evaluation cases use
2011-2017 only, so there is no shared file, date or row. Each training input is
built exactly like an evaluation case (Agmarknet header + 4 unmodified source
lines for Madhya Pradesh markets on one date), and its target is copied from
the source cells by plain string handling (no pipeline, no model).

Outputs
  data/train/raw/train_XXX_agmarknet_<crop>_<year>.csv   (hashed by eval/contamination.py)
  data/train/examples.jsonl  {"source","sha256","prompt","target","checked","check_method"}
The prompt is identical to eval/infer_adapter.py, so base and adapter are
compared on the same task format.

    python scripts/build_agmarknet_training.py
"""
import csv
import hashlib
import io
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_table_cases import CROP, HEADER, iso, num, parent  # noqa: E402
from build_training_set import prompt_for  # noqa: E402

YEARS = [2008, 2009, 2010]
PER_CROP_YEAR = 8


def main():
    raw_dir = ROOT / "data/train/raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    eval_dates = set()
    for c in json.loads((ROOT / "eval/case_index.json").read_text(encoding="utf-8")):
        if c["agent"] == "tables":
            eval_dates.add(c["source_locator"])
    out, k = [], 0
    for crop in CROP:
        for year in YEARS:
            src = parent(crop, year)
            by_date = defaultdict(dict)
            for line in src.read_text(encoding="utf-8").splitlines():
                row = next(csv.reader([line]))
                if len(row) == 10 and row[0] == "Madhya Pradesh" and all(row[6:9]):
                    by_date[row[9]].setdefault(row[1], line)
            dates = sorted(d for d, v in by_date.items() if len(v) >= 4)
            rng = random.Random(f"train-{crop}-{year}")
            for date in rng.sample(dates, min(PER_CROP_YEAR, len(dates))):
                k += 1
                districts = sorted(by_date[date])
                start = rng.randrange(0, len(districts) - 3)
                lines = [by_date[date][d] for d in districts[start:start + 4]]
                buf = io.StringIO()
                csv.writer(buf, lineterminator="\n").writerow(HEADER)
                content = buf.getvalue() + "\n".join(lines) + "\n"
                name = f"train_{k:03d}_agmarknet_{crop.lower()}_{year}.csv"
                (raw_dir / name).write_text(content, encoding="utf-8")
                target = []
                for line in lines:
                    r = next(csv.reader([line]))
                    common = dict(crop=CROP[crop], location=r[1].strip().casefold(), period=iso(r[9]))
                    target.append(dict(common, variable="arrivals", value=num(r[5]), unit="tonne",
                                       value_kind="decimal" if "." in r[5] else "integer"))
                    for var, cell in (("min_price", r[6]), ("max_price", r[7]), ("modal_price", r[8])):
                        target.append(dict(common, variable=var, value=num(cell), unit="INR/quintal",
                                           value_kind="decimal" if "." in cell else "integer"))
                out.append(dict(source=f"data/train/raw/{name}", sha256=hashlib.sha256(content.encode()).hexdigest(),
                                parent=f"{crop}/{year}.csv", prompt=prompt_for(content, name), target=target, checked=True,
                                check_method="deterministic copy of source cells by script (no model); spot-check 5 before training"))
    with (ROOT / "data/train/examples.jsonl").open("w", encoding="utf-8") as f:
        for e in out:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"{len(out)} training examples from Agmarknet {YEARS} (evaluation uses 2011-2017)")


if __name__ == "__main__":
    main()
