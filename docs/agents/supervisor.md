# Agent card: supervisor (router and orchestration)

Implemented in `agriagent/orchestrator.py` with LangGraph (falls back to the same logic in plain Python if LangGraph is missing; the run output field `orchestrator` says which ran).

| Step | Rule |
| --- | --- |
| Plan | Fixed rules on file type and content: KVK HTML -> directory, Hindi scheme HTML -> scheme, six-column statistics CSV -> statistics, PDF -> statistics then tables, other CSV / XLSX / images / HTML tables -> tables, unrendered templates and unsupported types -> fail |
| Run | Each specialist runs with every tool call recorded in `trajectory` (tool, arguments) and `agent_trace` (agent, ok, summary, seconds) |
| Retry | A transient tool failure (`ToolFault`) is retried up to 2 times on the same agent |
| Hand-off | "No data / unsupported" from one specialist hands the input to the next agent in the plan and is recorded in `handoffs` |
| Stop | A safety limit (PDF page limit) stops the run |
| Complete | The plan is exhausted or stopped; pipeline.process then sets complete / partial / failed |

Why a router and not an LLM planner: our input types are unambiguous (PDF, image, spreadsheet, HTML) and each needs a known tool chain, so rules are cheaper, reproducible and never mis-route a known type. A fixed sequential chain of every extractor would waste calls (M13) on inputs that only one specialist can read. The model is used only where rules cannot decide (unknown table headers).

Fault injection for the demo: `python run.py --input <pdf> --inject-tool-fault pdfplumber.extract_tables --trace` (fails once, retried, run completes). The original `--fault extract|database` failures are kept and still fail the run.
