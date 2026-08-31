"""
Tests for paper_scout.llm.query_refine.

Mocks the OllamaClient.generate_small call directly, same pattern as
test_synthesize.py's _StubClient — no live Ollama server needed.
"""

from __future__ import annotations

from paper_scout.llm.query_refine import refine_search_query


class _StubClient:
    """Minimal stand-in for OllamaClient.generate_small."""

    def __init__(self, response: str | None):
        self._response = response
        self.calls: list[tuple[str, str | None]] = []

    def generate_small(self, prompt, system=None):
        self.calls.append((prompt, system))
        return self._response


def test_refine_search_query_returns_refined_when_changed():
    client = _StubClient("diffusion models for audio generation")

    result = refine_search_query("difusion modles for audeo genration", client)

    assert result.original == "difusion modles for audeo genration"
    assert result.refined == "diffusion models for audio generation"
    assert result.changed is True
    assert result.error is None
    assert len(client.calls) == 1


def test_refine_search_query_marks_unchanged_when_response_matches_original():
    client = _StubClient("diffusion models for audio")

    result = refine_search_query("diffusion models for audio", client)

    assert result.refined == "diffusion models for audio"
    assert result.changed is False


def test_refine_search_query_is_case_insensitive_for_changed_detection():
    client = _StubClient("Diffusion Models For Audio")

    result = refine_search_query("diffusion models for audio", client)

    assert result.changed is False


def test_refine_search_query_strips_surrounding_quotes():
    client = _StubClient('"diffusion models for audio"')

    result = refine_search_query("diffusion models for audio", client)

    assert result.refined == "diffusion models for audio"


def test_refine_search_query_collapses_whitespace_and_newlines():
    client = _StubClient("diffusion   models\nfor audio")

    result = refine_search_query("diffusion models for audio typo", client)

    assert result.refined == "diffusion models for audio"


def test_refine_search_query_falls_back_when_client_returns_none():
    client = _StubClient(None)

    result = refine_search_query("some query", client)

    assert result.original == "some query"
    assert result.refined is None
    assert result.changed is False
    assert result.error is not None
    assert "reach" in result.error.lower()


def test_refine_search_query_falls_back_on_empty_response():
    client = _StubClient("")

    result = refine_search_query("some query", client)

    assert result.refined is None
    assert result.error is not None


def test_refine_search_query_falls_back_on_suspiciously_long_response():
    client = _StubClient("x " * 500)  # way longer than any reasonable refinement

    result = refine_search_query("short query", client)

    assert result.refined is None
    assert result.error is not None


def test_refine_search_query_strips_leading_and_trailing_whitespace_from_input():
    client = _StubClient("clean query")

    result = refine_search_query("  clean query  ", client)

    assert result.original == "clean query"


def test_refine_search_query_prompt_includes_the_raw_query():
    client = _StubClient("refined text")

    refine_search_query("original raw query", client)

    prompt, system = client.calls[0]
    assert "original raw query" in prompt
    assert system is not None
    assert "spelling" in system.lower()