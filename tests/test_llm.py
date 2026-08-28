"""
Tests for paper_scout.llm (Phase 4).

Prompt-builder tests run with no dependencies at all. OllamaClient tests
are split into:
  - unit tests that monkeypatch `requests` so retry/backoff/error-handling
    logic is verified without needing a running Ollama server
  - one live smoke test marked @pytest.mark.ollama that actually calls a
    local Ollama server, skipped (not failed) if it isn't reachable
"""

from __future__ import annotations

import pytest
import requests

from paper_scout.llm.ollama_client import ModelConfig, OllamaClient
from paper_scout.llm.prompts import (
    build_cross_paper_synthesis_prompt,
    build_future_work_prompt,
    build_summarize_prompt,
)
from paper_scout.utils.models import ExtractedSections, Paper, PaperSummary, SourceName

SAMPLE_CONFIG = {
    "llm": {
        "provider": "ollama",
        "small_model": {"name": "qwen3.5:9b", "temperature": 0.3, "max_tokens": 512},
        "large_model": {"name": "gemma4:e4b", "temperature": 0.5, "max_tokens": 1500},
        "timeout_seconds": 120,
    }
}


def _sample_paper(with_sections: bool = True, with_summary: bool = False) -> Paper:
    paper = Paper(
        title="Grounded Future-Work Ideation for Research Pipelines",
        authors=["A. Researcher"],
        abstract="We study how to ground LLM-generated future-work ideas in extracted paper text.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
    )
    if with_sections:
        paper.extracted_sections = ExtractedSections(
            conclusion="Our method outperforms free-form brainstorming baselines.",
            limitations="We only evaluate on English-language CS papers.",
            future_work="Future work should extend to other languages and domains.",
        )
    if with_summary:
        paper.summary = PaperSummary(
            problem="Free-form LLM brainstorming for future work tends to be generic.",
            method="Ground ideation in extracted Limitations/Future Work sections via RAG.",
            key_result="Grounded ideation is rated more specific and actionable by reviewers.",
            stated_limitations="Only evaluated on English CS papers.",
        )
    return paper


# ── Prompt builders ──────────────────────────────────────────────────


def test_build_summarize_prompt_includes_paper_content():
    paper = _sample_paper(with_sections=True)
    system, user = build_summarize_prompt(paper)

    assert "JSON" in system
    assert paper.title in user
    assert paper.abstract in user
    assert "outperforms free-form brainstorming baselines" in user
    assert "we only evaluate on english-language cs papers" in user.lower()


def test_build_summarize_prompt_handles_missing_sections():
    paper = _sample_paper(with_sections=False)
    system, user = build_summarize_prompt(paper)

    assert paper.title in user
    assert "(not available)" in user  # graceful placeholder, no crash


def test_build_cross_paper_synthesis_prompt_includes_all_summarized_papers():
    papers = [_sample_paper(with_summary=True) for _ in range(3)]
    system, user = build_cross_paper_synthesis_prompt(papers, query="future work ideation")

    assert "future work ideation" in user
    assert user.count("[1]") >= 1
    assert user.count("[2]") >= 1
    assert user.count("[3]") >= 1
    assert "Free-form LLM brainstorming" in user


def test_build_cross_paper_synthesis_prompt_skips_unsummarized_papers():
    papers = [_sample_paper(with_summary=True), _sample_paper(with_summary=False)]
    system, user = build_cross_paper_synthesis_prompt(papers, query="test query")

    assert "no summarized papers" not in user  # at least one WAS summarized
    assert user.count("Problem:") == 1  # only the summarized one appears


def test_build_future_work_prompt_grounds_in_extracted_sections():
    papers = [_sample_paper(with_sections=True)]
    system, user = build_future_work_prompt(papers, cross_paper_synthesis="Papers focus on grounding.")

    assert "grounded" in system.lower()
    assert "Papers focus on grounding." in user
    assert "extend to other languages" in user


