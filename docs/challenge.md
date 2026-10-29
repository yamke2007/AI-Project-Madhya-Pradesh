# Technical challenge, choices and measured tool tests

## Actual sources and stages

The TA shortlist prioritizes e-Vikas, DES APY, IMD advisories, ICAR KVK and conditional e-Uparjan. Inspection found only inventories/documentation in the initial repo, no crop corpus or runnable agents. Six source snapshots were collected with TLS verification. Direct ICAR directory and Hindi MSP scheme tables are operational; the historical Economic Survey supports a narrow sentence extractor and a transparently manual transcription import. Fertilizer/production/advisory portal forms are not numerical result datasets. No support for all six crops or all stages is inferred from a source listing.

## Challenges and design trade-offs

Dynamic pages contain unrendered {{...}} tokens. Treating them as recommendations would fabricate facts; the router rejects them. DES APY's query form is saved but automated filter/result retrieval is pending. IMD advisory filtering, e-Uparjan quantitative data, scanned/Hindi PDF OCR and model reasoning remain implementation gaps, not proven research impossibilities. The e-Mandi PDF is a workflow manual, not market-price data.

HTML tables preserve source rows more reliably for this narrow task than free-form model generation. The chosen sequential routing is inspectable on modest CPU hardware and supports unseen values within declared layouts. It lacks adaptable layout reasoning and cooperative agents. General PDF text extraction is not table extraction; the conservative sentence grammar omits unsupported facts explicitly. CSV imports preserve manual transcription provenance and never masquerade as automated PDF extraction. Missing dimensions are explicit; source spelling errors remain visible rather than guessing canonical locations.

## Literature and open-source alternatives

[pypdf extraction documentation](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) describes text-layer extraction and the need for OCR for image-only pages. This supports using pypdf for searchable PDFs, not claiming scanned-table support. [pdfplumber project documentation](https://github.com/jsvine/pdfplumber) offers character/layout inspection and configurable table extraction. We actually tested its text extraction; table reconstruction and OCR accuracy are not measured here. BeautifulSoup handles selected HTML tables; it cannot render JavaScript or validate agricultural meaning.

[LoRA, Hu et al.](https://arxiv.org/abs/2106.09685) freezes base weights and trains low-rank parameter updates. [QLoRA, Dettmers et al.](https://arxiv.org/abs/2305.14314) combines quantized base weights with adapter training. These are published approaches. The project now has a separate training set (72 real Agmarknet examples, 2008-2010, 0 hash overlap with evaluation) and a Colab QLoRA script for Qwen2.5-1.5B-Instruct, but no training result is claimed until that run is done. The machine has approximately 16 GiB RAM and 16 logical CPUs; torch/transformers were absent in the inspected system Python. Dedicated accelerator suitability was not established. Optional local inference/scoring code is provided, but no actual base/adapter run is claimed.

A calibrated LLM judge could evaluate semantic groundedness but needs independently human-labelled calibration (at least ten, agreement >=80%). This project has no such human panel or judge. Deterministic field and exact-trajectory comparisons are used only where semantics are explicit; M10 is unavailable. Update: M8 now uses AgentEvals trajectory match and M10 uses a deterministic groundedness check (no LLM judge); LangSmith tracing is available as an option.

## Tools actually executed

Command for every row: `python scripts/benchmark_tools.py`. Original numeric evidence: evidence/tool_benchmarks.csv. Each tool was run on both real downloaded project PDFs with default text extraction; full file, all pages, no OCR. Timings are one-run measurements and not comparative benchmarks across hardware.

| Tool/version | Source | Pages | Text pages | Characters | Seconds | Status |
|---|---|---:|---:|---:|---:|---|
| pypdf 6.12.1 | data/raw/mp_economic_survey.pdf | 20 | 17 | 22368 | 0.969 | executed |
| pdfplumber 0.11.9 | data/raw/mp_economic_survey.pdf | 20 | 17 | 21834 | 3.806 | executed |
| pypdf 6.12.1 | data/raw/e_mandi_manual.pdf | 35 | 35 | 11900 | 1.055 | executed |
| pdfplumber 0.11.9 | data/raw/e_mandi_manual.pdf | 35 | 35 | 10287 | 3.364 | executed |

These are real execution/coverage counts, not reference-labelled accuracy. Neither tool's character count proves correct Hindi encoding or table structure. pypdf was selected for the narrow production parser; pdfplumber remains a tested alternative rather than an installed-but-unused success claim. Numeric field F1 is reported separately on transparently source-derived CSV/HTML fragments.

## Measured: Hindi text layer vs OCR on a real source (added 25 Oct)

Command: `python scripts/benchmark_hindi_ocr.py`; evidence: `evidence/hindi_ocr_benchmark.csv`. Source: `data/raw/e_mandi_manual.pdf` (S04, MP Mandi Board, Hindi, 35 pages). Every page prints the footer "म.प्र. राज्य कृषि विपणन (मंडी) बोर्ड" (checked by viewing rendered pages). A page counts as correct when both key words "विपणन" and "बोर्ड" come out correctly spelled.

| Tool | Pages correct (both words) | "विपणन" found | "बोर्ड" found | Seconds |
|---|---:|---:|---:|---:|
| pypdf text layer | 0 / 35 | 0 | 0 | 0.9 |
| pdfplumber text layer | 0 / 35 | 0 | 0 | 2.1 |
| Tesseract 5 `eng` (footer strip, 300 dpi) | 0 / 35 | 0 | 0 | 11.7 |
| Tesseract 5 `hin` (footer strip, 300 dpi) | 26 / 35 | 34 | 26 | 13.9 |

What this shows: the PDF's text layer is present on every page but decodes to wrong Devanagari (e.g. "षवपणन", "बोड ड"), a legacy-font / character-mapping problem. Text-layer tools therefore look successful by character count while returning wrong Hindi. Tesseract's Hindi model recovers the words on most pages; the remaining errors are mostly the conjunct "र्ड" in "बोर्ड".

Research vs implementation: correct decoding of legacy Hindi fonts is a known open problem for PDF text extraction (the font has no reliable Unicode mapping), so this is a limitation of the source and tools, not of our code. Our implementation response: the tables agent re-reads Hindi pages with OCR when their text layer yields no usable values. Not yet done: automatic detection of a corrupted Hindi text layer on pages that do yield tables, and a dedicated Indic OCR model (e.g. Surya) for comparison.

Also implemented: a general table agent (pdfplumber tables, Tesseract word-box table rebuilding for English and Hindi, openpyxl, HTML) tested on synthetic fixtures, including a scanned Hindi price table where Hindi district and crop names normalize to the declared English forms. These fixture tests show the code works; they are not accuracy on real sources.

## Acquisition and provenance limitations

The inventory ICAR URL at icar.gov.in failed with an expired certificate; the official icar.org.in/en/node/15044 alternative returned HTTP 200 without bypassing verification. CM Helpline, e-Mandi manual, Economic Survey, e-Vikas and DES APY returned HTTP 200 in actual command output. The manifest records local collection date 25 October 2026 and unknown/unverified licenses; no guessed license or publication date is assigned. No historical acquisition timestamp/log was fabricated. The reproducible fetch script records only future attempts it actually executes.

The source PDFs/HTML are stored with hashes; survey page 7 was rendered and inspected against manual numerical references. Scheme and directory fields were checked against their original source tables. The 30 units share parent documents and were visible in development; no independent held-out generalization or instructor surprise success is asserted.
