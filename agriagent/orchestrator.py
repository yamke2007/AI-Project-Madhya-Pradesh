"""Supervisor / router orchestration (LangGraph).

For each input the supervisor builds a plan of specialist agents, runs them in
order and decides after every step:

  plan --> run_agent --(ok)--------------------> next agent or finish
               |-----(tool fault, attempts<=2)--> run_agent (retry same agent)
               |-----(no data / unsupported)----> hand off to next agent in plan
               '-----(safety limit exceeded)----> stop, run fails

Plans (fixed rules on file type and content, no LLM):
  KVK directory HTML -> [directory]        Hindi scheme HTML -> [scheme]
  six-column statistics CSV -> [statistics] other CSV / XLSX / images -> [tables]
  other HTML tables -> [tables]            PDF -> [statistics, tables]
For PDFs the statistics agent's sentence grammar and the table agent's
table/OCR extraction cooperate: both run and their records are merged; if the
statistics grammar finds nothing, its failure is a hand-off, not a failure.

The workflow is complete when the plan is exhausted (or stopped); the run
status (complete / partial / failed) is then set by pipeline.process.
"""
import time

from . import extractors, tables

try:
    from langsmith import traceable
except Exception:  # optional
    def traceable(*_a, **_k):
        return lambda f: f

MAX_RETRIES = 2
TOOL = {"directory": "beautifulsoup4", "scheme": "beautifulsoup4"}


class ToolFault(RuntimeError):
    """Transient tool failure (used by fault injection); the supervisor retries."""


class Trace:
    def __init__(self, inject_tool=None):
        self.trajectory, self.agent_trace, self.notes = [], [], []
        self.inject_tool, self.retries, self.llm_calls = inject_tool, 0, 0

    def call(self, agent, tool, arguments, fn):
        entry = dict(tool=tool, arguments=arguments)
        self.trajectory.append(entry)
        t0 = time.perf_counter()
        rec = dict(agent=agent, tool=tool, ok=True, summary="")
        if tool.startswith("llm."):
            self.llm_calls += 1
        try:
            if self.inject_tool and self.inject_tool == tool:
                self.inject_tool = None  # fail once so the retry can succeed
                raise ToolFault(f"injected transient failure in {tool}")
            out = fn()
            rec["summary"] = f"{type(out).__name__}[{len(out)}]" if hasattr(out, "__len__") else type(out).__name__
            return out
        except Exception as exc:
            rec.update(ok=False, summary=f"{type(exc).__name__}: {exc}")
            raise
        finally:
            rec["seconds"] = round(time.perf_counter() - t0, 3)
            self.agent_trace.append(rec)

    def note(self, agent, msg):
        self.notes.append(f"{agent}: {msg}")


def plan(path):
    agent, _, group = extractors.detect(path)
    if path.suffix.lower() == ".pdf":
        return ["statistics", "tables"], group
    return [agent], group


def run_specialist(agent, path, cfg, trace, digest):
    if agent == "tables":
        records, warnings = tables.run(path, cfg, trace, digest)
    elif agent == "statistics":
        tool = "pypdf" if path.suffix.lower() == ".pdf" else "csv.DictReader"
        args = {"input_sha256": digest, "schema": "observation-v1",
                "max_pages": cfg["max_pdf_pages"] if tool == "pypdf" else None}
        records, warnings = trace.call(agent, tool, args, lambda: extractors.statistics(path, cfg["max_pdf_pages"]))
    else:
        args = {"input_sha256": digest, "schema": "observation-v1", "max_pages": None}
        records, warnings = trace.call(agent, TOOL[agent], args, lambda: getattr(extractors, agent)(path))
    for r in records:
        r["agent"] = agent
    return records, warnings


def _fatal(exc):
    return isinstance(exc, tables.LimitError) or "page limit" in str(exc).lower()


def _step(state, path, cfg, trace, digest):
    agent = state["plan"][state["idx"]]
    try:
        recs, warns = run_specialist(agent, path, cfg, trace, digest)
        state["records"] += recs
        state["warnings"] += warns
        state["producers"].append(agent)
        state["useful_calls"] += sum(1 for c in trace.agent_trace if c["agent"] == agent and c["ok"])
        state["outcome"] = "ok"
    except ToolFault as exc:
        state["outcome"] = "retry" if state["attempts"] < MAX_RETRIES else "handoff"
        state["errors"].append(f"{agent}: {exc}")
    except Exception as exc:
        if _fatal(exc):
            state["outcome"] = "stop"
            state["fatal"] = exc
        else:
            state["outcome"] = "handoff"
            state["handoffs"].append(f"{agent} -> {'next agent' if state['idx'] + 1 < len(state['plan']) else 'none'}: {exc}")
            state["errors"].append(f"{agent}: {exc}")
    return state


def _route(state):
    if state["outcome"] == "retry":
        return "retry"
    if state["outcome"] == "stop" or state["idx"] + 1 >= len(state["plan"]):
        return "finish"
    return "next"


@traceable(name="agriagent_supervisor")
def run(path, cfg, digest, inject_tool=None):
    """Returns dict(records, warnings, trajectory, agent_trace, producers, handoffs, retries, ...)."""
    trace = Trace(inject_tool)
    plan_agents, group = plan(path)
    state = dict(plan=plan_agents, idx=0, attempts=0, records=[], warnings=[], errors=[], handoffs=[],
                 producers=[], useful_calls=0, outcome=None, fatal=None)
    engine = "sequential"
    try:
        from langgraph.graph import END, START, StateGraph
        from typing import Any, TypedDict

        class S(TypedDict, total=False):
            s: Any

        def node_run(st):
            return {"s": _step(st["s"], path, cfg, trace, digest)}

        def node_retry(st):
            s = st["s"]
            s["attempts"] += 1
            trace.retries += 1
            return {"s": s}

        def node_next(st):
            s = st["s"]
            s["idx"] += 1
            s["attempts"] = 0
            return {"s": s}

        g = StateGraph(S)
        g.add_node("run_agent", node_run)
        g.add_node("retry", node_retry)
        g.add_node("next", node_next)
        g.add_edge(START, "run_agent")
        g.add_conditional_edges("run_agent", lambda st: _route(st["s"]),
                                {"retry": "retry", "next": "next", "finish": END})
        g.add_edge("retry", "run_agent")
        g.add_edge("next", "run_agent")
        state = g.compile().invoke({"s": state}, {"recursion_limit": 50})["s"]
        engine = "langgraph"
    except ImportError:
        while True:  # same logic without LangGraph installed
            state = _step(state, path, cfg, trace, digest)
            r = _route(state)
            if r == "retry":
                state["attempts"] += 1
                trace.retries += 1
            elif r == "next":
                state["idx"] += 1
                state["attempts"] = 0
            else:
                break
    details = dict(agents=plan_agents, handoffs=state["handoffs"], trajectory=trace.trajectory,
                   agent_trace=trace.agent_trace, retries=trace.retries, orchestrator=engine, source_type=group)
    if state["fatal"] is not None:
        state["fatal"].details = details
        raise state["fatal"]
    if not state["records"]:
        exc = extractors.ExtractionError("; ".join(state["errors"]) or "No records produced")
        exc.details = details
        raise exc
    return dict(records=state["records"], warnings=state["warnings"], trajectory=trace.trajectory,
                agent_trace=trace.agent_trace, notes=trace.notes, producers=state["producers"],
                plan=plan_agents, handoffs=state["handoffs"], retries=trace.retries, llm_calls=trace.llm_calls,
                useful_calls=state["useful_calls"], group=group, engine=engine)
