"""
Tests for paper_scout.qa.history — sliding-window conversation memory.

Mocks OllamaClient.generate_small directly, same pattern as
test_query_refine.py, so no live Ollama server is needed.
"""

from __future__ import annotations

from paper_scout.qa.history import build_conversation_context, _RECENT_WINDOW


class _StubClient:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def generate_small(self, prompt, system=None):
        self.calls.append((prompt, system))
        return self._response


def _turn(i):
    return {"question": f"question {i}", "answer": f"answer {i}"}


def _history(n_turns, summary=None, summarized_through=0):
    return {
        "turns": [_turn(i) for i in range(n_turns)],
        "summary": summary,
        "summarized_through": summarized_through,
    }


def test_returns_all_turns_verbatim_when_under_window():
    history = _history(3)
    client = _StubClient("should not be called")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert summary is None
    assert recent_turns == history["turns"]
    assert client.calls == []  # no summarization needed
    assert updated_history == history


def test_returns_all_turns_verbatim_when_exactly_at_window():
    history = _history(_RECENT_WINDOW)
    client = _StubClient("should not be called")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert len(recent_turns) == _RECENT_WINDOW
    assert client.calls == []


def test_summarizes_older_turns_past_the_window():
    history = _history(_RECENT_WINDOW + 3)  # 3 turns fall outside the window
    client = _StubClient("Summary of the first 3 turns.")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert summary == "Summary of the first 3 turns."
    assert len(recent_turns) == _RECENT_WINDOW
    assert recent_turns == history["turns"][-_RECENT_WINDOW:]
    assert len(client.calls) == 1
    assert updated_history["summarized_through"] == 3
    assert updated_history["summary"] == "Summary of the first 3 turns."


def test_only_summarizes_turns_not_already_covered():
    """3 older turns already summarized (summarized_through=3); one more
    turn has since fallen out of the window — only that one new turn
    should be sent to the summarizer, not all 4."""
    history = _history(_RECENT_WINDOW + 4, summary="Prior summary.", summarized_through=3)
    client = _StubClient("Updated summary.")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert len(client.calls) == 1
    prompt, system = client.calls[0]
    # only the 4th older turn ("question 3") should appear as new content
    assert "question 3" in prompt
    assert "question 0" not in prompt  # already covered, shouldn't be resent
    assert updated_history["summarized_through"] == 4


def test_no_summarization_call_when_nothing_new_to_summarize():
    """All older turns already covered by summarized_through — should
    not call the model again."""
    history = _history(_RECENT_WINDOW + 2, summary="Already up to date.", summarized_through=2)
    client = _StubClient("should not be called")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert client.calls == []
    assert summary == "Already up to date."
    assert updated_history == history


def test_falls_back_gracefully_when_summarization_fails():
    history = _history(_RECENT_WINDOW + 2)
    client = _StubClient(None)  # simulates model unreachable

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    assert summary is None  # no summary produced
    assert len(recent_turns) == _RECENT_WINDOW  # recent window still works
    assert updated_history == history  # unchanged — will retry next call


def test_recent_turns_always_excludes_summarized_ones():
    history = _history(_RECENT_WINDOW + 10)
    client = _StubClient("summary text")

    summary, recent_turns, updated_history = build_conversation_context(history, client)

    recent_questions = {t["question"] for t in recent_turns}
    assert "question 0" not in recent_questions  # oldest turn must not leak into recent window
    assert f"question {_RECENT_WINDOW + 9}" in recent_questions  # newest turn must be present