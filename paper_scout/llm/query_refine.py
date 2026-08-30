"""
paper_scout.llm.query_refine

Optional pre-pipeline step: uses the small model to fix spelling and
lightly tighten a user's raw search query before it's sent to the
paper sources. Entirely synchronous — a single small-model call is
fast enough to run before a job even starts — and never silently
swaps the user's query out from under them. Callers are expected to
show both the original and refined text and let the user confirm,
edit, or cancel before it's actually used.

Degrades gracefully like the rest of the project: on any failure
(unreachable Ollama, empty/garbage response), returns the ORIGINAL
query with refined=None and a human-readable error, rather than
raising or guessing at a fix.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_query_refine_prompt

logger = logging.getLogger(__name__)

# If the model's response is wildly longer than the input, or empty,
# it's more likely to be a broken/garbage response than a real
# refinement — better to fall back than trust it blindly.
_MAX_REFINED_LENGTH_RATIO = 4
_MIN_REFINED_CHARS = 3


@dataclass
class QueryRefinement:
    original: str
    refined: Optional[str]  # None if refinement failed or looked unreliable
    changed: bool  # True if refined differs from original (only meaningful when refined is set)
    error: Optional[str] = None


def refine_search_query(raw_query: str, client: OllamaClient) -> QueryRefinement:
    """
    Ask the small model to fix spelling/grammar and lightly tighten
    raw_query into better search phrasing. Never raises.
    """
    raw_query = raw_query.strip()

    system, user = build_query_refine_prompt(raw_query)
    result = client.generate_small(user, system=system)

    if result is None:
        logger.warning("Query refinement failed (no response) for %r", raw_query)
        return QueryRefinement(
            original=raw_query,
            refined=None,
            changed=False,
            error="Could not reach the small model to refine the query.",
        )

    refined = result.strip().strip('"').strip("'")
    refined = " ".join(refined.split())  # collapse to a single line, defensively

    if len(refined) < _MIN_REFINED_CHARS or len(refined) > len(raw_query) * _MAX_REFINED_LENGTH_RATIO:
        logger.warning(
            "Query refinement response looked unreliable for %r -> %r — falling back to original",
            raw_query,
            refined,
        )
        return QueryRefinement(
            original=raw_query,
            refined=None,
            changed=False,
            error="The model's response didn't look reliable, so your original query was kept.",
        )

    return QueryRefinement(
        original=raw_query,
        refined=refined,
        changed=refined.lower() != raw_query.lower(),
    )