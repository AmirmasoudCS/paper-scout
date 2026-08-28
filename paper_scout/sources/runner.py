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


def fetch_all_sources(query: str, config: dict) -> list[Paper]:
    """
    Run `query` against every enabled source and return the combined,
    not-yet-deduped raw results. One source failing (even at
    construction time) never stops the others.
    """
    fetchers = build_source_fetchers(config)
    max_results = config["search"]["max_papers_per_source"]

    all_papers: list[Paper] = []
    for fetcher in fetchers:
        try:
            results = fetcher.search(query, max_results=max_results)
            logger.info("%s: fetched %d papers", fetcher.name, len(results))
            all_papers.extend(results)
        except Exception as exc:
            logger.error("Source %s raised unexpectedly, skipping it: %s", fetcher.name, exc)
            continue

    return all_papers