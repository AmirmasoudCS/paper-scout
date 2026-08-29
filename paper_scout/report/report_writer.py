"""
paper_scout.report.report_writer

Phase 7 — assembles a PipelineRun (papers + summaries + cross-paper
synthesis + future-work ideas) into the final markdown report, per
config.yaml's `report` section (output_dir, filename_template, include_toc).

Every paper section links back to its source (arXiv/Semantic
Scholar/HF page or PDF), so claims in the report are traceable to their
origin. Degrades gracefully throughout: a paper missing a summary falls
back to showing its abstract; a missing cross-paper synthesis or
future-work section is rendered as an explicit "not available" note
rather than silently omitted or crashing the report generation.
"""

from __future__ import annotations

import logging
import re
from datetime import date as date_type
from pathlib import Path
from typing import Optional

from paper_scout.utils.models import Paper, PipelineRun

logger = logging.getLogger(__name__)

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")
_ANCHOR_STRIP_RE = re.compile(r"[^a-z0-9\s-]")


def slugify(text: str) -> str:
    """Lowercase, hyphen-separated slug — used for filenames (e.g. query_slug)."""
    slug = _SLUG_STRIP_RE.sub("-", text.lower()).strip("-")
    return slug or "untitled"

def build_run_dir_name(pipeline_run: PipelineRun) -> str:
    """Folder name for one pipeline run's self-contained output directory."""
    query_slug = slugify(pipeline_run.query)
    run_date = (
        pipeline_run.run_timestamp.date()
        if hasattr(pipeline_run.run_timestamp, "date")
        else date_type.today()
    )
    return f"{query_slug}_{run_date.isoformat()}"

def _anchor(text: str) -> str:
    """
    GitHub-flavored-markdown-style heading anchor: lowercase, spaces to
    hyphens, strip everything but alphanumerics/spaces/hyphens. Used so
    the table of contents links actually land on the right heading.
    """
    lowered = text.lower()
    cleaned = _ANCHOR_STRIP_RE.sub("", lowered)
    return re.sub(r"\s+", "-", cleaned.strip())


def _paper_heading(index: int, paper: Paper) -> str:
    return f"{index}. {paper.title}"


def _format_authors(paper: Paper) -> str:
    if not paper.authors:
        return "Unknown authors"
    if len(paper.authors) <= 3:
        return ", ".join(paper.authors)
    return f"{', '.join(paper.authors[:3])}, et al."


def _format_paper_meta_line(paper: Paper) -> str:
    parts = []
    parts.append(_format_authors(paper))
    if paper.published_date:
        parts.append(paper.published_date.isoformat())
    parts.append(f"*{_source_label(paper)}*")
    if paper.citation_count is not None:
        parts.append(f"{paper.citation_count} citations")
    return " · ".join(parts)


def _source_label(paper: Paper) -> str:
    # Paper.model_config uses use_enum_values=True, so paper.source is
    # already a plain string (e.g. "arxiv") rather than a SourceName member.
    labels = {
        "arxiv": "arXiv",
        "semantic_scholar": "Semantic Scholar",
        "huggingface_papers": "HF Papers",
    }
    return labels.get(str(paper.source), str(paper.source))

def _has_no_grounding_text(paper: Paper) -> bool:
    """True if this paper has neither extracted Limitations nor Future
    Work text — i.e. any future-work ideas touching it in the report
    can only have come from Tier 2 inference, never Tier 1 grounding.
    Mirrors synthesize.future_work._has_grounding_text()."""
    sections = paper.extracted_sections
    if sections is None:
        return True
    return not sections.limitations and not sections.future_work

def _render_paper_section(index: int, paper: Paper) -> str:
    lines = [f"### {_paper_heading(index, paper)}", ""]
    lines.append(_format_paper_meta_line(paper))
    lines.append("")

    link = paper.url or paper.pdf_url
    if link:
        lines.append(f"[View source]({link})")
        lines.append("")

    if paper.summary is not None:
        lines.append(f"**Problem:** {paper.summary.problem}")
        lines.append("")
        lines.append(f"**Method:** {paper.summary.method}")
        lines.append("")
        lines.append(f"**Key result:** {paper.summary.key_result}")
        lines.append("")
        if paper.summary.stated_limitations:
            lines.append(f"**Stated limitations:** {paper.summary.stated_limitations}")
            lines.append("")
        if _has_no_grounding_text(paper):
            lines.append(
                "*This paper had no extractable Limitations/Future Work section — any "
                "future-work ideas involving it are inferred, not author-stated. See "
                "\"Future Work Ideas (Inferred)\" above.*"
            )
            lines.append("")
    else:
        logger.info("No summary available for %r — falling back to abstract", paper.title)
        lines.append("*No structured summary available — showing abstract.*")
        lines.append("")
        lines.append(paper.abstract.strip())
        lines.append("")

    return "\n".join(lines)


