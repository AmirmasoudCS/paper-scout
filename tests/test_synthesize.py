"""
Tests for paper_scout.synthesize (Phase 6).

Mocks the OllamaClient large-model call directly, same pattern as
test_summarize.py, so these run without a live Ollama server. One live
smoke test marked @pytest.mark.ollama exercises the real gemma4:e4b
end to end for both cross-paper synthesis and grounded future-work
ideation.
"""

from __future__ import annotations

import pytest

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.summarize.summarizer import summarize_paper
from paper_scout.synthesize.cross_paper import synthesize_cross_paper
from paper_scout.synthesize.future_work import generate_future_work_ideas
from paper_scout.utils.models import ExtractedSections, Paper, PaperSummary, SourceName
from paper_scout.synthesize.future_work import generate_inferred_future_work_ideas

SAMPLE_CONFIG = {
    "llm": {
        "provider": "ollama",
        "small_model": {"name": "qwen3.5:9b", "temperature": 0.3, "max_tokens": 512},
        "large_model": {"name": "gemma4:e4b", "temperature": 0.5, "max_tokens": 1500},
        "timeout_seconds": 120,
    }
}

LONG_SYNTHESIS_TEXT = (
    "Across these papers, a clear methodological split emerges. [1] and [2] both rely on "
    "retrieval-grounded generation to constrain model output, while [3] takes a purely "
    "parametric approach. The papers agree that ungrounded generation tends toward generic "
    "output, but diverge on how tightly retrieval should constrain the final response. A "
    "notable gap: none of these papers evaluate on non-English corpora."
)

LONG_FUTURE_WORK_TEXT = (
    "1. Multilingual grounding — [1] and [2] both note their evaluation is English-only; "
    "extending retrieval-grounded generation to other languages is a natural next step. "
    "2. Tighter retrieval constraints — [3]'s purely parametric approach could be combined "
    "with [1]'s retrieval mechanism to test whether hybrid approaches reduce generic output "
    "further, directly addressing the limitation [3] states in its own future work section."
)


def _summarized_paper(title: str, with_sections: bool = True) -> Paper:
    paper = Paper(
        title=title,
        authors=["A. Researcher"],
        abstract="We study grounded generation for research ideation pipelines.",
        source=SourceName.ARXIV,
        arxiv_id="2401.00001",
    )
    paper.summary = PaperSummary(
        problem="Ungrounded LLM ideation tends to be generic.",
        method="Ground ideation in retrieved paper text via RAG.",
        key_result="Grounded ideation is rated more specific by reviewers.",
    )
    if with_sections:
        paper.extracted_sections = ExtractedSections(
            limitations="We only evaluate on English-language papers.",
            future_work="Future work should extend to other languages.",
        )
    return paper


class _StubClient:
    """Minimal stand-in for OllamaClient.generate_large."""

    def __init__(self, response: str | None):
        self._response = response
        self.calls: list[tuple[str, str | None]] = []

    def generate_large(self, prompt, system=None):
        self.calls.append((prompt, system))
        return self._response


# ── synthesize_cross_paper ───────────────────────────────────────────


def test_synthesize_cross_paper_returns_text_on_success():
    papers = [_summarized_paper("Paper A"), _summarized_paper("Paper B")]
    client = _StubClient(LONG_SYNTHESIS_TEXT)

    result = synthesize_cross_paper(papers, query="retrieval-grounded generation", client=client)

    assert result == LONG_SYNTHESIS_TEXT
    assert len(client.calls) == 1
    prompt, system = client.calls[0]
    assert "retrieval-grounded generation" in prompt


def test_synthesize_cross_paper_returns_none_when_no_papers_summarized():
    unsummarized = Paper(
        title="Unsummarized Paper",
        authors=["A. Researcher"],
        abstract="Some abstract.",
        source=SourceName.ARXIV,
    )
    client = _StubClient(LONG_SYNTHESIS_TEXT)

    result = synthesize_cross_paper([unsummarized], query="test", client=client)

    assert result is None
    assert len(client.calls) == 0  # should short-circuit before calling the LLM


def test_synthesize_cross_paper_returns_none_when_client_fails():
    papers = [_summarized_paper("Paper A")]
    client = _StubClient(None)

    result = synthesize_cross_paper(papers, query="test", client=client)

    assert result is None


def test_synthesize_cross_paper_returns_none_on_too_short_response():
    papers = [_summarized_paper("Paper A")]
    client = _StubClient("Too short.")

    result = synthesize_cross_paper(papers, query="test", client=client)

    assert result is None


