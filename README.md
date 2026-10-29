# AgriAgent Madhya Pradesh: Phase 2 review package

Runnable multi-agent extraction (LangGraph supervisor, four specialists including a general PDF/OCR/Excel table agent) with source evidence, normalization, validation, SQLite storage and reproducible local evaluation. **Phase 2 is partial; the live/model gates are not passed.** Four specialists are implemented: KVK directory HTML, Hindi scheme HTML, structured statistics CSV with a narrow production-sentence PDF grammar, and a general table agent (PDF tables, OCR English + Hindi, Excel, HTML, any CSV). The table agent has 22 source-derived Agmarknet CSV cases (12 development and 10 held-out); the held-out references still require independent teammate verification. The original 23-source Phase 1 inventory and TA work are preserved; the original README is in `docs/Phase1/README_original.md`.

## Quick start (Python 3.10+)

From this directory, install pinned packages and process an actual included source:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe run.py --input data/raw/icar_kvk.html
```

On Linux/macOS use `.venv/bin/python` instead. With dependencies installed in the current interpreter, the one-command entry point is:

```powershell
python run.py --input data/raw/icar_kvk.html
```

The directory snapshot produces 162 observations from 54 source rows. Every run prints a UUID/status/count and saves full records/evidence/trajectory in `output/<run_id>.json`, inserts observations into SQLite and appends one input-attempt row to `logs/automation_log.csv`. Repeated ingestion rejects natural-key duplicates and records rejection counts. Logs are sequential CSV, so use separate configs for concurrent processes. Existing acquisition/evaluation history is bundled as evidence; future runs append history.

## Supported workflow (supervisor + specialists, LangGraph)

```mermaid
flowchart TD
  A[run.py --input file(s) or folder] --> B[Size, type and content checks]
  B --> P[Supervisor plan: fixed rules]
  P --> D[directory: KVK HTML]
  P --> E[scheme: Hindi scheme HTML]
  P --> F[statistics: 6-column CSV / PDF sentences]
  P --> T[tables: PDF tables, OCR eng+hin, XLSX, HTML, any CSV]
  F -- PDF: no sentences = hand-off --> T
  D & E & F & T -- transient tool fault --> R[retry same agent, max 2]
  R --> P
  T -. unknown header .-> M[local LLM via Ollama, optional]
  D & E & F & T --> G[Normalize with declared rules]
  G --> H[Validate; attach hash, locator, evidence, agent]
  H --> I[Transactional SQLite with duplicate rejection]
  I --> J[JSON result, trajectory, agent trace, automation log]
  P -- unsupported / template / page limit --> K[Explicit failed result]
  K --> J
