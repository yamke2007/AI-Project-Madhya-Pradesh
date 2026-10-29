"""Challenge benchmark on a real Hindi source: text layer vs OCR.

Source: data/raw/e_mandi_manual.pdf (S04, MP Mandi Board, Hindi). Every page
carries the printed footer "म.प्र. राज्य कृषि विपणन (मंडी) बोर्ड" (checked by
viewing the rendered pages). We measure, per tool, on how many pages the
footer comes out spelled correctly, using two key words:
  "विपणन" (marketing)  and  "बोर्ड" (board)
Tools: pypdf text layer, pdfplumber text layer, Tesseract eng and Tesseract
hin on the rendered footer strip (bottom 9% of the page at 300 dpi).

    python scripts/benchmark_hindi_ocr.py   -> evidence/hindi_ocr_benchmark.csv
Needs Tesseract with the Hindi model (macOS: brew install tesseract tesseract-lang).
"""
import csv
import importlib.metadata
import json
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data/raw/e_mandi_manual.pdf"
WORDS = ["विपणन", "बोर्ड"]


def norm(s):
    return unicodedata.normalize("NFC", s or "")


def score(texts):
    pages = len(texts)
    both = sum(all(w in norm(t) for w in WORDS) for t in texts)
    per_word = {w: sum(w in norm(t) for t in texts) for w in WORDS}
    return pages, both, per_word


def main():
    import pdfplumber
    import pytesseract
    from pypdf import PdfReader
    rows = []
    t0 = time.perf_counter()
    layer_pypdf = [p.extract_text() or "" for p in PdfReader(PDF).pages]
    rows.append(("pypdf text layer", importlib.metadata.version("pypdf"), layer_pypdf, time.perf_counter() - t0))
    with pdfplumber.open(PDF) as pdf:
        t0 = time.perf_counter()
        layer_plumber = [p.extract_text() or "" for p in pdf.pages]
        rows.append(("pdfplumber text layer", importlib.metadata.version("pdfplumber"), layer_plumber,
                     time.perf_counter() - t0))
        strips = []
        for p in pdf.pages:
            img = p.to_image(resolution=300).original
            w, h = img.size
            strips.append(img.crop((0, int(h * 0.91), w, h)))
    have = set(pytesseract.get_languages(config=""))
    for lang in ("eng", "hin"):
        if lang not in have:
            rows.append((f"tesseract {lang}", "not installed", None, 0))
            continue
        t0 = time.perf_counter()
        texts = [pytesseract.image_to_string(s, lang=lang, config="--psm 6") for s in strips]
        rows.append((f"tesseract {lang} (footer strip)", pytesseract.get_tesseract_version().public, texts,
                     time.perf_counter() - t0))
    out = []
    for name, version, texts, secs in rows:
        if texts is None:
            out.append(dict(tool=name, version=version, input="data/raw/e_mandi_manual.pdf", pages="", correct_pages="",
                            share="", vipanan_pages="", board_pages="", seconds="", status="not_run"))
            continue
        pages, both, per = score(texts)
        out.append(dict(tool=name, version=version, input="data/raw/e_mandi_manual.pdf", pages=pages,
                        correct_pages=both, share=round(both / pages, 3), vipanan_pages=per["विपणन"],
                        board_pages=per["बोर्ड"], seconds=round(secs, 2), status="executed"))
    with (ROOT / "evidence/hindi_ocr_benchmark.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print("example text layer:", norm(layer_plumber[3])[-60:].replace("\n", " "))


if __name__ == "__main__":
    main()
