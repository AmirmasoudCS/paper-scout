"""
Tests for paper_scout.report.report_writer (Phase 7).

No LLM or network dependency at all here — report_writer just
assembles already-populated PipelineRun/Paper objects into markdown,
so every test is a pure in-memory / tmp_path test.
"""

from __future__ import annotations

from datetime import date, datetime

from paper_scout.report.report_writer import render_report, slugify, write_report
from paper_scout.utils.models import ExtractedSections, Paper, PaperSummary, PipelineRun, SourceName

SAMPLE_CONFIG = {
    "report": {
        "output_dir": "outputs",
        "filename_template": "{query_slug}_{date}.md",
        "include_toc": True,
    }
}


def _paper_with_summary(title: str = "Grounded Future-Work Ideation") -> Paper:
    return Paper(
        title=title,
        authors=["A. Researcher", "B. Coauthor"],
        abstract="We study how to ground LLM-generated future-work ideas in extracted paper text.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
        url="https://arxiv.org/abs/2401.00001",
        pdf_url="https://arxiv.org/pdf/2401.00001",
        published_date=date(2024, 1, 15),
        citation_count=12,
        summary=PaperSummary(
            problem="Ungrounded LLM ideation tends to be generic.",
            method="Ground ideation in retrieved paper text via RAG.",
            key_result="Grounded ideation is rated more specific by reviewers.",
            stated_limitations="Only evaluated on English-language CS papers.",
        ),
    )


def _paper_without_summary(title: str = "Unsummarized Paper") -> Paper:
    return Paper(
        title=title,
        authors=["C. Author"],
        abstract="This paper's abstract should appear as a fallback since no summary exists.",
        source=SourceName.SEMANTIC_SCHOLAR,
        url="https://www.semanticscholar.org/paper/abc123",
    )


def _sample_pipeline_run(papers: list[Paper] | None = None) -> PipelineRun:
    return PipelineRun(
        query="grounded future-work ideation",
        run_timestamp=datetime(2024, 6, 1, 12, 0, 0),
        papers=papers if papers is not None else [_paper_with_summary()],
        cross_paper_synthesis="Papers in this set consistently favor retrieval-grounded approaches.",
        future_work_ideas="1. Multilingual grounding — extend beyond English-only evaluation.",
    )


# ── slugify ──────────────────────────────────────────────────────────


def test_slugify_basic():
    assert slugify("Grounded Future-Work Ideation") == "grounded-future-work-ideation"


def test_slugify_handles_punctuation_and_extra_spaces():
    assert slugify("  What's New in RAG?!  ") == "what-s-new-in-rag"


def test_slugify_empty_string_falls_back_to_untitled():
    assert slugify("") == "untitled"
    assert slugify("!!!") == "untitled"


# ── render_report: structure ─────────────────────────────────────────


def test_render_report_includes_query_and_paper_count():
    run = _sample_pipeline_run()
    report = render_report(run, SAMPLE_CONFIG)

    assert "grounded future-work ideation" in report
    assert "1 papers" in report


def test_render_report_includes_toc_when_enabled():
    run = _sample_pipeline_run()
    report = render_report(run, SAMPLE_CONFIG)

    assert "## Table of Contents" in report
    assert "[Cross-Paper Synthesis](#cross-paper-synthesis)" in report
    assert "[Future Work Ideas](#future-work-ideas)" in report


def test_render_report_omits_toc_when_disabled():
    config = {"report": {**SAMPLE_CONFIG["report"], "include_toc": False}}
    run = _sample_pipeline_run()
    report = render_report(run, config)

    assert "## Table of Contents" not in report


def test_render_report_toc_entries_use_valid_anchors():
    papers = [_paper_with_summary("Attention Is All You Need")]
    run = _sample_pipeline_run(papers)
    report = render_report(run, SAMPLE_CONFIG)

    assert "(#1-attention-is-all-you-need)" in report
    assert "### 1. Attention Is All You Need" in report


# ── render_report: synthesis / future-work sections ─────────────────


def test_render_report_includes_synthesis_and_future_work_text():
    run = _sample_pipeline_run()
    report = render_report(run, SAMPLE_CONFIG)

    assert "retrieval-grounded approaches" in report
    assert "Multilingual grounding" in report


def test_render_report_handles_missing_synthesis_gracefully():
    run = _sample_pipeline_run()
    run.cross_paper_synthesis = None
    report = render_report(run, SAMPLE_CONFIG)

    assert "not available for this run" in report


def test_render_report_handles_missing_future_work_gracefully():
    run = _sample_pipeline_run()
    run.future_work_ideas = None
    report = render_report(run, SAMPLE_CONFIG)

    assert "no grounded future-work ideas" in report.lower()


