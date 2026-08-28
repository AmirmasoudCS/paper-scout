"""
paper_scout.synthesize.future_work

Phase 6b — the core payoff of the whole project: generates future-work
directions grounded in papers' own extracted Limitations/Future Work
text (RAG-style), rather than free LLM brainstorming. This is what the
project's design principles doc calls out as critical for keeping
7-14B model output useful instead of generic.

Enforces the grounding requirement in code, not just in the prompt:
if no paper in the batch has any extracted Limitations/Future Work
text, we refuse to generate ideas at all rather than let the large
model fall back to ungrounded brainstorming. That's a deliberate
product decision, not just an error case.
"""

from __future__ import annotations

import logging
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_future_work_prompt
from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)

_MIN_VALID_FUTURE_WORK_CHARS = 100


def _has_grounding_text(paper: Paper) -> bool:
    sections = paper.extracted_sections
    if sections is None:
        return False
    return bool(sections.limitations) or bool(sections.future_work)


def generate_future_work_ideas(
    papers: list[Paper],
    cross_paper_synthesis: str,
    client: OllamaClient,
) -> Optional[str]:
    """
    Generate future-work directions grounded in papers' extracted
    Limitations/Future Work sections plus the cross-paper synthesis.

    Returns None (never raises) if:
      - cross_paper_synthesis is empty (nothing to build on)
      - NO paper has any extracted limitations/future_work text — this is
        a deliberate refusal, not just an error: ungrounded ideation from
        the large model defeats the whole point of this phase
      - the LLM is unreachable or returns a suspiciously short response
    """
    if not cross_paper_synthesis or not cross_paper_synthesis.strip():
        logger.warning("Empty cross_paper_synthesis passed in — skipping future-work ideation")
        return None

    grounded_papers = [p for p in papers if _has_grounding_text(p)]
    if not grounded_papers:
        logger.warning(
            "No paper has extracted Limitations/Future Work text (%d papers checked) — "
            "refusing to generate future-work ideas rather than fall back to "
            "ungrounded brainstorming. Check that Phase 3 ingestion ran successfully.",
            len(papers),
        )
        return None

    system, user = build_future_work_prompt(papers, cross_paper_synthesis)
    result = client.generate_large(user, system=system)

    if result is None:
        logger.warning("No response from large model during future-work ideation")
        return None

    result = result.strip()
    if len(result) < _MIN_VALID_FUTURE_WORK_CHARS:
        logger.warning(
            "Future-work ideation response looked too short to be useful "
            "(%d chars) — treating as a failure: %r",
            len(result),
            result,
        )
        return None

    logger.info(
        "Generated future-work ideas grounded in %d/%d papers with extracted sections (%d chars)",
        len(grounded_papers),
        len(papers),
        len(result),
    )
    return result