"""
paper_scout.pipeline

Phase 8 — wires Phases 1-7 into a single LangGraph state machine:

    fetch_sources -> dedupe_and_rank -> ingest -> summarize
        -> cross_paper_synthesis -> future_work -> write_report

True end-to-end per the project's UX goal: one query in, nothing shown
until the final report is ready (no intermediate prompts).

Each node function is a thin wrapper around an already-tested module
from Phases 1-7 — this file's only new logic is the state shape and
the sequencing. Every phase already degrades gracefully internally
(returns [] / None rather than raising), so nodes here mostly just
pass state through; the one exception is dedupe_and_rank, which uses
a plain try/except around the embedding-based ranking step since a
corrupted/uncached embedding model is a real failure mode (see the
project's recurring ISP-blocking issue) and we'd rather fall back to
unranked papers than crash the whole run.
"""

from __future__ import annotations

import logging
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from paper_scout.ingestion.ingest import ingest_papers
from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.ranking.dedupe import dedupe_papers
from paper_scout.ranking.rank import rank_papers
from paper_scout.report.report_writer import write_report
from paper_scout.sources.runner import fetch_all_sources
from paper_scout.summarize.summarizer import summarize_papers
from paper_scout.synthesize.cross_paper import synthesize_cross_paper
from paper_scout.synthesize.future_work import generate_future_work_ideas
from paper_scout.utils.models import Paper, PipelineRun

logger = logging.getLogger(__name__)


class PipelineState(TypedDict, total=False):
    query: str
    config: dict
    client: OllamaClient
    raw_papers: list[Paper]
    papers: list[Paper]
    cross_paper_synthesis: Optional[str]
    future_work_ideas: Optional[str]
    pipeline_run: PipelineRun


# ── Nodes ────────────────────────────────────────────────────────────


def node_fetch_sources(state: PipelineState) -> dict:
    logger.info("Fetching papers for query: %r", state["query"])
    raw_papers = fetch_all_sources(state["query"], state["config"])
    logger.info("Fetched %d raw papers across all sources", len(raw_papers))
    return {"raw_papers": raw_papers}


def node_dedupe_and_rank(state: PipelineState) -> dict:
    ranking_cfg = state["config"]["ranking"]
    search_cfg = state["config"]["search"]

    deduped = dedupe_papers(
        state["raw_papers"], similarity_threshold=ranking_cfg["dedupe_similarity_threshold"]
    )

    try:
        ranked = rank_papers(
            deduped,
            query=state["query"],
            embedding_model_name=ranking_cfg["embedding_model"],
            embedding_device=ranking_cfg["embedding_device"],
            weights=ranking_cfg["weights"],
            date_range_days=search_cfg["date_range_days"],
        )
    except Exception as exc:
        # Ranking depends on downloading/loading an embedding model — a real
        # failure mode given this project's recurring ISP-blocking issue.
        # Fall back to the deduped-but-unranked list rather than losing the
        # whole run over it.
        logger.error("Ranking failed (%s) — falling back to unranked deduped papers", exc)
        ranked = deduped

    final_count = search_cfg["final_paper_count"]
    top_papers = ranked[:final_count]
    logger.info(
        "Deduped %d -> %d, ranked, kept top %d", len(state["raw_papers"]), len(deduped), len(top_papers)
    )
    return {"papers": top_papers}


def node_ingest(state: PipelineState) -> dict:
    logger.info("Ingesting PDFs/sections for %d papers", len(state["papers"]))
    papers = ingest_papers(state["papers"], state["config"]["ingestion"])
    return {"papers": papers}


def node_summarize(state: PipelineState) -> dict:
    logger.info("Summarizing %d papers", len(state["papers"]))
    papers = summarize_papers(state["papers"], state["client"])
    return {"papers": papers}


def node_cross_paper_synthesis(state: PipelineState) -> dict:
    synthesis = synthesize_cross_paper(state["papers"], state["query"], state["client"])
    return {"cross_paper_synthesis": synthesis}


def node_future_work(state: PipelineState) -> dict:
    future_work = generate_future_work_ideas(
        state["papers"], state.get("cross_paper_synthesis") or "", state["client"]
    )
    return {"future_work_ideas": future_work}


def node_write_report(state: PipelineState) -> dict:
    run = PipelineRun(
        query=state["query"],
        papers=state["papers"],
        cross_paper_synthesis=state.get("cross_paper_synthesis"),
        future_work_ideas=state.get("future_work_ideas"),
    )
    write_report(run, state["config"])
    return {"pipeline_run": run}


# ── Graph assembly ───────────────────────────────────────────────────


def build_pipeline_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("fetch_sources", node_fetch_sources)
    graph.add_node("dedupe_and_rank", node_dedupe_and_rank)
    graph.add_node("ingest", node_ingest)
    graph.add_node("summarize", node_summarize)
    graph.add_node("cross_paper_synthesis", node_cross_paper_synthesis)
    graph.add_node("future_work", node_future_work)
    graph.add_node("write_report", node_write_report)

    graph.add_edge(START, "fetch_sources")
    graph.add_edge("fetch_sources", "dedupe_and_rank")
    graph.add_edge("dedupe_and_rank", "ingest")
    graph.add_edge("ingest", "summarize")
    graph.add_edge("summarize", "cross_paper_synthesis")
    graph.add_edge("cross_paper_synthesis", "future_work")
    graph.add_edge("future_work", "write_report")
    graph.add_edge("write_report", END)

    return graph.compile()


def run_pipeline(query: str, config: dict, client: Optional[OllamaClient] = None) -> PipelineRun:
    """
    Run the full end-to-end pipeline for `query` and return the
    resulting PipelineRun (report already written to disk at
    pipeline_run.report_path).

    If `client` isn't provided, one is built from config — verified
    against the locally pulled Ollama models first so a missing/
    misnamed model fails fast with a clear message instead of a
    confusing silent-empty-report failure four stages later.
    """
    if client is None:
        client = OllamaClient.from_config(config)

    if not client.is_available():
        raise RuntimeError(
            "Ollama server is not reachable. Make sure `ollama serve` is running "
            "before starting the pipeline."
        )

    verified = client.verify_configured_models()
    missing = [tier for tier, ok in verified.items() if not ok]
    if missing:
        raise RuntimeError(
            f"Configured model(s) for {missing} not found locally. "
            f"Run `ollama pull <model>` for the models named in config.yaml's llm section."
        )

    app = build_pipeline_graph()
    final_state = app.invoke({"query": query, "config": config, "client": client})
    return final_state["pipeline_run"]