"""
Tests for paper_scout.ingestion (Phase 3).

Section-extraction tests run against a synthetic PDF built in-process
with PyMuPDF, so they don't depend on network access — deliberately,
given this project's recurring ISP-blocking issue. The PDF download
test is a live-network smoke test and is skipped (not failed) if the
network is unreachable.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from paper_scout.ingestion.pdf_fetch import fetch_pdf
from paper_scout.ingestion.section_extract import extract_sections, extract_text
from paper_scout.utils.models import Paper, SourceName

# ── Fixtures ─────────────────────────────────────────────────────────

SAMPLE_TARGET_SECTIONS = ["abstract", "conclusion", "limitations", "future work"]


def _make_pdf(tmp_path: Path, filename: str, body: str) -> Path:
    """Render `body` as simple single-column text into a real PDF file."""
    doc = pymupdf.open()
    page = doc.new_page()
    rect = pymupdf.Rect(50, 50, 545, 792)
    page.insert_textbox(rect, body, fontsize=10)
    pdf_path = tmp_path / filename
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


WELL_FORMED_BODY = """Abstract
This paper introduces a method for testing section extraction pipelines. We show that synthetic PDFs are sufficient for validating heading-detection heuristics without relying on network access.

1. Introduction
Section extraction is a common preprocessing step in literature review pipelines. Prior work has relied on manual annotation.

2. Method
We construct synthetic single-column PDFs with clearly labeled section headings and known ground-truth content, then verify the extractor recovers each section correctly.

3. Conclusion
We demonstrated a lightweight heading-based extractor recovers target sections from single-column academic PDFs with high reliability.

4. Limitations
Our approach does not handle multi-column layouts well and can be confused by figures or tables that interrupt heading detection. It also assumes English section headings.

5. Future Work
Future work should explore layout-aware extraction models and multilingual heading detection to generalize beyond the common single-column English case.

References
[1] Smith, J. et al. A prior paper on section extraction. 2021.
"""

COMBINED_HEADING_BODY = """Abstract
A short paper testing the combined-heading case where limitations and future work share one section.

1. Conclusion
This is the conclusion text for the combined heading test.

2. Limitations and Future Work
The main limitation of this study is its narrow scope. Future work should broaden the scope to more domains and validate on real-world PDFs.

References
[1] Someone. Some other paper.
"""

NO_SECTIONS_BODY = """This document has no clear section headings at all, it's just a
wall of unstructured text simulating a badly-OCR'd scanned paper where
heading detection is expected to fail gracefully and fall back cleanly
without raising any exceptions during extraction.
"""


@pytest.fixture
def well_formed_pdf(tmp_path) -> Path:
    return _make_pdf(tmp_path, "well_formed.pdf", WELL_FORMED_BODY)


@pytest.fixture
def combined_heading_pdf(tmp_path) -> Path:
    return _make_pdf(tmp_path, "combined.pdf", COMBINED_HEADING_BODY)


@pytest.fixture
def no_sections_pdf(tmp_path) -> Path:
    return _make_pdf(tmp_path, "no_sections.pdf", NO_SECTIONS_BODY)


def _sample_paper(pdf_url: str | None = "https://arxiv.org/pdf/2401.00001") -> Paper:
    return Paper(
        title="A Sample Paper For Testing",
        authors=["A. Researcher"],
        abstract="This is the metadata abstract, distinct from any in-PDF abstract.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
        pdf_url=pdf_url,
    )


# ── extract_text ─────────────────────────────────────────────────────


def test_extract_text_returns_readable_content(well_formed_pdf):
    text = extract_text(well_formed_pdf)
    assert text is not None
    assert "Limitations" in text
    assert "Future Work" in text


def test_extract_text_returns_none_for_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.pdf"
    assert extract_text(missing) is None


# ── extract_sections: well-formed document ──────────────────────────


def _norm_ws(text: str) -> str:
    """Collapse whitespace/newlines so assertions aren't sensitive to PDF line wrapping."""
    return " ".join(text.split())


def test_extracts_all_target_sections(well_formed_pdf):
    sections, full_text_available = extract_sections(well_formed_pdf, SAMPLE_TARGET_SECTIONS)

    assert full_text_available is True
    assert sections.abstract is not None
    assert "synthetic PDFs are sufficient" in _norm_ws(sections.abstract)

    assert sections.conclusion is not None
    assert "lightweight heading-based extractor" in _norm_ws(sections.conclusion)

    assert sections.limitations is not None
    assert "multi-column layouts" in _norm_ws(sections.limitations)

    assert sections.future_work is not None
    assert "layout-aware extraction" in _norm_ws(sections.future_work)


