"""
paper_scout.sources.runner

Builds the enabled PaperSource fetchers from config and runs a query
against all of them, combining the raw (not yet deduped/ranked) results.
Each individual source fetcher already degrades gracefully (returns []
rather than raising) per the PaperSource contract, but this wraps each
call in an extra try/except anyway — a source's __init__ (e.g. a bad
API key) can raise before search() is ever reached, and one
misconfigured source should never take down the others.
"""

from __future__ import annotations

import logging
import os

from paper_scout.sources.arxiv_source import ArxivSource
from paper_scout.sources.base import PaperSource
from paper_scout.sources.huggingface_papers_source import HuggingFacePapersSource
from paper_scout.sources.semantic_scholar_source import SemanticScholarSource
from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)


def build_source_fetchers(config: dict) -> list[PaperSource]:
    sources_cfg = config["sources"]
    fetchers: list[PaperSource] = []

    if sources_cfg.get("arxiv", {}).get("enabled", True):
        fetchers.append(ArxivSource(categories=sources_cfg["arxiv"].get("categories") or []))

    if sources_cfg.get("semantic_scholar", {}).get("enabled", True):
        api_key = sources_cfg["semantic_scholar"].get("api_key") or os.environ.get(
            "SEMANTIC_SCHOLAR_API_KEY"
        )
        fetchers.append(SemanticScholarSource(api_key=api_key))

    if sources_cfg.get("huggingface_papers", {}).get("enabled", True):
        fetchers.append(HuggingFacePapersSource())

    return fetchers


def fetch_all_sources_with_stats(query: str, config: dict) -> tuple[list[Paper], dict]:
    """
    Same as fetch_all_sources(), but also returns per-source stats for
    run metadata: how many papers each enabled source found, and the
    error message if a source failed entirely (including construction-
    time failures, e.g. a bad API key). Kept as a separate function so
    fetch_all_sources() and its existing callers/tests are unaffected.
    """
    fetchers = build_source_fetchers(config)
    max_results = config["search"]["max_papers_per_source"]

    all_papers: list[Paper] = []
    stats: dict[str, dict] = {}

    for fetcher in fetchers:
        try:
            results = fetcher.search(query, max_results=max_results)
            logger.info("%s: fetched %d papers", fetcher.name, len(results))
            all_papers.extend(results)
            stats[fetcher.name] = {"enabled": True, "papers_found": len(results)}
        except Exception as exc:
            logger.error("Source %s raised unexpectedly, skipping it: %s", fetcher.name, exc)
            stats[fetcher.name] = {"enabled": True, "papers_found": 0, "error": str(exc)}
            continue

    sources_cfg = config["sources"]
    for source_name in ("arxiv", "semantic_scholar", "huggingface_papers"):
        if source_name not in stats:
            stats[source_name] = {
                "enabled": sources_cfg.get(source_name, {}).get("enabled", True),
                "papers_found": 0,
            }

    return all_papers, stats


def fetch_all_sources(query: str, config: dict) -> list[Paper]:
    """
    Run `query` against every enabled source and return the combined,
    not-yet-deduped raw results. One source failing (even at
    construction time) never stops the others.
    """
    papers, _stats = fetch_all_sources_with_stats(query, config)
    return papers