def test_build_future_work_prompt_handles_no_extracted_sections():
    papers = [_sample_paper(with_sections=False)]
    system, user = build_future_work_prompt(papers, cross_paper_synthesis="No grounding available.")

    assert "no extracted limitations/future work available" in user


# ── OllamaClient: config parsing ─────────────────────────────────────


def test_from_config_parses_both_tiers():
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    assert client._models["small"].name == "qwen3.5:9b"
    assert client._models["small"].temperature == 0.3
    assert client._models["large"].name == "gemma4:e4b"
    assert client._models["large"].max_tokens == 1500
    assert client.timeout_seconds == 120


# ── OllamaClient: health checks (mocked) ─────────────────────────────


def test_is_available_returns_false_on_connection_error(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "get", raise_connection_error)
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    assert client.is_available() is False


def test_list_models_returns_empty_list_on_failure(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "get", raise_connection_error)
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    assert client.list_models() == []


def test_verify_configured_models_flags_missing_models(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"models": [{"name": "llama3:8b"}]}  # neither configured model present

    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse())
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.verify_configured_models()
    assert result["small"] is False
    assert result["large"] is False


def test_verify_configured_models_finds_present_models(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"models": [{"name": "qwen3.5:9b"}, {"name": "gemma4:e4b"}]}

    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResponse())
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.verify_configured_models()
    assert result["small"] is True
    assert result["large"] is True


# ── OllamaClient: generation (mocked) ────────────────────────────────


def test_generate_small_returns_content_on_success(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "This is a summary."}}

    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json))
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.generate_small("Summarize this.")
    assert result == "This is a summary."
    assert calls[0][1]["model"] == "qwen3.5:9b"
    assert calls[0][1]["messages"][-1] == {"role": "user", "content": "Summarize this."}


def test_generate_large_uses_large_model_config(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "Synthesis text."}}

    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.generate_large("Synthesize these papers.", system="You are an analyst.")
    assert result == "Synthesis text."
    assert calls[0]["model"] == "gemma4:e4b"
    assert calls[0]["messages"][0] == {"role": "system", "content": "You are an analyst."}


def test_generate_sets_json_format_when_requested(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": '{"key": "value"}'}}

    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    client.generate_small("Give me JSON.", json_mode=True)
    assert calls[0]["format"] == "json"


def test_generate_retries_then_returns_none_on_repeated_failure(monkeypatch):
    call_count = {"n": 0}

    def always_fail(url, json, timeout):
        call_count["n"] += 1
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "post", always_fail)
    monkeypatch.setattr("time.sleep", lambda seconds: None)  # skip real backoff delay in tests

    client = OllamaClient.from_config(SAMPLE_CONFIG)
    result = client.generate_small("This will fail.")

    assert result is None
    assert call_count["n"] == 3  # default max_retries


def test_generate_returns_none_on_empty_response_content(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": ""}}

    monkeypatch.setattr(requests, "post", lambda url, json, timeout: FakeResponse())
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.generate_small("Prompt.")
    assert result is None


def test_generate_returns_none_on_malformed_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("not JSON")

    monkeypatch.setattr(requests, "post", lambda url, json, timeout: FakeResponse())
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    result = client.generate_small("Prompt.")
    assert result is None


# ── OllamaClient: live smoke test ────────────────────────────────────


@pytest.mark.ollama
def test_live_small_model_roundtrip():
    """
    Live test against a real local Ollama server with qwen3.5:9b pulled.
    Skipped (not failed) if Ollama isn't running or the model isn't
    available, per the project's graceful-degradation philosophy.
    """
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    if not client.is_available():
        pytest.skip("Ollama server not reachable at localhost:11434")

    verified = client.verify_configured_models()
    if not verified["small"]:
        pytest.skip("qwen3.5:9b not pulled locally")

    result = client.generate_small("Reply with exactly one word: hello")
    assert result is not None
    assert len(result.strip()) > 0