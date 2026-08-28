"""
scripts/diagnose_headings.py

Diagnostic (not a test) for the "conclusion/future_work still 0% after
the column fix" problem. Column-interleaving was only one hypothesis —
this script checks the more basic question: on real downloaded PDFs,
does ANY line in the extracted text actually match _HEADING_LINE_RE at
all, for headings we expect to exist (Conclusion, Limitations, Future
Work, etc)?

For one PDF, prints:
  1. Every line _find_headings() currently detects as heading-like,
     with its categorization (or "uncategorized").
  2. Every raw line in the extracted text that CONTAINS a target
     keyword (e.g. "limitations", "conclusion") anywhere in it, even
     if it did NOT get detected as a heading line — so we can see the
     actual raw formatting real papers use (numbering style, extra
     characters, bold-run artifacts, line-splitting, etc) and compare
     it against what _HEADING_LINE_RE expects.

Usage:
    python scripts/diagnose_headings.py outputs/pdf_cache/<some>.pdf
    python scripts/diagnose_headings.py outputs/pdf_cache/<some>.pdf --full-text
"""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_scout.ingestion.section_extract import (
    _categorize_heading,
    _find_headings,
    _is_stop_heading,
    extract_text,
)

KEYWORDS_OF_INTEREST = [
    "abstract",
    "conclusion",
    "limitation",
    "future work",
    "future direction",
    "references",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path)
    parser.add_argument(
        "--full-text",
        action="store_true",
        help="Also dump the entire extracted text (long).",
    )
    args = parser.parse_args()

    text = extract_text(args.pdf_path)
    if text is None:
        print(f"extract_text() returned None for {args.pdf_path} — extraction failed entirely.")
        return

    print(f"Extracted {len(text)} chars from {args.pdf_path.name}\n")

    # ── 1. What _find_headings currently detects ──────────────────
    headings = _find_headings(text)
    print(f"_find_headings() detected {len(headings)} heading-like lines:\n")
    for _start, _end, raw in headings:
        cats = _categorize_heading(raw)
        stop = _is_stop_heading(raw)
        tag = f"category={cats}" if cats else ("STOP" if stop else "uncategorized")
        print(f"  [{tag}] {raw!r}")

    # ── 2. Raw lines containing a keyword, whether or not detected ─
    print("\nRaw lines containing a target keyword (detected or not):\n")
    detected_raw_set = {raw for _s, _e, raw in headings}
    for i, line in enumerate(text.split("\n")):
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if any(kw in lower for kw in KEYWORDS_OF_INTEREST):
            was_detected = stripped in detected_raw_set or any(
                stripped == raw for raw in detected_raw_set
            )
            marker = "DETECTED as heading" if was_detected else "NOT detected as heading"
            print(f"  line {i:4d} [{marker}] (len={len(stripped)}): {stripped!r}")

    if args.full_text:
        print("\n" + "=" * 100)
        print("FULL EXTRACTED TEXT")
        print("=" * 100)
        print(text)


if __name__ == "__main__":
    main()