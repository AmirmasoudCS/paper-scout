"""
paper_scout.ingestion.section_extract

Extracts target sections (Abstract, Conclusion, Limitations, Future Work)
from a downloaded PDF's full text, using heading-detection heuristics
rather than a layout model — good enough for the common single/double
column academic paper format, and it degrades gracefully rather than
raising when a section can't be found.

Design notes:
  - We find ALL heading-like lines in the document (not just target
    ones), so a target section's extracted text correctly stops at the
    START of the next section instead of running on.
  - "Limitations and Future Work" (a common combined heading) is
    detected and its text is assigned to BOTH categories.
  - Papers often list a section in the Table of Contents (a short line,
    immediately followed by another heading-like line) AND again at the
    real section start (a heading followed by several paragraphs of
    body text). When a heading appears more than once, we keep the
    occurrence with the longest trailing text, which reliably picks the
    real section over the TOC entry.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import pymupdf

from paper_scout.utils.models import ExtractedSections

logger = logging.getLogger(__name__)

# Category -> keywords that identify a heading as belonging to it.
_CATEGORY_KEYWORDS: dict[str, set[str]] = {
    "abstract": {"abstract"},
    "conclusion": {"conclusion", "conclusions", "concluding remarks", "summary and conclusion"},
    "limitations": {"limitations", "limitation", "limitations of this work"},
    "future_work": {
        "future work",
        "future works",
        "future directions",
        "directions for future work",
    },
}

# Headings that mark the end of the paper body — extraction always stops here.
_STOP_KEYWORDS: set[str] = {
    "references",
    "bibliography",
    "acknowledgments",
    "acknowledgements",
    "appendix",
}

_MAX_SECTION_CHARS = 6000

_HEADING_LINE_RE = re.compile(
    r"^(?:(?:[IVXLCM]+|\d{1,2}(?:\.\d{1,2})*)(?:\.\s+|\)\s+|\s+))?"
    r"([A-Za-z][A-Za-z &/,'-]{2,70})\s*$"
)


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().rstrip(".:").split())


def _categorize_heading(raw_heading: str) -> set[str]:
    """Return the set of category names this heading line matches (often 0 or 1, sometimes 2)."""
    norm = _normalize(raw_heading)
    categories: set[str] = set()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if norm in keywords:
            categories.add(category)
    # Handle combined headings like "limitations and future work"
    if not categories:
        has_limitations = any(kw in norm for kw in _CATEGORY_KEYWORDS["limitations"])
        has_future = any(kw in norm for kw in _CATEGORY_KEYWORDS["future_work"])
        if has_limitations and has_future and len(norm) < 60:
            categories.update({"limitations", "future_work"})
    return categories


def _is_stop_heading(raw_heading: str) -> bool:
    norm = _normalize(raw_heading)
    return any(norm == kw or norm.startswith(kw) for kw in _STOP_KEYWORDS)


def extract_text(pdf_path: str | Path) -> Optional[str]:
    """
    Extract raw text from a PDF, page-joined, using a column-aware
    reading-order heuristic.

    Plain page.get_text("text") interleaves left/right column text on
    two-column academic layouts, which mangles heading lines like
    "6. Limitations" so they no longer survive as clean, matchable
    lines for _find_headings(). Instead we read blocks (bounding boxes),
    sort by vertical position, and treat any block wider than ~60% of
    the page width as a full-width "flush point" (title, section
    heading, figure caption spanning both columns) that drains the
    accumulated left/right column buffers — sorted by y within each
    buffer — before continuing. Narrow blocks are bucketed left/right
    by their center x-position relative to the page midpoint.

    Single-column pages are nearly all "full-width" blocks, so this
    degrades to the same top-to-bottom order as before.
    """
    try:
        doc = pymupdf.open(str(pdf_path))
        pages_text: list[str] = []

        for page in doc:
            page_width = page.rect.width
            midpoint = page_width / 2.0

            raw_blocks = page.get_text("blocks")
            # block tuple: (x0, y0, x1, y1, text, block_no, block_type)
            text_blocks = [b for b in raw_blocks if b[6] == 0 and b[4].strip()]
            text_blocks.sort(key=lambda b: b[1])  # top-to-bottom first pass

            left_buf: list[tuple] = []
            right_buf: list[tuple] = []
            ordered_parts: list[str] = []

            def _drain() -> None:
                left_buf.sort(key=lambda b: b[1])
                right_buf.sort(key=lambda b: b[1])
                for b in left_buf:
                    ordered_parts.append(b[4])
                for b in right_buf:
                    ordered_parts.append(b[4])
                left_buf.clear()
                right_buf.clear()

            for b in text_blocks:
                x0, _y0, x1, _y1, text = b[0], b[1], b[2], b[3], b[4]
                block_width = x1 - x0
                if block_width > 0.6 * page_width:
                    _drain()
                    ordered_parts.append(text)
                else:
                    center_x = (x0 + x1) / 2.0
                    (left_buf if center_x < midpoint else right_buf).append(b)

            _drain()
            pages_text.append("\n".join(ordered_parts))

        doc.close()
        return "\n".join(pages_text)
    except Exception as exc:  # pymupdf can raise several different error types
        logger.warning("Failed to extract text from %s: %s", pdf_path, exc)
        return None

_LOWERCASE_CONNECTORS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in",
    "of", "on", "or", "the", "to", "with",
}


def _looks_like_heading_case(heading_text: str) -> bool:
    """Real section headings are Title Case or ALL CAPS. Ordinary wrapped
    body sentences that happen to lack trailing punctuation (and so still
    pass the character-class check) are not — this rejects those, so
    they can't be mistaken for a section boundary."""
    words = heading_text.split()
    if not words:
        return False
    if heading_text.isupper():
        return True
    for i, word in enumerate(words):
        core = word.strip("&/,'-")
        if not core:
            continue
        if i != 0 and core.lower() in _LOWERCASE_CONNECTORS:
            continue
        if not core[0].isupper():
            return False
    return True

