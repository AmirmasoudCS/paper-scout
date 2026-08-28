"""
paper_scout.ingestion.ingest

Glue function combining pdf_fetch.py + section_extract.py into a single
per-paper ingestion step, populating Paper.extracted_sections and
Paper.full_text_available in place. Deferred from Phase 3 until the
final pipeline (Phase 8) so it could be wired against the real
orchestration shape rather than guessed at in isolation.
"""

from __future__ import annotations

import logging

from paper_scout.ingestion.pdf_fetch import fetch_pdf
from paper_scout.ingestion.section_extract import extract_sections
from paper_scout.utils.models import ExtractedSections, Paper

logger = logging.getLogger(__name__)


def ingest_paper(paper: Paper, ingestion_config: dict) -> Paper:
    """
    Download the paper's PDF (if available) and extract target sections,
    populating paper.extracted_sections and paper.full_text_available
    in place. Always returns the same paper object, never raises —
    on any failure, falls back to an abstract-only ExtractedSections
    (when fallback_to_abstract_only is set) so downstream phases always
    have *something* to work with.
    """
    pdf_path = fetch_pdf(
        paper,
        cache_dir=ingestion_config["pdf_cache_dir"],
        timeout_seconds=ingestion_config.get("download_timeout_seconds", 30),
    )

    if pdf_path is None:
        logger.info("No PDF available for %r — falling back to abstract only", paper.title)
        if ingestion_config.get("fallback_to_abstract_only", True):
            paper.extracted_sections = ExtractedSections(abstract=paper.abstract)
        else:
            paper.extracted_sections = ExtractedSections()
        paper.full_text_available = False
        return paper

    sections, full_text_available = extract_sections(
        pdf_path,
        target_sections=ingestion_config["target_sections"],
        fallback_abstract=paper.abstract,
        fallback_to_abstract_only=ingestion_config.get("fallback_to_abstract_only", True),
    )
    paper.extracted_sections = sections
    paper.full_text_available = full_text_available
    return paper


def ingest_papers(papers: list[Paper], ingestion_config: dict) -> list[Paper]:
    """
    Batch wrapper. One paper's ingestion failing never stops the batch —
    ingest_paper() already degrades gracefully per-paper.
    """
    for paper in papers:
        ingest_paper(paper, ingestion_config)
    return papers