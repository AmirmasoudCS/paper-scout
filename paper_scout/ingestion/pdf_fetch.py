"""
paper_scout.ingestion.pdf_fetch

Downloads a paper's PDF (given Paper.pdf_url) to a local cache directory,
with retry/backoff and graceful degradation — consistent with the
sources/ modules: never raises, returns None on failure.

Caching is keyed on arxiv_id when available, otherwise a hash of the
pdf_url, so repeated pipeline runs against the same paper don't
re-download.
"""

from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path
from typing import Optional

import requests

import shutil

from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_BASE_SECONDS = 2


def _cache_key(paper: Paper) -> str:
    """Stable filename stem for a paper's cached PDF."""
    if paper.arxiv_id:
        return paper.arxiv_id.replace("/", "_")
    url_str = str(paper.pdf_url)
    return hashlib.sha256(url_str.encode("utf-8")).hexdigest()[:16]


def _cache_path(paper: Paper, cache_dir: Path) -> Path:
    return cache_dir / f"{_cache_key(paper)}.pdf"


def fetch_pdf(
    paper: Paper,
    cache_dir: str | Path,
    timeout_seconds: int = 30,
    max_retries: int = _MAX_RETRIES,
) -> Optional[Path]:
    """
    Download `paper.pdf_url` into `cache_dir`, returning the local Path.

    Returns None (never raises) if:
      - paper.pdf_url is not set
      - all retries are exhausted
      - the response isn't actually a PDF

    If the file already exists in the cache, skips the network call
    entirely and returns the cached path immediately.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    if paper.pdf_url is None:
        logger.warning("No pdf_url for paper %r — skipping download", paper.title)
        return None

    dest = _cache_path(paper, cache_dir)
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("Cache hit for %r -> %s", paper.title, dest)
        return dest

    url = str(paper.pdf_url)

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout_seconds,
                headers={"User-Agent": "paper-scout/0.1 (research pipeline)"},
                stream=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            first_chunk = next(response.iter_content(chunk_size=1024), b"")

            if not first_chunk.startswith(b"%PDF") and "pdf" not in content_type.lower():
                logger.warning(
                    "URL for %r did not return a PDF (content-type=%s) — skipping",
                    paper.title,
                    content_type,
                )
                return None

            tmp_path = dest.with_suffix(".pdf.partial")
            with open(tmp_path, "wb") as f:
                f.write(first_chunk)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            tmp_path.rename(dest)
            logger.info("Downloaded %r -> %s", paper.title, dest)
            return dest

        except requests.RequestException as exc:
            wait = _BACKOFF_BASE_SECONDS**attempt
            logger.warning(
                "Attempt %d/%d failed for %r (%s)%s",
                attempt,
                max_retries,
                paper.title,
                exc,
                f" — retrying in {wait}s" if attempt < max_retries else "",
            )
            if attempt < max_retries:
                time.sleep(wait)

    logger.error("Giving up on PDF download for %r after %d attempts", paper.title, max_retries)
    return None


def fetch_pdfs(
    papers: list[Paper],
    cache_dir: str | Path,
    timeout_seconds: int = 30,
) -> dict[str, Optional[Path]]:
    """
    Convenience batch wrapper. Returns a dict keyed by paper.dedupe_key()
    mapping to the local Path (or None on failure). One paper failing
    never stops the batch.
    """
    results: dict[str, Optional[Path]] = {}
    for paper in papers:
        results[paper.dedupe_key()] = fetch_pdf(paper, cache_dir, timeout_seconds)
    return results