```

The supervisor (`agriagent/orchestrator.py`) plans one or more specialists per input with fixed rules, retries transient tool faults, records hand-offs between agents and decides when the plan is complete. For PDFs the statistics sentence grammar and the general table agent cooperate. The only model decision is optional: a local LLM (Ollama, no paid API) maps table headers the keyword rules cannot classify; if it is not running, those columns are skipped and noted, never guessed. No evaluation case ID or expected value drives extraction. See `docs/agents/supervisor.md` and `docs/agents/tables.md`.

Extra setup for OCR and the optional model (macOS): `brew install tesseract tesseract-lang` and, optionally, `brew install ollama && ollama serve & ollama pull qwen2.5:3b`. Optional tracing: `export LANGSMITH_TRACING=true LANGSMITH_API_KEY=<key>`.

New commands:

```powershell
python run.py --input C:/demo/ --trace                                   # every file in a folder, with agent/tool trace
python run.py --input data/raw/mp_economic_survey.pdf --trace            # statistics + tables hand-off
python run.py --input tests/fixtures_tables/synthetic_district_apy.pdf --inject-tool-fault pdfplumber.extract_tables --trace
python scripts/benchmark_hindi_ocr.py                                    # real Hindi text-layer vs OCR test
```

| Input | Operational scope | Limits |
|---|---|---|
| UTF-8 KVK HTML | Four columns: serial, address, host, sanction year; retains source row evidence | District extraction expects `Distt.`; source errors retained; current status/LGD unverified |
| UTF-8 Hindi scheme HTML | Two-cell label/value table with scheme/department context | Generic labels preserved in Hindi; no inference of crop/geography/effective date; blank values invalid |
| UTF-8 CSV | Headers `crop,location,period,variable,value,unit`; optional value_kind, origin_source, origin_locator, qualifier, lgd_code | Structured importer, not proof of DES portal retrieval |
| PDF | Explicit English production sentences plus bounded PDF-table/OCR hand-off | Partial coverage; at most 10 digital table pages, 2 scanned OCR pages and 3 legacy-text OCR pages per run; not arbitrary full-document extraction |

Useful real-source commands (partial returns exit code 2, failed returns 1):

```powershell
python run.py --input data/raw/msp_scheme.html
python run.py --input data/raw/mp_economic_survey.pdf
python run.py --input data/derived/survey_agriculture_transcription.csv
python run.py --input data/raw/evikas_calculator.html
python run.py --input data/raw/icar_kvk.html --fault extract
python scripts/db_cli.py --id 1
```

The scheme snapshot has 23 rows, some empty, so its run is partial. The survey PDF grammar extracts one wheat observation and explicitly warns of omitted facts. The ten-fact survey CSV was manually transcribed from page 7 and preserves lower bounds/targets; it must not be described as automatic PDF extraction. The e-Vikas template is deliberately rejected; fetching a template is not fetching fertilizer results. DES query HTML and the manual remain supporting/pending sources.

## Tests, evaluation and models

```powershell
python -m unittest discover -v
python eval/run_eval.py
python eval/compare_adapters.py
python scripts/benchmark_tools.py
python scripts/audit_project.py
```

See `evidence/test_report.json` and `evidence/clean_extraction_report.json` for executed commands/results, `evidence/tool_benchmarks.csv` for two actual PDF-tool runs, and `docs/phase2_implementation_status.md` for the final checklist. Initial repository contained no runnable tests; the current suite tests extraction, matching thresholds/units, faults, schema, duplicate detection, restore, corpus hashes, Phase 1 preservation and model-unavailable behavior.

`eval/cases/` and `eval/reference/` contain 30 source-verified fragments, ten per specialist, with a separate Hindi slice. They derive from three development-visible snapshots and include manually transcribed statistics; high local F1 is an importer/regression result, **not an independent held-out document or surprise gate result**. Source verification was performed by the implementing agent, not an independently labelled human panel. See `eval/README.md` for rules, denominators, contamination limitations and metric semantics before presenting results.

All M1–M18 IDs are represented, with unavailable values blank. M1–M4 and M6–M16 have local measurements (M8 via AgentEvals, M10 deterministic groundedness, M11 over eight workflow cases including a transient fault and retry); M4 is a local locator proxy. M5/M17 await the instructor and M18 stays blocked until genuine base and adapter predictions are produced; training examples and a Colab recipe exist (72 Agmarknet 2008–2010 examples, 0 exact-hash overlaps, no semantic/pretraining guarantee). The official separate metrics CSV attachment was not supplied: the current header is provisional, not certified as the exact required format.

The optional model runner and identical-case comparison workflow are documented in `eval/README.md`. No training or actual model/adapter inference occurred. Missing weights/dependencies produce blocked statuses; there are no fabricated scores. A separately collected training set, compatible base/PEFT weights, suitable compute and an independently checked evaluation set remain necessary.

## Configuration, provenance and troubleshooting

`config.json` controls database/output/log paths (relative to project root or absolute), byte/page limits and an optional authoritative LGD code/name JSON registry (build it from the official CSV with `scripts/import_lgd.py`). Use `--config <json>`, `--source-url <url>` and `--manual-interventions N` as needed; record runtime configuration changes during the demo as manual interventions. Paths do not depend on the current shell directory once the script is located.

Crop synonyms, unit conversions and period normalization are in `agriagent/normalization.py` and declared in `eval/README.md`. Unknown and inapplicable dimensions use explicit missing codes. Integer/code/decimal matching follows the protocol; incompatible units fail. No district code is inferred without a registry. Non-English labels are retained instead of silently translated. `data/manifest.csv` covers all raw/derived/evaluation corpus inputs with hashes, official URL, local collection date, language, lineage and explicit unverified licenses. Source snapshots are historical evidence, not current agricultural advice.

Database DDL, dictionary and portable dump are in `db/`. `scripts/db_cli.py` retrieves source hash/URL/input/locator for trace-back; historical absolute paths can be remapped using the manifest hash. `docs/agents/` contains operational and pending cards, and `docs/challenge.md` separates tool/literature capabilities from implemented behavior. The protocol PDF is preserved under `docs/evaluation_protocol.pdf`.

If imports fail, install `requirements.txt` with the same Python interpreter. If a portal snapshot is rejected, export actual results in the declared schema; do not replace placeholders with invented figures. A PDF with no supported sentence fails explicitly. An invalid row is retained with its validation errors; inspect output JSON. Database errors fail the run and retain output/log evidence; retry after correcting the config. Transient tool faults are retried up to the supervisor limit; deliberate extraction/database failures are logged and are not silently retried. Never bypass TLS verification to refresh source snapshots: the inventory ICAR hostname had an expired certificate, while official `icar.org.in` worked. `scripts/fetch_sources.py` preserves existing files by default and records genuine retrieval attempts.

For the timed session use `docs/demo_guide.md`. The protocol deadline predates this work and no submission tag, commit or push was created. For safe review/integration without overwriting unrelated work, use `docs/git_review_and_merge.md`. The exact requested archive filename is used for delivery despite the explicitly partial status; its name is not a claim that all evaluation gates passed.
