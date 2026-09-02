"""
paper_scout.qa.history

Sliding-window conversation memory for the report Q&A assistant. The
last _RECENT_WINDOW turns are always fed to the model verbatim; any
older turns are folded once into a running summary via the small
model, so the summarization cost stays flat as a conversation grows
instead of scaling with its length.

This module only computes context to feed into a question — it does
not read/write qa_history.json itself (see web/runs.py for that) and
it does not answer questions (see qa/answer.py). Keeping these split
mirrors how synthesize/future_work.py keeps its two tiers separate.
"""

from __future__ import annotations

import logging
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_conversation_summary_prompt

logger = logging.getLogger(__name__)

_RECENT_WINDOW = 5  # last N turns fed verbatim; matches the project's chosen window size


def build_conversation_context(
    history: dict, client: OllamaClient
) -> tuple[Optional[str], list[dict], dict]:
    """
    Given a run's stored history dict (shape: {"turns": [...],
    "summary": str|None, "summarized_through": int}), returns:

      (conversation_summary, recent_turns, updated_history)

    - conversation_summary / recent_turns are what should be passed to
      build_qa_prompt() for the upcoming question.
    - updated_history is the history dict to persist afterward (via
      web/runs.py's append_qa_turn), with "summary" and
      "summarized_through" advanced if new turns were folded in this
      call. Callers should always persist updated_history, even if
      nothing changed, to keep call sites simple.

    Never raises — if summarization fails (model unreachable, etc.),
    older turns are simply left un-summarized and omitted from context
    this time; the next call will retry them. The recent-turns window
    is unaffected either way, so answers degrade gracefully rather
    than failing outright.
    """
    turns = history.get("turns", [])
    summary = history.get("summary")
    summarized_through = history.get("summarized_through", 0)

    if len(turns) <= _RECENT_WINDOW:
        # Nothing has fallen out of the window yet — nothing to summarize.
        recent_turns = turns
        return summary, recent_turns, history

    recent_turns = turns[-_RECENT_WINDOW:]
    older_turns = turns[:-_RECENT_WINDOW]
    not_yet_summarized = older_turns[summarized_through:]

    if not not_yet_summarized:
        # Older turns exist but were already folded into `summary` in a
        # previous call — nothing new to do.
        return summary, recent_turns, history

    system, user = build_conversation_summary_prompt(summary, not_yet_summarized)
    updated_summary = client.generate_small(user, system=system)

    if updated_summary is None:
        logger.warning(
            "Conversation summarization failed — proceeding with recent turns only "
            "(%d older turn(s) remain un-summarized for now)",
            len(not_yet_summarized),
        )
        return summary, recent_turns, history

    updated_history = {
        **history,
        "turns": turns,
        "summary": updated_summary.strip(),
        "summarized_through": len(older_turns),
    }
    return updated_history["summary"], recent_turns, updated_history