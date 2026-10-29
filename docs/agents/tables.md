# Agent card: tables (general table specialist)

Status: implemented; evaluated on **22 cases built from real Agmarknet mandi price records** (official DMI data, via the public GitHub archive iancovert/Agmarknet): 12 development cases (used while building; they exposed one bug, see below) and 10 held-out cases generated afterwards from crop-years never used and scored once. References were written by `scripts/prepare_table_cases.py` from the raw source lines without calling the pipeline; **a team member still has to check them** (`checked` field) before the protocol counts them.

| Split | Cases | Fields | Pooled F1 |
| --- | ---: | ---: | ---: |
| development (tables_01-12) | 12 | 192 | 1.0 after the fix (0.0 before) |
| held-out (tables_13-22) | 10 | 160 | 1.0 (first run) |

What this does and does not show: real column layouts, number formats ("1,391.60"), dates ("05 Apr 2012"), MP-only filtering and district spellings (Badwani, Umariya, Anupur) are handled. All 22 cases are the same format (English CSV); PDF tables, scanned pages and Hindi tables still have no real-source cases, so no score is claimed for those modes.

Bug found by the real cases: the crop is given only in the file name (Agmarknet files have no crop column). Words in the name were split on `\w`, so "agmarknet_soyabean_2012" stayed one token and the crop was missed (F1 0.0 on all 12 development cases). Fixed by splitting on letters only (tables.py, caption_context).

Inventory sources it is meant for: S03 / S18 / S19 (mandi price tables), S11 / S12 (DES exports), S13 (Agricultural Statistics tables), S23 (survey tables, together with statistics). Statuses in docs/source_agent_map.csv stay pending until real files from those sources pass checked cases.

## Responsibility and input
Turn tables into observation-v1 records when no narrow specialist applies: digital PDF tables, scanned PDF pages and images (OCR, English + Hindi), Excel workbooks, HTML tables and CSV files with arbitrary headers. This is where instructor surprise items (mandi price PDF, district crop report, scanned Hindi table) are routed.

## Tools
| Tool | Used for |
| --- | --- |
| pdfplumber (`pdfplumber.pages`, `pdfplumber.extract_tables`) | page text, ruled and text-aligned tables |
| Tesseract via pytesseract (`tesseract.ocr_tables`) | scanned pages, images and Hindi pages with a broken text layer; word boxes rebuilt into rows/cells |
| openpyxl (`openpyxl.read`) | .xlsx sheets |
| BeautifulSoup (`beautifulsoup4.tables`) | HTML tables |
| csv (`csv.reader`) | CSV with any headers |
| local LLM via Ollama (`llm.header_mapping`, optional) | headers the keyword rules cannot classify |

## Decisions: fixed code vs model
| Decision | Made by |
| --- | --- |
| Digital vs scanned page (text layer > 50 chars) | code |
| Re-read a Hindi page with OCR when its text layer gives no usable values | code (motivated by evidence/hindi_ocr_benchmark.csv: 0/35 text-layer pages decode correctly) |
| OCR language (`eng+hin` when installed) | code |
| Header row (keyword score) and two-line headers | code |
| Column meaning for English/Hindi keywords (district, जिला, फसल, न्यूनतम, उत्पादन...) | code |
| Column meaning for unknown headers | **model** (local Ollama); if the model is not running, the column is ignored and a note is logged; nothing is guessed |
| Units from header/caption, price default INR/quintal when a date or mandi is present | code |
| Skip total rows, keep only Madhya Pradesh rows, drop numbers with no crop and no place | code |

## Provenance
Locators: `page:P/table:T/row:R/col:C`, `page:P/ocr/row:R/col:C`, `image/ocr/row:R/col:C`, `sheet:S/row:R/col:C`, `table:T/row:R/col:C`, `csv/row:R/col:C`. Evidence is the source row text; `column_mapped_by` says whether a rule or the model decided the column.

## Failure handling
Raises "no table values it could map" so the supervisor can hand off or fail the run honestly; a PDF over the page limit stops the whole run. Values missing crop, place, period or unit are kept as explicit MISSING and make the run partial.

## Known limits
- Column splitting in OCR uses word gaps; tightly spaced columns can merge.
- Multi-level merged headers in large reports may need the model.
- Wide tables with years as columns are supported; crops as columns are not yet.
- No real-source checked cases yet, so no per-agent F1 is claimed for this agent.
