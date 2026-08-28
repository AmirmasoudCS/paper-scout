"""
scripts/recheck_extraction.py

Ad-hoc manual check (not a pytest test) — re-runs section extraction
against the real PDFs already sitting in the local cache (from the
"Cultural reasoning of LLMs for resource constrained languages" run
that surfaced the two-column bug) and reports, per PDF:

  - whether text extraction succeeded at all
  - which target sections were found vs missing
  - a short preview of the found limitations/future_work text, so you
    can eyeball whether it looks like real recovered prose or garbage

Run from the repo root:

    python scripts/recheck_extraction.py
    python scripts/recheck_extraction.py --cache-dir outputs/pdf_cache
    python scripts/recheck_extraction.py --preview-chars 400

This does not hit the network — it only reads whatever .pdf files are
already in the cache dir. If the cache is empty, re-run the pipeline
once (with VPN on, per the usual ISP issue) to repopulate it first.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from paper_scout.ingestion.section_extract import extract_sections

TARGET_SECTIONS = ["abstract", "conclusion", "limitations", "future work"]


def _preview(text: str | None, chars: int) -> str:
    if not text:
        return "(none)"
    snippet = " ".join(text.split())[:chars]
    suffix = "..." if len(text) > chars else ""
    return snippet + suffix


def recheck(cache_dir: Path, preview_chars: int) -> None:
    pdfs = sorted(cache_dir.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {cache_dir}. Run the pipeline once to populate the cache.")
        return

    print(f"Found {len(pdfs)} cached PDF(s) in {cache_dir}\n")

    found_counts = {"abstract": 0, "conclusion": 0, "limitations": 0, "future_work": 0}
    total = len(pdfs)

    for pdf_path in pdfs:
        sections, full_text_available = extract_sections(pdf_path, TARGET_SECTIONS)

        print("=" * 100)
        print(pdf_path.name)
        print(f"  full_text_available: {full_text_available}")

        for field in ("abstract", "conclusion", "limitations", "future_work"):
            value = getattr(sections, field)
            status = "FOUND" if value else "missing"
            if value:
                found_counts[field] += 1
            print(f"  {field:12s}: {status}")

        if sections.limitations:
            print(f"    limitations preview : {_preview(sections.limitations, preview_chars)}")
        if sections.future_work:
            print(f"    future_work preview : {_preview(sections.future_work, preview_chars)}")
        print()

    print("=" * 100)
    print("SUMMARY")
    for field, count in found_counts.items():
        pct = (count / total * 100) if total else 0.0
        print(f"  {field:12s}: {count}/{total} papers ({pct:.0f}%)")

    grounded = sum(
        1
        for pdf_path in pdfs
        for sections, _ in [extract_sections(pdf_path, TARGET_SECTIONS)]
        if sections.limitations or sections.future_work
    )
    print(f"\n  Papers with SOME grounding text (limitations OR future_work): {grounded}/{total}")
    print("  (future_work ideation only runs at all if this number is > 0 for the run)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("outputs/pdf_cache"),
        help="Directory containing already-downloaded PDFs (default: outputs/pdf_cache)",
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=300,
        help="How many characters of limitations/future_work text to preview per paper",
    )
    args = parser.parse_args()

    if not args.cache_dir.exists():
        print(f"Cache dir does not exist: {args.cache_dir}")
        return

    recheck(args.cache_dir, args.preview_chars)


if __name__ == "__main__":
    main()