def test_synthesize_cross_paper_excludes_unsummarized_papers_from_prompt():
    summarized = _summarized_paper("Summarized Paper")
    unsummarized = Paper(
        title="Should Not Appear",
        authors=[],
        abstract="x",
        source=SourceName.ARXIV,
    )
    client = _StubClient(LONG_SYNTHESIS_TEXT)

    synthesize_cross_paper([summarized, unsummarized], query="test", client=client)

    prompt, _ = client.calls[0]
    assert "Should Not Appear" not in prompt
    assert "Summarized Paper" in prompt


# ── generate_future_work_ideas ───────────────────────────────────────


def test_generate_future_work_ideas_returns_text_on_success():
    papers = [_summarized_paper("Paper A", with_sections=True)]
    client = _StubClient(LONG_FUTURE_WORK_TEXT)

    result = generate_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result == LONG_FUTURE_WORK_TEXT
    prompt, system = client.calls[0]
    assert LONG_SYNTHESIS_TEXT in prompt
    assert "grounded" in system.lower()


def test_generate_future_work_ideas_refuses_when_no_grounding_text():
    """Core design principle: refuse ideation rather than fall back to
    ungrounded brainstorming when no paper has extracted limitations/future work."""
    papers = [_summarized_paper("Paper A", with_sections=False)]
    client = _StubClient(LONG_FUTURE_WORK_TEXT)

    result = generate_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result is None
    assert len(client.calls) == 0  # must short-circuit BEFORE calling the LLM


def test_generate_future_work_ideas_returns_none_on_empty_synthesis():
    papers = [_summarized_paper("Paper A", with_sections=True)]
    client = _StubClient(LONG_FUTURE_WORK_TEXT)

    result = generate_future_work_ideas(papers, "", client)

    assert result is None
    assert len(client.calls) == 0


def test_generate_future_work_ideas_returns_none_when_client_fails():
    papers = [_summarized_paper("Paper A", with_sections=True)]
    client = _StubClient(None)

    result = generate_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result is None


def test_generate_future_work_ideas_returns_none_on_too_short_response():
    papers = [_summarized_paper("Paper A", with_sections=True)]
    client = _StubClient("Too short.")

    result = generate_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result is None


def test_generate_future_work_ideas_grounds_with_at_least_one_qualifying_paper():
    """Only ONE paper needs grounding text — mixed batches should still proceed."""
    grounded = _summarized_paper("Grounded Paper", with_sections=True)
    ungrounded = _summarized_paper("Ungrounded Paper", with_sections=False)
    client = _StubClient(LONG_FUTURE_WORK_TEXT)

    result = generate_future_work_ideas([grounded, ungrounded], LONG_SYNTHESIS_TEXT, client)

    assert result is not None
    assert len(client.calls) == 1


# ── Live smoke test ───────────────────────────────────────────────────


@pytest.mark.ollama
def test_live_synthesis_and_future_work_roundtrip():
    """
    Live end-to-end test against real gemma4:e4b: cross-paper synthesis
    followed by grounded future-work ideation on two small papers.
    Skipped (not failed) if Ollama/the model isn't available.
    """
    client = OllamaClient.from_config(SAMPLE_CONFIG)

    if not client.is_available():
        pytest.skip("Ollama server not reachable at localhost:11434")

    verified = client.verify_configured_models()
    if not verified["large"]:
        pytest.skip("gemma4:e4b not pulled locally")

    papers = [
        Paper(
            title="Attention Is All You Need",
            authors=["A. Vaswani"],
            abstract=(
                "We propose the Transformer, a model architecture based solely on attention "
                "mechanisms, dispensing with recurrence and convolutions entirely."
            ),
            source=SourceName.ARXIV,
            arxiv_id="1706.03762",
            extracted_sections=ExtractedSections(
                limitations="The model requires substantial compute for training on large datasets.",
                future_work="Future work includes extending attention mechanisms to other modalities.",
            ),
        ),
        Paper(
            title="Retrieval-Augmented Generation for Knowledge-Intensive NLP",
            authors=["P. Lewis"],
            abstract=(
                "We introduce retrieval-augmented generation, combining parametric and "
                "non-parametric memory for language generation."
            ),
            source=SourceName.ARXIV,
            arxiv_id="2005.11401",
            extracted_sections=ExtractedSections(
                limitations="Retrieval quality bottlenecks overall generation quality.",
                future_work="Future work should explore end-to-end retriever training.",
            ),
        ),
    ]

    # Populate summaries via the real small model first, same as the real pipeline would.
    for paper in papers:
        summary = summarize_paper(paper, client)
        if summary is not None:
            paper.summary = summary

    if not any(p.summary for p in papers):
        pytest.skip("Small model failed to produce any summaries — cannot test synthesis")

    synthesis = synthesize_cross_paper(papers, query="attention and retrieval methods", client=client)
    assert synthesis is not None
    assert len(synthesis) > 0

    future_work = generate_future_work_ideas(papers, synthesis, client)
    assert future_work is not None
    assert len(future_work) > 0

