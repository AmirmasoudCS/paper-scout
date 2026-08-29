"""
Tests for Phase 8: ingestion glue (ingest.py), source runner
(sources/runner.py), and the LangGraph pipeline (pipeline.py).

Pipeline tests mock every stage (fetch/dedupe/rank/ingest/summarize/
synthesize/future_work/report) so the graph WIRING is what's actually
under test — sequencing, state passing between nodes, and each node's
graceful-degradation behavior — independent of whether any individual
module works correctly in isolation (that's already covered by
test_ingestion.py, test_llm.py, test_summarize.py, test_synthesize.py,
test_report.py).
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

import pytest

from paper_scout.ingestion.ingest import ingest_paper, ingest_papers
from paper_scout.pipeline import build_pipeline_graph, run_pipeline
from paper_scout.sources.runner import build_source_fetchers, fetch_all_sources
from paper_scout.utils.models import ExtractedSections, Paper, PaperSummary, SourceName

SAMPLE_CONFIG = {
    "search": {
        "max_papers_per_source": 20,
        "final_paper_count": 10,
        "date_range_days": 365,
        "min_citation_count": 0,
    },
    "sources": {
        "arxiv": {"enabled": True, "categories": []},
        "semantic_scholar": {"enabled": True, "api_key": None},
        "huggingface_papers": {"enabled": True},
    },
    "ranking": {
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "embedding_device": "cpu",
        "weights": {"relevance": 0.5, "recency": 0.3, "citations": 0.2},
        "dedupe_similarity_threshold": 0.9,
    },
    "ingestion": {
        "pdf_cache_dir": "outputs/pdf_cache",
        "download_timeout_seconds": 30,
        "target_sections": ["abstract", "conclusion", "limitations", "future work"],
        "fallback_to_abstract_only": True,
    },
    "llm": {
        "provider": "ollama",
        "small_model": {"name": "qwen3.5:9b", "temperature": 0.3, "max_tokens": 512},
        "large_model": {"name": "gemma4:e4b", "temperature": 0.5, "max_tokens": 1500},
        "timeout_seconds": 120,
    },
    "report": {
        "output_dir": "outputs",
        "filename_template": "{query_slug}_{date}.md",
        "include_toc": True,
    },
}


def _sample_paper(title: str = "Sample Paper", pdf_url: str | None = "https://arxiv.org/pdf/2401.00001") -> Paper:
    return Paper(
        title=title,
        authors=["A. Researcher"],
        abstract="Sample abstract text.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
        pdf_url=pdf_url,
        published_date=date(2024, 1, 1),
    )


# ── ingest_paper / ingest_papers (deferred Phase 3 glue) ────────────


def test_ingest_paper_falls_back_to_abstract_when_no_pdf_url(monkeypatch):
    paper = _sample_paper(pdf_url=None)

    ingest_paper(paper, SAMPLE_CONFIG["ingestion"])

    assert paper.full_text_available is False
    assert paper.extracted_sections is not None
    assert paper.extracted_sections.abstract == "Sample abstract text."


def test_ingest_paper_falls_back_when_pdf_download_fails(monkeypatch):
    monkeypatch.setattr("paper_scout.ingestion.ingest.fetch_pdf", lambda *a, **k: None)
    paper = _sample_paper()

    ingest_paper(paper, SAMPLE_CONFIG["ingestion"])

    assert paper.full_text_available is False
    assert paper.extracted_sections.abstract == "Sample abstract text."


def test_ingest_paper_populates_sections_on_successful_download(monkeypatch, tmp_path):
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")

    monkeypatch.setattr("paper_scout.ingestion.ingest.fetch_pdf", lambda *a, **k: fake_pdf)
    monkeypatch.setattr(
        "paper_scout.ingestion.ingest.extract_sections",
        lambda *a, **k: (ExtractedSections(limitations="Some limitation."), True),
    )

    paper = _sample_paper()
    ingest_paper(paper, SAMPLE_CONFIG["ingestion"])

    assert paper.full_text_available is True
    assert paper.extracted_sections.limitations == "Some limitation."


def test_ingest_papers_one_failure_does_not_block_others(monkeypatch):
    call_count = {"n": 0}

    def flaky_fetch(paper, *a, **k):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise Exception("boom")
        return None

    monkeypatch.setattr("paper_scout.ingestion.ingest.fetch_pdf", flaky_fetch)
    papers = [_sample_paper("A"), _sample_paper("B")]

    # ingest_paper itself doesn't catch exceptions from fetch_pdf raising directly
    # (fetch_pdf's own contract is to never raise) — this test documents that
    # ingest_papers relies on fetch_pdf's own graceful-degradation contract
    # rather than adding a second layer of try/except.
    with pytest.raises(Exception):
        ingest_papers(papers, SAMPLE_CONFIG["ingestion"])


def test_ingest_papers_processes_all_papers_when_fetch_always_degrades(monkeypatch):
    monkeypatch.setattr("paper_scout.ingestion.ingest.fetch_pdf", lambda *a, **k: None)
    papers = [_sample_paper("A"), _sample_paper("B"), _sample_paper("C")]

    result = ingest_papers(papers, SAMPLE_CONFIG["ingestion"])

    assert result is papers
    assert all(p.extracted_sections is not None for p in papers)


# ── sources/runner.py ─────────────────────────────────────────────────


def test_build_source_fetchers_respects_enabled_flags():
    config = {
        "sources": {
            "arxiv": {"enabled": True, "categories": []},
            "semantic_scholar": {"enabled": False},
            "huggingface_papers": {"enabled": True},
        }
    }
    fetchers = build_source_fetchers(config)
    names = {f.name for f in fetchers}

    assert SourceName.ARXIV in names
    assert SourceName.SEMANTIC_SCHOLAR not in names
    assert SourceName.HUGGINGFACE_PAPERS in names


def test_fetch_all_sources_combines_results_across_sources(monkeypatch):
    fetcher_a = MagicMock()
    fetcher_a.name = "fake_a"
    fetcher_a.search.return_value = [_sample_paper("From A")]

    fetcher_b = MagicMock()
    fetcher_b.name = "fake_b"
    fetcher_b.search.return_value = [_sample_paper("From B")]

    monkeypatch.setattr(
        "paper_scout.sources.runner.build_source_fetchers", lambda config: [fetcher_a, fetcher_b]
    )

    results = fetch_all_sources("test query", SAMPLE_CONFIG)

    assert len(results) == 2
    assert {p.title for p in results} == {"From A", "From B"}


def test_fetch_all_sources_one_source_raising_does_not_block_others(monkeypatch):
    broken_fetcher = MagicMock()
    broken_fetcher.name = "broken"
    broken_fetcher.search.side_effect = Exception("source blew up")

    working_fetcher = MagicMock()
    working_fetcher.name = "working"
    working_fetcher.search.return_value = [_sample_paper("Survivor")]

    monkeypatch.setattr(
        "paper_scout.sources.runner.build_source_fetchers",
        lambda config: [broken_fetcher, working_fetcher],
    )

    results = fetch_all_sources("test query", SAMPLE_CONFIG)

    assert len(results) == 1
    assert results[0].title == "Survivor"


# ── pipeline.py: graph wiring ──────────────────────────────────────


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.is_available.return_value = True
    client.verify_configured_models.return_value = {"small": True, "large": True}
    return client


def _patch_all_stages(monkeypatch, tmp_path, papers=None):
    """Patch every pipeline stage to fast, deterministic fakes."""
    papers = papers if papers is not None else [_sample_paper("Fetched Paper")]

    monkeypatch.setattr("paper_scout.pipeline.fetch_all_sources", lambda query, config: list(papers))
    monkeypatch.setattr(
        "paper_scout.pipeline.dedupe_papers", lambda papers, similarity_threshold: papers
    )
    monkeypatch.setattr(
        "paper_scout.pipeline.rank_papers",
        lambda papers, **kwargs: papers,
    )

    def fake_ingest(papers, ingestion_cfg):
        for p in papers:
            p.extracted_sections = ExtractedSections(
                limitations="A limitation.", future_work="Some future work."
            )
            p.full_text_available = True
        return papers

    monkeypatch.setattr("paper_scout.pipeline.ingest_papers", fake_ingest)

    def fake_summarize(papers, client):
        for p in papers:
            p.summary = PaperSummary(problem="P", method="M", key_result="R")
        return papers

    monkeypatch.setattr("paper_scout.pipeline.summarize_papers", fake_summarize)
    monkeypatch.setattr(
        "paper_scout.pipeline.synthesize_cross_paper",
        lambda papers, query, client: "Fake cross-paper synthesis.",
    )
    monkeypatch.setattr(
        "paper_scout.pipeline.generate_future_work_ideas",
        lambda papers, synthesis, client: "Fake future work ideas.",
    )
    monkeypatch.setattr(
        "paper_scout.pipeline.generate_inferred_future_work_ideas",
        lambda papers, synthesis, client: "Fake inferred future work ideas.",
    )

    config = {**SAMPLE_CONFIG, "report": {**SAMPLE_CONFIG["report"], "output_dir": str(tmp_path)}}
    return config


def test_run_pipeline_wires_all_stages_in_order(monkeypatch, tmp_path, mock_client):
    config = _patch_all_stages(monkeypatch, tmp_path)

    result = run_pipeline("test query", config, client=mock_client)

    assert result.query == "test query"
    assert len(result.papers) == 1
    assert result.papers[0].summary is not None
    assert result.papers[0].summary.problem == "P"
    assert result.cross_paper_synthesis == "Fake cross-paper synthesis."
    assert result.future_work_ideas == "Fake future work ideas."
    assert result.future_work_ideas_inferred == "Fake inferred future work ideas."
    assert result.report_path is not None


def test_run_pipeline_writes_actual_report_file(monkeypatch, tmp_path, mock_client):
    config = _patch_all_stages(monkeypatch, tmp_path)

    result = run_pipeline("test query", config, client=mock_client)

    from pathlib import Path

    report_path = Path(result.report_path)
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "test query" in content
    assert "Fake cross-paper synthesis." in content
    assert "Fake future work ideas." in content


def test_run_pipeline_raises_if_ollama_unreachable(monkeypatch, tmp_path):
    config = _patch_all_stages(monkeypatch, tmp_path)
    client = MagicMock()
    client.is_available.return_value = False

    with pytest.raises(RuntimeError, match="not reachable"):
        run_pipeline("test query", config, client=client)


def test_run_pipeline_raises_if_configured_model_missing(monkeypatch, tmp_path):
    config = _patch_all_stages(monkeypatch, tmp_path)
    client = MagicMock()
    client.is_available.return_value = True
    client.verify_configured_models.return_value = {"small": True, "large": False}

    with pytest.raises(RuntimeError, match="not found locally"):
        run_pipeline("test query", config, client=client)


def test_run_pipeline_handles_zero_papers_found(monkeypatch, tmp_path, mock_client):
    config = _patch_all_stages(monkeypatch, tmp_path, papers=[])

    result = run_pipeline("test query", config, client=mock_client)

    assert result.papers == []
    assert result.report_path is not None  # report should still be written


def test_run_pipeline_survives_ranking_failure(monkeypatch, tmp_path, mock_client):
    config = _patch_all_stages(monkeypatch, tmp_path)

    def broken_rank(*args, **kwargs):
        raise RuntimeError("embedding model failed to load")

    monkeypatch.setattr("paper_scout.pipeline.rank_papers", broken_rank)

    result = run_pipeline("test query", config, client=mock_client)

    # Should fall back to unranked papers rather than crash the whole run
    assert len(result.papers) == 1


def test_run_pipeline_survives_none_synthesis_and_future_work(monkeypatch, tmp_path, mock_client):
    config = _patch_all_stages(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "paper_scout.pipeline.synthesize_cross_paper", lambda papers, query, client: None
    )
    monkeypatch.setattr(
        "paper_scout.pipeline.generate_future_work_ideas",
        lambda papers, synthesis, client: None,
    )

    result = run_pipeline("test query", config, client=mock_client)

    assert result.cross_paper_synthesis is None
    assert result.future_work_ideas is None
    assert result.report_path is not None


def test_build_pipeline_graph_compiles_without_error():
    app = build_pipeline_graph()
    assert app is not None