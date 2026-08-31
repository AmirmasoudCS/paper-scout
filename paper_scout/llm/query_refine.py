"""
paper_scout.llm.query_refine

Optional pre-pipeline step: uses the small model to fix spelling and
lightly tighten a user's raw search query before it is sent to the
paper sources.

The refinement is intentionally conservative: it should improve
spelling, grammar, capitalization, and academic phrasing while
preserving the user's original research intent.

Degrades gracefully like the rest of the project: on any failure
(unreachable Ollama, empty/garbage response), returns the ORIGINAL
query with refined=None and a human-readable error rather than
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
# it is more likely to be a broken/garbage response than a useful
# refinement.
_MAX_REFINED_LENGTH_RATIO = 4
_MIN_REFINED_CHARS = 3


@dataclass
class QueryRefinement:
    original: str
    refined: Optional[str]
    changed: bool
    error: Optional[str] = None


def refine_search_query(
    raw_query: str,
    client: OllamaClient,
) -> QueryRefinement:
    """
    Ask the small model to improve a raw research search query.

    The model is allowed to correct:
    - spelling
    - grammar
    - capitalization
    - awkward phrasing
    - common academic terminology

    It should preserve:
    - the original research topic
    - important technical terms
    - acronyms
    - requested constraints
    - the overall scope of the query

    Never raises. If refinement fails or produces an obviously
    unreliable response, the caller can fall back to the original
    query.
    """

    raw_query = raw_query.strip()

    system, user = build_query_refine_prompt(raw_query)

    try:
        result = client.generate_small(user, system=system)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Query refinement failed for %r", raw_query)

        return QueryRefinement(
            original=raw_query,
            refined=None,
            changed=False,
            error=f"Could not refine the query: {exc}",
        )

    if result is None:
        logger.warning(
            "Query refinement failed (no response) for %r",
            raw_query,
        )

        return QueryRefinement(
            original=raw_query,
            refined=None,
            changed=False,
            error="Could not reach the small model to refine the query.",
        )

    # Defensively clean up common formatting mistakes from the model.
    refined = result.strip()

    # Remove surrounding quotes if the model ignored the instruction
    # and returned something like:
    # "diffusion models for audio generation"
    if (
        len(refined) >= 2
        and refined[0] == refined[-1]
        and refined[0] in {"'", '"'}
    ):
        refined = refined[1:-1].strip()

    # Force the result onto a single line.
    refined = " ".join(refined.split())

    # Basic reliability checks.
    if (
        len(refined) < _MIN_REFINED_CHARS
        or len(refined) > len(raw_query) * _MAX_REFINED_LENGTH_RATIO
    ):
        logger.warning(
            "Query refinement response looked unreliable for %r -> %r",
            raw_query,
            refined,
        )

        return QueryRefinement(
            original=raw_query,
            refined=None,
            changed=False,
            error=(
                "The model's response didn't look reliable, "
                "so your original query was kept."
            ),
        )

    return QueryRefinement(
        original=raw_query,
        refined=refined,
        changed=refined.lower() != raw_query.lower(),
    )