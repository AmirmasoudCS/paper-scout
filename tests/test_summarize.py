"""
Tests for paper_scout.summarize.summarizer (Phase 5).

All tests here mock OllamaClient.generate_small directly rather than
hitting a live server — summarizer.py's job is JSON parsing / validation
/ graceful degradation, which is independent of whether the model
itself is reachable (that's already covered by test_llm.py). There's
one live smoke test marked @pytest.mark.ollama that exercises the real
qwen3.5:9b end to end.
"""

from __future__ import annotations

import json

import pytest

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.summarize.summarizer import summarize_paper, summarize_papers
from paper_scout.utils.models import ExtractedSections, Paper, SourceName

SAMPLE_CONFIG = {
    "llm": {
        "provider": "ollama",
        "small_model": {"name": "qwen3.5:9b", "temperature": 0.3, "max_tokens": 512},
        "large_model": {"name": "gemma4:e4b", "temperature": 0.5, "max_tokens": 1500},
        "timeout_seconds": 120,
    }
}

VALID_SUMMARY_JSON = json.dumps(
    {
        "problem": "Free-form LLM future-work ideation tends to be generic.",
        "method": "Ground ideation in extracted Limitations/Future Work sections via RAG.",
        "key_result": "Grounded ideation is rated more specific and actionable.",
        "stated_limitations": "Only evaluated on English-language CS papers.",
    }
)


def _sample_paper(title: str = "Grounded Future-Work Ideation") -> Paper:
    return Paper(
        title=title,
        authors=["A. Researcher"],
        abstract="We study how to ground LLM-generated future-work ideas in extracted paper text.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
        extracted_sections=ExtractedSections(
            conclusion="Our method outperforms free-form brainstorming baselines.",
            limitations="We only evaluate on English-language CS papers.",
        ),
    )


class _StubClient:
    """Minimal stand-in for OllamaClient.generate_small, avoids monkeypatching internals."""

    def __init__(self, response: str | None):
        self._response = response
        self.calls: list[tuple[str, str | None, bool]] = []

    def generate_small(self, prompt, system=None, json_mode=False):
        self.calls.append((prompt, system, json_mode))
        return self._response


# ── summarize_paper: happy path ──────────────────────────────────────


def test_summarize_paper_returns_populated_summary_on_valid_json():
    paper = _sample_paper()
    client = _StubClient(VALID_SUMMARY_JSON)

    summary = summarize_paper(paper, client)

    assert summary is not None
    assert summary.problem == "Free-form LLM future-work ideation tends to be generic."
    assert summary.method.startswith("Ground ideation")
    assert summary.stated_limitations == "Only evaluated on English-language CS papers."


def test_summarize_paper_calls_client_with_json_mode():
    paper = _sample_paper()
    client = _StubClient(VALID_SUMMARY_JSON)

    summarize_paper(paper, client)

    assert len(client.calls) == 1
    prompt, system, json_mode = client.calls[0]
    assert json_mode is True
    assert paper.title in prompt
    assert system is not None


def test_summarize_paper_handles_stated_limitations_null():
    data = json.loads(VALID_SUMMARY_JSON)
    data["stated_limitations"] = None
    client = _StubClient(json.dumps(data))

    summary = summarize_paper(_sample_paper(), client)

    assert summary is not None
    assert summary.stated_limitations is None


def test_summarize_paper_strips_markdown_fences():
    fenced = f"```json\n{VALID_SUMMARY_JSON}\n```"
    client = _StubClient(fenced)

    summary = summarize_paper(_sample_paper(), client)

    assert summary is not None
    assert summary.problem == "Free-form LLM future-work ideation tends to be generic."


# ── summarize_paper: graceful degradation ────────────────────────────


def test_summarize_paper_extracts_json_from_surrounding_prose():
    """Regression test for ollama/ollama#14645: format='json' can be silently
    ignored on thinking-capable models once think=False is set, so the model
    may wrap its JSON in prose despite json_mode. Parser should recover it."""
    wrapped = f"Sure, here is the summary:\n\n{VALID_SUMMARY_JSON}\n\nLet me know if you need anything else!"
    client = _StubClient(wrapped)

    summary = summarize_paper(_sample_paper(), client)

    assert summary is not None
    assert summary.problem == "Free-form LLM future-work ideation tends to be generic."


def test_summarize_paper_returns_none_when_model_unreachable():
    client = _StubClient(None)  # simulates OllamaClient.generate_small returning None

    summary = summarize_paper(_sample_paper(), client)

    assert summary is None


def test_summarize_paper_returns_none_on_invalid_json():
    client = _StubClient("this is not json at all")

    summary = summarize_paper(_sample_paper(), client)

    assert summary is None


def test_summarize_paper_returns_none_on_missing_required_keys():
    incomplete = json.dumps({"problem": "Something.", "method": "Something else."})
    # missing "key_result"
    client = _StubClient(incomplete)

    summary = summarize_paper(_sample_paper(), client)

    assert summary is None


def test_summarize_paper_returns_none_when_json_is_not_an_object():
    client = _StubClient(json.dumps(["not", "an", "object"]))

    summary = summarize_paper(_sample_paper(), client)

    assert summary is None


# ── summarize_papers: batch behavior ─────────────────────────────────


def test_summarize_papers_populates_summary_in_place():
    papers = [_sample_paper("Paper A"), _sample_paper("Paper B")]
    client = _StubClient(VALID_SUMMARY_JSON)

    result = summarize_papers(papers, client)

    assert result is papers  # same list, mutated in place
    assert all(p.summary is not None for p in papers)


def test_summarize_papers_one_failure_does_not_block_others():
    good_client_responses = [VALID_SUMMARY_JSON, "not json", VALID_SUMMARY_JSON]

    class SequencedStubClient:
        def __init__(self, responses):
            self._responses = iter(responses)

        def generate_small(self, prompt, system=None, json_mode=False):
            return next(self._responses)

    papers = [_sample_paper("Paper A"), _sample_paper("Paper B"), _sample_paper("Paper C")]
    client = SequencedStubClient(good_client_responses)

    summarize_papers(papers, client)

    assert papers[0].summary is not None
    assert papers[1].summary is None  # the failed one
    assert papers[2].summary is not None


def test_summarize_papers_empty_list_returns_empty_list():
    result = summarize_papers([], _StubClient(VALID_SUMMARY_JSON))
    assert result == []


# ── Live smoke test ───────────────────────────────────────────────────


@pytest.mark.ollama
def test_live_summarize_paper_roundtrip():
    """
    Live end-to-end test: real qwen3.5:9b summarizing a real paper-like
    input. Skipped (not failed) if Ollama/the model isn't available.
    """
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    if not client.is_available():
        pytest.skip("Ollama server not reachable at localhost:11434")

    verified = client.verify_configured_models()
    if not verified["small"]:
        pytest.skip("qwen3.5:9b not pulled locally")

    paper = Paper(
        title="Attention Is All You Need",
        authors=["A. Vaswani"],
        abstract=(
            "We propose the Transformer, a model architecture based solely on attention "
            "mechanisms, dispensing with recurrence and convolutions entirely."
        ),
        source=SourceName.ARXIV,
        arxiv_id="1706.03762",
    )

    summary = summarize_paper(paper, client)

    assert summary is not None
    assert len(summary.problem) > 0
    assert len(summary.method) > 0
    assert len(summary.key_result) > 0