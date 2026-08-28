"""
paper_scout.synthesize.cross_paper

Phase 6a — synthesizes themes, agreements, and contradictions across a
set of already-summarized papers, using the large local model
(gemma4:e4b) via OllamaClient.

Unlike Phase 5's per-paper summarization, this step produces free-form
prose rather than structured JSON, so there's no schema to validate
against — validation here is limited to "did we get something
non-trivial back", with the real quality control happening one step
downstream in future_work.py's grounding requirement.
"""

from __future__ import annotations

import logging
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_cross_paper_synthesis_prompt
from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)

_MIN_VALID_SYNTHESIS_CHARS = 100


def synthesize_cross_paper(
    papers: list[Paper],
    query: str,
    client: OllamaClient,
) -> Optional[str]:
    """
    Produce a cross-paper synthesis (themes / agreements / contradictions /
    gaps) across all papers in `papers` that have a populated `.summary`
    (Phase 5 output). Papers without a summary are silently excluded —
    the prompt builder already handles this, we just short-circuit here
    if NONE of them qualify, since there'd be nothing to synthesize.

    Returns None (never raises) if there's nothing to synthesize, the
    LLM is unreachable, or the model returns a suspiciously short/empty
    response.
    """
    summarized = [p for p in papers if p.summary is not None]
    if not summarized:
        logger.warning(
            "No summarized papers available for cross-paper synthesis "
            "(got %d papers, 0 with a .summary) — skipping",
            len(papers),
        )
        return None

    system, user = build_cross_paper_synthesis_prompt(summarized, query)
    result = client.generate_large(user, system=system)

    if result is None:
        logger.warning("No response from large model during cross-paper synthesis")
        return None

    result = result.strip()
    if len(result) < _MIN_VALID_SYNTHESIS_CHARS:
        logger.warning(
            "Cross-paper synthesis response looked too short to be useful "
            "(%d chars) — treating as a failure: %r",
            len(result),
            result,
        )
        return None

    logger.info(
        "Produced cross-paper synthesis from %d/%d summarized papers (%d chars)",
        len(summarized),
        len(papers),
        len(result),
    )
    return result