def test_extracted_sections_do_not_bleed_into_each_other(well_formed_pdf):
    """Limitations text should not swallow the Future Work heading/content, and vice versa."""
    sections, _ = extract_sections(well_formed_pdf, SAMPLE_TARGET_SECTIONS)

    assert "Future Work" not in (sections.limitations or "")
    assert "multi-column layouts" not in (sections.future_work or "")
    assert "References" not in (sections.future_work or "")


def test_only_requested_target_sections_are_populated(well_formed_pdf):
    sections, _ = extract_sections(well_formed_pdf, ["limitations"])

    assert sections.limitations is not None
    assert sections.abstract is None
    assert sections.conclusion is None
    assert sections.future_work is None


# ── extract_sections: combined heading ──────────────────────────────


def test_combined_limitations_and_future_work_heading(combined_heading_pdf):
    sections, full_text_available = extract_sections(combined_heading_pdf, SAMPLE_TARGET_SECTIONS)

    assert full_text_available is True
    assert sections.limitations is not None
    assert sections.future_work is not None
    # Both categories should point at the same shared section body
    assert "narrow scope" in sections.limitations
    assert "broaden the scope" in sections.future_work


# ── extract_sections: graceful fallback ─────────────────────────────


def test_no_sections_found_falls_back_cleanly(no_sections_pdf):
    sections, full_text_available = extract_sections(no_sections_pdf, SAMPLE_TARGET_SECTIONS)

    assert full_text_available is True  # PDF parsed fine, just no headings matched
    assert sections.limitations is None
    assert sections.future_work is None


def test_missing_pdf_falls_back_to_metadata_abstract(tmp_path):
    missing = tmp_path / "does_not_exist.pdf"
    sections, full_text_available = extract_sections(
        missing,
        SAMPLE_TARGET_SECTIONS,
        fallback_abstract="Metadata abstract text.",
        fallback_to_abstract_only=True,
    )

    assert full_text_available is False
    assert sections.abstract == "Metadata abstract text."
    assert sections.limitations is None


def test_missing_pdf_without_fallback_abstract_returns_empty_sections(tmp_path):
    missing = tmp_path / "does_not_exist.pdf"
    sections, full_text_available = extract_sections(missing, SAMPLE_TARGET_SECTIONS)

    assert full_text_available is False
    assert sections.abstract is None


def test_backfills_metadata_abstract_when_in_pdf_abstract_not_found(no_sections_pdf):
    sections, full_text_available = extract_sections(
        no_sections_pdf,
        SAMPLE_TARGET_SECTIONS,
        fallback_abstract="Metadata abstract text.",
    )

    assert full_text_available is True
    assert sections.abstract == "Metadata abstract text."


# ── pdf_fetch ────────────────────────────────────────────────────────


def test_fetch_pdf_returns_none_when_no_pdf_url(tmp_path):
    paper = _sample_paper(pdf_url=None)
    result = fetch_pdf(paper, cache_dir=tmp_path)
    assert result is None


def test_fetch_pdf_uses_cache_on_second_call(tmp_path, well_formed_pdf):
    """If a file already exists at the computed cache path, fetch_pdf should
    return it immediately without attempting any network call."""
    paper = _sample_paper()
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()

    from paper_scout.ingestion.pdf_fetch import _cache_path

    dest = _cache_path(paper, cache_dir)
    dest.write_bytes(well_formed_pdf.read_bytes())

    result = fetch_pdf(paper, cache_dir=cache_dir, max_retries=1)
    assert result == dest


@pytest.mark.network
def test_fetch_pdf_live_download_smoke_test(tmp_path):
    """
    Live network smoke test — downloads a real, small, stable arXiv PDF.
    Skipped (not failed) if the network/ISP blocks the connection, since
    this project has a known recurring TLS-reset issue without a VPN.
    """
    paper = _sample_paper(pdf_url="https://arxiv.org/pdf/1706.03762")  # "Attention Is All You Need"
    result = fetch_pdf(paper, cache_dir=tmp_path, timeout_seconds=15, max_retries=1)

    if result is None:
        pytest.skip("Live PDF download failed — likely network/VPN issue, not a code bug")

    assert result.exists()
    assert result.stat().st_size > 0