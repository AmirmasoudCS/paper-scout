"""
paper_scout.qa.answer

Answers a question grounded strictly in one run's report text — the
same "prove it from the source" discipline the rest of the project
applies to future-work ideation, here applied to interactive Q&A.
Never uses outside knowledge; if the report doesn't contain the
answer, the model is instructed to say so rather than guess.

Optional conversation_summary/recent_turns let the model resolve
references to earlier questions ("the second one") without treating
prior answers as report content — see qa/history.py for how these are
produced from a run's stored Q&A history.
"""

from __future__ import annotations

import logging
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_qa_prompt

logger = logging.getLogger(__name__)

_MIN_VALID_ANSWER_CHARS = 3


def answer_question(
    report_markdown: str,
    question: str,
    client: OllamaClient,
    conversation_summary: Optional[str] = None,
    recent_turns: Optional[list[dict]] = None,
) -> str:
    """Never raises — returns a user-facing fallback string if the
    model is unreachable or returns something unusably short."""
    system, user = build_qa_prompt(
        report_markdown, question, conversation_summary=conversation_summary, recent_turns=recent_turns
    )
    result = client.generate_large(user, system=system)

    if result is None or len(result.strip()) < _MIN_VALID_ANSWER_CHARS:
        logger.warning("Q&A failed or returned an unusably short response for %r", question)
        return "Sorry, I couldn't reach the model to answer that — please try again."

    return result.strip()