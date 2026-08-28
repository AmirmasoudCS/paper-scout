"""
scripts/compare_extraction_methods.py

Isolates whether the "first letter of many lines is missing" issue
(e.g. 'Causal' -> 'ausal', 'Methods' -> 'ethods') is:
  (a) a regression introduced by the new blocks-based, column-aware
      extract_text() (e.g. drop-cap glyphs living in a separate block
      that gets filtered out or dropped during re-ordering), or
  (b) a pre-existing PyMuPDF quirk with plain page.get_text("text")
      extraction that was already there before the rewrite.

It runs BOTH methods against the same PDF and diffs which "words that
look like a capitalized word missing its first letter" appear in one
but not the other.

Usage:
    python scripts/compare_extraction_methods.py outputs/pdf_cache/<file>.pdf
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pymupdf

from paper_scout.ingestion.section_extract import extract_text as new_extract_text

# crude heuristic: a lowercase word that, if you prepend a plausible
# capital letter, forms a common word fragment pattern seen in the
# drop-cap bug (starts lowercase but mid-sentence position looks like
# it should start a sentence/heading, i.e. preceded by nothing or by
# a line-start / period+space)
_SUSPECT_WORD_RE = re.compile(r"\b[a-z][a-z]{2,20}\b")

KNOWN_TRUNCATIONS = {
    "ausal": "Causal",
    "ethods": "Methods",
    "ompeting": "Competing",
    "odel": "Model",
    "oefficient": "Coefficient",
    "nteractive": "Interactive",
    "nstructions": "Instructions",
    "ixture": "Mixture",
}


def old_extract_text(pdf_path: str) -> str:
    doc = pymupdf.open(str(pdf_path))
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n".join(pages)


def find_suspects(text: str) -> set[str]:
    found = set()
    lower_text = text
    for truncated in KNOWN_TRUNCATIONS:
        if re.search(rf"\b{truncated}\b", lower_text):
            found.add(truncated)
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path)
    args = parser.parse_args()

    old_text = old_extract_text(str(args.pdf_path))
    new_text = new_extract_text(args.pdf_path)

    print(f"old (plain get_text) length: {len(old_text)} chars")
    print(f"new (blocks-based)   length: {len(new_text) if new_text else 0} chars\n")

    old_suspects = find_suspects(old_text)
    new_suspects = find_suspects(new_text or "")

    print("Known truncation patterns found in OLD extraction:", old_suspects or "(none)")
    print("Known truncation patterns found in NEW extraction:", new_suspects or "(none)")

    only_in_new = new_suspects - old_suspects
    only_in_old = old_suspects - new_suspects
    in_both = old_suspects & new_suspects

    print()
    if only_in_new:
        print(f"REGRESSION SIGNAL: these truncations appear ONLY in the new blocks-based method: {only_in_new}")
        print("  -> the block filter is likely dropping something plain get_text() preserved (e.g. block_type != 0)")
    if only_in_old:
        print(f"These truncations appear ONLY in the old method (new method fixed them): {only_in_old}")
    if in_both:
        print(f"PRE-EXISTING: these truncations appear in BOTH methods, so it predates the rewrite: {in_both}")
    if not (old_suspects or new_suspects):
        print("No known truncation patterns found in either — the specific words checked may not appear in this PDF.")

    # Also show a couple of lines of context for whichever truncations we found, from each method
    for word in sorted(old_suspects | new_suspects):
        print(f"\n--- context for {word!r} ---")
        for label, text in (("OLD", old_text), ("NEW", new_text or "")):
            m = re.search(rf".{{0,40}}\b{word}\b.{{0,40}}", text)
            if m:
                print(f"  [{label}] ...{m.group(0)}...")
            else:
                print(f"  [{label}] not found")


if __name__ == "__main__":
    main()