def _find_headings(full_text: str) -> list[tuple[int, int, str]]:
    """
    Scan line-by-line for heading-like lines.
    Returns a list of (line_start_char_offset, line_end_char_offset, raw_heading_text),
    in document order.
    """
    headings: list[tuple[int, int, str]] = []
    offset = 0
    for line in full_text.split("\n"):
        line_start = offset
        line_end = offset + len(line)
        offset = line_end + 1  # account for the '\n' we split on

        stripped = line.strip()
        if not stripped or len(stripped) > 80:
            continue
        match = _HEADING_LINE_RE.match(stripped)
        if not match:
            continue
        heading_text = match.group(1).strip()
        # Skip short/noisy false positives like "A" or "I I"
        if len(heading_text) < 4:
            continue
        headings.append((line_start, line_end, heading_text))
    return headings


def _extract_sections_from_text(
    full_text: str,
    target_sections: list[str],
) -> ExtractedSections:
    headings = _find_headings(full_text)

    # For each category, gather all (content_length, content) candidates, pick the longest.
    best_by_category: dict[str, str] = {}

    for idx, (_, line_end, raw_heading) in enumerate(headings):
        categories = _categorize_heading(raw_heading)
        if not categories:
            continue

        # Find the offset where the NEXT heading (any kind, including stop headings) begins.
        next_offset = headings[idx + 1][0] if idx + 1 < len(headings) else len(full_text)

        section_text = full_text[line_end:next_offset].strip()
        section_text = section_text[:_MAX_SECTION_CHARS]

        for category in categories:
            existing = best_by_category.get(category, "")
            if len(section_text) > len(existing):
                best_by_category[category] = section_text

    target_set = {t.lower().replace(" ", "_") for t in target_sections}

    return ExtractedSections(
        abstract=best_by_category.get("abstract") if "abstract" in target_set else None,
        conclusion=best_by_category.get("conclusion") if "conclusion" in target_set else None,
        limitations=best_by_category.get("limitations") if "limitations" in target_set else None,
        future_work=best_by_category.get("future_work") if "future_work" in target_set else None,
    )


def extract_sections(
    pdf_path: str | Path,
    target_sections: list[str],
    fallback_abstract: Optional[str] = None,
    fallback_to_abstract_only: bool = True,
) -> tuple[ExtractedSections, bool]:
    """
    Extract target sections from a PDF.

    Returns (ExtractedSections, full_text_available):
      - full_text_available is True if we managed to read/parse the PDF at all
        (independent of whether every target section was actually found).
      - If parsing fails entirely and fallback_to_abstract_only is True and a
        fallback_abstract (e.g. from the paper metadata) is provided, returns
        an ExtractedSections with only `abstract` populated and
        full_text_available=False.
    """
    full_text = extract_text(pdf_path)

    if full_text is None:
        if fallback_to_abstract_only and fallback_abstract:
            logger.info("Falling back to metadata abstract only for %s", pdf_path)
            return ExtractedSections(abstract=fallback_abstract), False
        return ExtractedSections(), False

    sections = _extract_sections_from_text(full_text, target_sections)

    # If PDF text extraction succeeded but the abstract heading itself wasn't
    # found (common — abstracts are often unlabeled/styled differently),
    # backfill from metadata so downstream consumers still get one.
    if sections.abstract is None and fallback_abstract:
        sections.abstract = fallback_abstract

    return sections, True