# Live demonstration (15–20 minutes)

> **Current implementation note (27 Oct):** the supervisor routes by fixed rules; PDFs can hand off from statistics to tables, and transient tool faults are retried. Demonstrate the workflow with `python run.py --input data/raw/mp_economic_survey.pdf --trace` and a retry with `python run.py --input tests/fixtures_tables/synthetic_district_apy.pdf --inject-tool-fault pdfplumber.extract_tables --trace`. PDF table/OCR coverage is deliberately bounded: up to 10 digital pages, 2 scanned pages and 3 legacy-text OCR pages per run; this is not full-document coverage.

This is a partial Phase 2 implementation, not a gate-passed submission. The protocol's table has malformed/inconsistent block times; the sequence below preserves its order and totals 18 minutes. Agree timing with the evaluator. The protocol says the TA freezes the last pre-deadline commit at `phase2-submission` (22 October, 23:59); this work is prepared on 25 October 2026 and no on-time tag or member commit history is claimed. No commit, tag or push was made by this implementation session.

Before the session, obtain the TA's actual metrics CSV header, independently checked unseen documents, a base model/adapter with separate training data, and an LGD registry. Confirm any overdue-submission handling. If a required item remains unavailable, show the blocked status. Test dependencies in advance; do not install or edit code during surprise processing.

## 0–2: start surprise inputs immediately

Use a clean review checkout approved by the TA. Once a legitimate tag exists, the normal command is `git switch --detach phase2-submission`; do not manufacture that tag to suggest earlier completion. The ZIP itself contains no Git internals and cannot establish a revision/tag.

From the project root:

```powershell
python run.py --input C:/demo/unseen1.html
python run.py --input C:/demo/unseen_hindi.html
python run.py --input C:/demo/unseen3.csv
```

Use the instructor's actual file names/types. Run in separate terminals if desired, using separate database/log paths via pre-prepared config files to avoid concurrent CSV writers. The logger is designed for sequential runs. Input HTML must be a KVK-style directory or Hindi two-column scheme table; CSV needs the declared headers. Text PDF support is deliberately narrow and partial. Do not imply arbitrary scanned or audio inputs work. Attempt unsupported instructor files too: a failed attempt is logged and earns no invented extraction credit. Config changes during a live run must be counted using `--manual-interventions 1`; no source edits.

Expected terminal shape is JSON with run_id/agent/status/errors/warnings/latency followed by records count. Full trace/output is `output/<run_id>.json`; exit 0 complete, 2 partial, 1 failed. The instructor supplies a key with 10–15 fields per surprise item; M5 remains blank until all three actual items are checked. Regular benchmark outputs must not be relabelled as surprise results.

## 2–5: mapping, scope and challenge

Open `docs/source_agent_map.csv`: 23 rows match original inventory, three partial and twenty pending. Explain S21 (direct KVK table) and S06 (Hindi descriptive MSP scheme) as two concrete selections; contrast S02's unrendered calculator template and S11's query form with usable data. Preserve TA's six proposed crops; do not claim all sources cover them. Show `docs/challenge.md` and `evidence/tool_benchmarks.csv`. Character counts measure execution/coverage, not correctness.

## 5–8: specialists

Show the existing real directory run or execute `python run.py --input data/raw/icar_kvk.html`: 162 long-form observations from 54 directory rows. Trace table 1, row 3 for Datia's sanction year 2007, address and host. Demonstrate directory→header detection→BeautifulSoup call→source row→normalized observations. Source spellings are retained; LGD/freshness unverified.

Execute `python run.py --input data/raw/msp_scheme.html`: 23 policy rows, partial because source cells are blank. Show Hindi labels/value evidence, missing crop/location/period codes and the empty-fee/other-field distinctions. This is descriptive policy, not operational procurement statistics.

Execute `python run.py --input data/derived/survey_agriculture_transcription.csv`: ten imported observations. Explain manual PDF page-7 transcription, lower-bound and target variables, and source evidence. Execute `python run.py --input data/raw/mp_economic_survey.pdf` separately: one explicit wheat production observation; partial PDF grammar. Do not present manual transcription as automatic PDF extraction. All routing, extraction, validation and tool decisions are fixed code; no inference model is active.

## 8–10: orchestration, hard case and fault injection

Show the README flow and `output/<run_id>.json` trajectory. It is a router plus one specialist, not cooperative model agents. `M11` cannot claim multi-agent workflow success.

```powershell
python run.py --input data/raw/evikas_calculator.html
python run.py --input data/raw/icar_kvk.html --fault extract
python run.py --input data/raw/icar_kvk.html
```

The template command rejects placeholders. `--fault extract` records a deliberate failure without fabricated rows; a separate fresh run can then recover. For a transient tool fault, use `--inject-tool-fault pdfplumber.extract_tables`; the supervisor retries the failing tool up to its configured retry limit. Failures remain in the automation log and M12 denominator. Database failure can be demonstrated with `--fault database`; it must yield failed status and retain the run output.

## 10–14: evaluation and adapter evidence

```powershell
python eval/run_eval.py
python eval/compare_adapters.py
```

Open `eval/results.json` and `eval/phase2_metrics.csv`, show per-agent, group and Hindi slices and macro_agents. The bundled benchmark has 30 fragment cases, ten per specialist, with shared/development-visible parent sources. Its high F1 is a regression/import result, not evidence of independent document generalization. Show input/reference separation, source locators, SHA-256 hashes and `eval/contamination_report.json`. No training files exist; empty-set zero overlap is not proof about pretrained data. Invite the evaluator to check source values directly. M4 is a local-locator proxy, M10 unavailable, and the official CSV template is still needed.

Show base/adapter blocked rows with blank scores, explain actual missing weights/training evidence. Only use the optional commands in `eval/README.md` if compatible weights were genuinely run beforehand and metadata/failures are available. M18 can be negative; no adapter was trained here. Review the three surprise results now; do not insert scores without the instructor key.

## 14–17: automation and database

```powershell
python scripts/db_cli.py --id 1
python scripts/db_cli.py
python scripts/db_cli.py --dump
```

Open the source file selected by hash in `data/manifest.csv`, then the exact table/row or physical page/CSV line in the record. Let the evaluator select three random database rows for M17; don't substitute hand-picked traces. Show `db/schema.sql`, `db/dictionary.md`, rejected duplicates in attempts and validation errors on incomplete scheme rows. Show `logs/automation_log.csv`; one row per genuine input attempt, including evaluation and failures. Test-suite temporary attempts are isolated. Repeated evaluation appends history and changes M12's accumulated denominator legitimately.

## 17–18: individual viva and limitations

Each real team member explains their assigned code and evidence. Phase 1 role names are preserved; this session does not fabricate their implementation commits or attribute generated code to them. State remaining gates and use `docs/phase2_implementation_status.md`.

Recovery: install pinned requirements for missing import errors; use UTF-8 HTML/CSV; export actual dynamic results instead of submitting portal templates; verify paths; inspect exit codes and per-run errors. Keep the original input intact. Unsupported layouts/modalities remain failed/partial until implemented and evaluated. No recorded run of these exact surprise items is supplied; the protocol's half-credit fallback is only available if a real recording exists.