def _render_toc(papers: list[Paper]) -> str:
    lines = ["## Table of Contents", ""]
    lines.append("- [Cross-Paper Synthesis](#cross-paper-synthesis)")
    lines.append("- [Future Work Ideas](#future-work-ideas)")
    lines.append("- [Future Work Ideas (Inferred)](#future-work-ideas-inferred)")
    lines.append("- [Papers](#papers)")
    for i, paper in enumerate(papers, start=1):
        heading = _paper_heading(i, paper)
        lines.append(f"  - [{heading}](#{_anchor(heading)})")
    lines.append("")
    return "\n".join(lines)


def render_report(pipeline_run: PipelineRun, config: dict) -> str:
    """
    Render the full markdown report for a PipelineRun. Pure function —
    does not touch the filesystem. See write_report() for that.
    """
    report_cfg = config.get("report", {})
    include_toc = report_cfg.get("include_toc", True)

    lines: list[str] = []
    lines.append(f"# Research Report: {pipeline_run.query}")
    lines.append("")
    lines.append(
        f"*Generated {pipeline_run.run_timestamp.strftime('%Y-%m-%d %H:%M UTC')} "
        f"· {len(pipeline_run.papers)} papers*"
    )
    lines.append("")

    if include_toc and pipeline_run.papers:
        lines.append(_render_toc(pipeline_run.papers))

    lines.append("## Cross-Paper Synthesis")
    lines.append("")
    if pipeline_run.cross_paper_synthesis:
        lines.append(pipeline_run.cross_paper_synthesis.strip())
    else:
        lines.append("*Cross-paper synthesis not available for this run.*")
    lines.append("")

    lines.append("## Future Work Ideas")
    lines.append("")
    if pipeline_run.future_work_ideas:
        lines.append(pipeline_run.future_work_ideas.strip())
    else:
        lines.append(
            "*No grounded future-work ideas were generated for this run — this can happen "
            "if no paper had extractable Limitations/Future Work sections.*"
        )
    lines.append("")

    lines.append("## Future Work Ideas (Inferred)")
    lines.append("")
    lines.append(
        "*The directions below are inferred by the model from each paper's problem/method/"
        "key-result summary, for papers that had no extractable Limitations/Future Work "
        "section. Unlike the section above, these are not statements the authors themselves "
        "made — treat them as speculative.*"
    )
    lines.append("")
    if pipeline_run.future_work_ideas_inferred:
        lines.append(pipeline_run.future_work_ideas_inferred.strip())
    else:
        lines.append("*No inferred future-work ideas were generated for this run.*")
    lines.append("")

    lines.append("## Papers")
    lines.append("")
    if not pipeline_run.papers:
        lines.append("*No papers were found for this query.*")
    else:
        for i, paper in enumerate(pipeline_run.papers, start=1):
            lines.append(_render_paper_section(i, paper))

    return "\n".join(lines).rstrip() + "\n"


def _build_filename(pipeline_run: PipelineRun, report_cfg: dict) -> str:
    template = report_cfg.get("filename_template", "{query_slug}_{date}.md")
    query_slug = slugify(pipeline_run.query)
    run_date = pipeline_run.run_timestamp.date() if hasattr(
        pipeline_run.run_timestamp, "date"
    ) else date_type.today()
    return template.format(query_slug=query_slug, date=run_date.isoformat())


def write_report(
    pipeline_run: PipelineRun,
    config: dict,
    output_dir: Optional[str | Path] = None,
    filename: Optional[str] = None,
) -> Path:
    report_cfg = config.get("report", {})
    target_dir = Path(output_dir) if output_dir is not None else Path(report_cfg.get("output_dir", "outputs"))
    target_dir.mkdir(parents=True, exist_ok=True)

    report_filename = filename if filename is not None else _build_filename(pipeline_run, report_cfg)
    report_path = target_dir / report_filename

    content = render_report(pipeline_run, config)
    report_path.write_text(content, encoding="utf-8")

    pipeline_run.report_path = str(report_path)
    logger.info("Wrote report for query %r -> %s", pipeline_run.query, report_path)
    return report_path