# ── render_report: per-paper sections ────────────────────────────────


def test_render_report_shows_structured_summary_when_available():
    run = _sample_pipeline_run([_paper_with_summary()])
    report = render_report(run, SAMPLE_CONFIG)

    assert "**Problem:** Ungrounded LLM ideation tends to be generic." in report
    assert "**Method:**" in report
    assert "**Key result:**" in report
    assert "**Stated limitations:** Only evaluated on English-language CS papers." in report


def test_render_report_falls_back_to_abstract_when_no_summary():
    run = _sample_pipeline_run([_paper_without_summary()])
    report = render_report(run, SAMPLE_CONFIG)

    assert "No structured summary available" in report
    assert "This paper's abstract should appear as a fallback" in report


def test_render_report_omits_stated_limitations_line_when_none():
    paper = _paper_with_summary()
    paper.summary.stated_limitations = None
    run = _sample_pipeline_run([paper])
    report = render_report(run, SAMPLE_CONFIG)

    assert "**Stated limitations:**" not in report


def test_render_report_includes_source_link():
    run = _sample_pipeline_run([_paper_with_summary()])
    report = render_report(run, SAMPLE_CONFIG)

    assert "[View source](https://arxiv.org/abs/2401.00001)" in report


def test_render_report_includes_author_and_citation_metadata():
    run = _sample_pipeline_run([_paper_with_summary()])
    report = render_report(run, SAMPLE_CONFIG)

    assert "A. Researcher, B. Coauthor" in report
    assert "2024-01-15" in report
    assert "12 citations" in report
    assert "arXiv" in report


def test_render_report_truncates_long_author_lists():
    paper = _paper_with_summary()
    paper.authors = ["A. One", "B. Two", "C. Three", "D. Four", "E. Five"]
    run = _sample_pipeline_run([paper])
    report = render_report(run, SAMPLE_CONFIG)

    assert "A. One, B. Two, C. Three, et al." in report
    assert "D. Four" not in report


def test_render_report_handles_no_papers():
    run = _sample_pipeline_run([])
    report = render_report(run, SAMPLE_CONFIG)

    assert "No papers were found for this query." in report


def test_render_report_multiple_papers_each_get_own_section():
    papers = [_paper_with_summary("Paper A"), _paper_without_summary("Paper B")]
    run = _sample_pipeline_run(papers)
    report = render_report(run, SAMPLE_CONFIG)

    assert "### 1. Paper A" in report
    assert "### 2. Paper B" in report


# ── write_report: filesystem behavior ────────────────────────────────


def test_write_report_creates_file_with_expected_name(tmp_path):
    run = _sample_pipeline_run()

    path = write_report(run, SAMPLE_CONFIG, output_dir=tmp_path)

    assert path == tmp_path / "grounded-future-work-ideation_2024-06-01.md"
    assert path.exists()


def test_write_report_content_matches_render_report(tmp_path):
    run = _sample_pipeline_run()

    path = write_report(run, SAMPLE_CONFIG, output_dir=tmp_path)

    assert path.read_text(encoding="utf-8") == render_report(run, SAMPLE_CONFIG)


def test_write_report_sets_pipeline_run_report_path(tmp_path):
    run = _sample_pipeline_run()
    assert run.report_path is None

    path = write_report(run, SAMPLE_CONFIG, output_dir=tmp_path)

    assert run.report_path == str(path)


def test_write_report_creates_output_dir_if_missing(tmp_path):
    nested_dir = tmp_path / "nested" / "outputs"
    run = _sample_pipeline_run()

    path = write_report(run, SAMPLE_CONFIG, output_dir=nested_dir)

    assert path.exists()
    assert nested_dir.exists()


def test_write_report_falls_back_to_config_output_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = {"report": {**SAMPLE_CONFIG["report"], "output_dir": "my_outputs"}}
    run = _sample_pipeline_run()

    path = write_report(run, config)  # no output_dir override

    assert path.resolve() == (tmp_path / "my_outputs" / "grounded-future-work-ideation_2024-06-01.md").resolve()
    assert path.exists()

def test_render_report_marks_papers_with_no_grounding_text():
    paper = _paper_with_summary()
    paper.extracted_sections = ExtractedSections()  # no limitations, no future_work
    run = _sample_pipeline_run([paper])
    report = render_report(run, SAMPLE_CONFIG)

    assert "no extractable Limitations/Future Work section" in report


def test_render_report_does_not_mark_papers_with_grounding_text():
    paper = _paper_with_summary()
    paper.extracted_sections = ExtractedSections(limitations="Some limitation.")
    run = _sample_pipeline_run([paper])
    report = render_report(run, SAMPLE_CONFIG)

    assert "no extractable Limitations/Future Work section" not in report