LONG_INFERRED_TEXT = (
    "[Inferred, not author-stated] Multilingual evaluation — [1]'s method is only evaluated on "
    "English-language papers based on its stated problem framing; extending the evaluation to "
    "other languages is a natural next step given this constraint, though the paper does not "
    "state this itself."
)


def _summary_only_paper(title: str) -> Paper:
    """A paper with a Phase 5 summary but NO extracted Limitations/
    Future Work text — the Tier 2 eligibility case."""
    return _summarized_paper(title, with_sections=False)


def _no_summary_paper(title: str) -> Paper:
    return Paper(
        title=title,
        authors=["A. Researcher"],
        abstract="Some abstract.",
        source=SourceName.ARXIV,
    )


# ── generate_inferred_future_work_ideas (Tier 2) ─────────────────────


def test_generate_inferred_future_work_ideas_returns_text_on_success():
    papers = [_summary_only_paper("Paper A")]
    client = _StubClient(LONG_INFERRED_TEXT)

    result = generate_inferred_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result == LONG_INFERRED_TEXT
    prompt, system = client.calls[0]
    assert "Paper A" in prompt
    assert "inferred" in system.lower()


def test_generate_inferred_future_work_ideas_skips_papers_that_already_have_grounding_text():
    """A paper with real Limitations/Future Work text should go through
    Tier 1 only — it must not also appear in the Tier 2 prompt."""
    grounded = _summarized_paper("Grounded Paper", with_sections=True)
    ungrounded = _summary_only_paper("Ungrounded Paper")
    client = _StubClient(LONG_INFERRED_TEXT)

    generate_inferred_future_work_ideas([grounded, ungrounded], LONG_SYNTHESIS_TEXT, client)

    prompt, _ = client.calls[0]
    assert "Grounded Paper" not in prompt
    assert "Ungrounded Paper" in prompt


def test_generate_inferred_future_work_ideas_returns_none_when_no_eligible_papers():
    """If every paper either already has grounding text or has no
    summary at all, there's nothing for Tier 2 to work with."""
    grounded = _summarized_paper("Grounded Paper", with_sections=True)
    no_summary = _no_summary_paper("No Summary Paper")
    client = _StubClient(LONG_INFERRED_TEXT)

    result = generate_inferred_future_work_ideas([grounded, no_summary], LONG_SYNTHESIS_TEXT, client)

    assert result is None
    assert len(client.calls) == 0


def test_generate_inferred_future_work_ideas_returns_none_on_empty_synthesis():
    papers = [_summary_only_paper("Paper A")]
    client = _StubClient(LONG_INFERRED_TEXT)

    result = generate_inferred_future_work_ideas(papers, "", client)

    assert result is None
    assert len(client.calls) == 0


def test_generate_inferred_future_work_ideas_returns_none_when_client_fails():
    papers = [_summary_only_paper("Paper A")]
    client = _StubClient(None)

    result = generate_inferred_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result is None


def test_generate_inferred_future_work_ideas_returns_none_on_too_short_response():
    papers = [_summary_only_paper("Paper A")]
    client = _StubClient("Too short.")

    result = generate_inferred_future_work_ideas(papers, LONG_SYNTHESIS_TEXT, client)

    assert result is None


def test_tier1_and_tier2_are_independent_and_never_conflated():
    """A mixed batch should produce distinct Tier 1 and Tier 2 outputs
    from two separate calls — this is a design invariant, not just a
    behavior check."""
    grounded = _summarized_paper("Grounded Paper", with_sections=True)
    summary_only = _summary_only_paper("Summary Only Paper")

    tier1_client = _StubClient(LONG_FUTURE_WORK_TEXT)
    tier2_client = _StubClient(LONG_INFERRED_TEXT)

    tier1_result = generate_future_work_ideas([grounded, summary_only], LONG_SYNTHESIS_TEXT, tier1_client)
    tier2_result = generate_inferred_future_work_ideas([grounded, summary_only], LONG_SYNTHESIS_TEXT, tier2_client)

    assert tier1_result == LONG_FUTURE_WORK_TEXT
    assert tier2_result == LONG_INFERRED_TEXT
    assert tier1_result != tier2_result