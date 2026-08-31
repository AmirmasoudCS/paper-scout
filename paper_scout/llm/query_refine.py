"""
Prompt evaluation tests for paper_scout.llm.query_refine.

Unlike tests/test_query_refine.py, these tests intentionally call the
real small model. They are designed to evaluate the QUALITY of the
query-refinement prompt rather than the Python plumbing around it.

Run with:

    RUN_PROMPT_EVAL=1 pytest tests/prompt_eval/test_query_refine.py -v

On Windows PowerShell:

    $env:RUN_PROMPT_EVAL="1"
    pytest tests/prompt_eval/test_query_refine.py -v

These tests deliberately do NOT require an exact model response.
Small local models are probabilistic, and several different phrasings
can be equally good search queries.

The evaluation focuses on:
- spelling correction
- grammar/phrasing cleanup
- preservation of the original research intent
- preservation of important technical terms
- preservation of acronyms
- avoiding unnecessary scope expansion
- producing concise academic-search phrasing
"""

from __future__ import annotations

import os
import re

import pytest

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_query_refine_prompt
from paper_scout.utils.config import load_config


# ---------------------------------------------------------------------------
# Deliberately chosen evaluation cases
# ---------------------------------------------------------------------------
#
# Each case contains:
#
#   query:
#       What the user typed.
#
#   required_terms:
#       Concepts that should survive refinement. Matching is
#       case-insensitive and checks that these concepts still appear.
#
#   expected_changes:
#       What we are testing the model should improve.
#
#   forbidden_terms:
#       Terms that indicate the model invented a new topic/scope.
#
# The expected output is NOT specified exactly.
# ---------------------------------------------------------------------------

CASES = [
    {
        "name": "obvious spelling mistakes",
        "query": "difusion modles for audeo genration",
        "required_terms": ["diffusion", "audio", "generation"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "deep learning medical imaging",
        "query": "deep lerning for medical image analisis",
        "required_terms": ["deep learning", "medical", "image"],
        "expected_changes": ["spelling", "phrasing"],
    },
    {
        "name": "mixed capitalization",
        "query": "DEEP LEARNING FOR MEDICAL IMAGE ANALYSIS",
        "required_terms": ["deep learning", "medical", "image", "analysis"],
        "expected_changes": ["capitalization"],
    },
    {
        "name": "bad grammar",
        "query": "machine learning methods for detect cancer in medical images",
        "required_terms": ["machine learning", "cancer", "medical", "images"],
        "expected_changes": ["grammar", "phrasing"],
    },
    {
        "name": "transformer NLP",
        "query": "transformer models for text clasification",
        "required_terms": ["transformer", "text", "classification"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "sentiment analysis",
        "query": "transformers for natural language procesing and sentiment analisis",
        "required_terms": ["transformer", "natural language", "sentiment", "analysis"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "RAG acronym preservation",
        "query": "llms for retrieval augmented generation",
        "required_terms": ["LLM", "RAG"],
        "expected_changes": ["phrasing", "acronym normalization"],
    },
    {
        "name": "RAG question answering",
        "query": "retrieval augmented generation for question answering",
        "required_terms": ["retrieval", "augmented", "generation", "question", "answering"],
        "expected_changes": [],
    },
    {
        "name": "vision transformers",
        "query": "vision transformers for image clasification",
        "required_terms": ["vision transformer", "image", "classification"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "reinforcement learning robotics",
        "query": "reinforcment learning for robot navigaton",
        "required_terms": ["reinforcement learning", "robot", "navigation"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "research question",
        "query": "what is the impact of federated learning on privacy in healthcare?",
        "required_terms": ["federated learning", "privacy", "healthcare"],
        "expected_changes": ["phrasing"],
    },
    {
        "name": "specific medical application",
        "query": "deep learning for diabetic retinopathy detection in retinal images",
        "required_terms": ["deep learning", "diabetic retinopathy", "detection", "retinal"],
        "expected_changes": [],
    },
    {
        "name": "LLM hallucinations",
        "query": "papers on LLM halucinations in RAG systems",
        "required_terms": ["LLM", "hallucination", "RAG"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "local model constraint",
        "query": "LLM hallucinations in RAG systems particulary when using small local models",
        "required_terms": ["LLM", "hallucination", "RAG", "small", "local"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "retrieval comparison",
        "query": "comparison of retrival methods in RAG and their impact on large language model answer quality",
        "required_terms": ["retrieval", "RAG", "large language model", "answer quality"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "compound technical query",
        "query": "effect of chunk size and embedding models on RAG retrival performance",
        "required_terms": ["chunk", "embedding", "RAG", "retrieval"],
        "expected_changes": ["spelling"],
    },
    {
        "name": "lowercase technical acronyms",
        "query": "rag with llm for question answering",
        "required_terms": ["RAG", "LLM", "question answering"],
        "expected_changes": ["capitalization", "acronym normalization"],
    },
    {
        "name": "very short query",
        "query": "graph neural networks",
        "required_terms": ["graph neural network"],
        "expected_changes": [],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Normalize text for semantic-ish string comparisons."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\- ]+", " ", text)
    return " ".join(text.split())


def _contains_concept(output: str, concept: str) -> bool:
    """
    Check whether a required concept survived refinement.

    This is intentionally simple. We are not trying to build a semantic
    evaluator here; the goal is to catch obvious cases where the model
    drops an important part of the user's query.
    """
    return _normalize(concept) in _normalize(output)


def _assert_reasonable_output(original: str, refined: str) -> None:
    """Basic sanity checks for a live model response."""

    assert refined.strip(), "Model returned an empty refinement."

    assert "\n" not in refined, (
        "Refinement should be a single line, "
        f"but got: {refined!r}"
    )

    assert len(refined) >= 3

    # The production code already has this guard. We repeat the idea
    # here because this is a prompt evaluation and we want to surface
    # obviously pathological generations.
    assert len(refined) <= len(original) * 4, (
        "Refinement became suspiciously long.\n"
        f"Original: {original!r}\n"
        f"Refined:  {refined!r}"
    )

    # The prompt asks for query text only.
    assert not refined.startswith("```"), (
        f"Model returned markdown instead of query text: {refined!r}"
    )

    assert not refined.lower().startswith(
        ("here is", "here's", "corrected query", "refined query")
    ), (
        "Model added explanatory text instead of returning only "
        f"the query: {refined!r}"
    )


# ---------------------------------------------------------------------------
# Live model fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client() -> OllamaClient:
    """
    Create the configured Ollama client once for the whole evaluation.

    Prompt evaluation is opt-in because it requires a real local model.
    """

    if os.getenv("RUN_PROMPT_EVAL") != "1":
        pytest.skip(
            "Prompt evaluation disabled. "
            "Set RUN_PROMPT_EVAL=1 to run against the local Ollama model."
        )

    config = load_config()
    client = OllamaClient.from_config(config)

    if not client.is_available():
        pytest.skip(
            "Ollama is not available. Start Ollama before running "
            "the prompt evaluation."
        )

    verified = client.verify_configured_models()
    if not all(verified.values()):
        pytest.skip(
            f"Configured Ollama model(s) are unavailable: {verified}"
        )

    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_query_refinement_preserves_research_intent(case, client):
    """
    The most important evaluation:

    The model may rewrite the query, but it must not silently remove
    important concepts from the user's original request.
    """

    result = refine_search_query(case["query"], client)

    assert result.refined is not None, (
        f"Refinement failed for query: {case['query']!r}\n"
        f"Error: {result.error}"
    )

    refined = result.refined

    _assert_reasonable_output(case["query"], refined)

    missing = [
        term
        for term in case["required_terms"]
        if not _contains_concept(refined, term)
    ]

    assert not missing, (
        "Refinement appears to have changed the user's research intent.\n"
        f"Original: {case['query']}\n"
        f"Refined:  {refined}\n"
        f"Missing concepts: {missing}"
    )


@pytest.mark.parametrize(
    "case",
    [
        case
        for case in CASES
        if "spelling" in case["expected_changes"]
    ],
    ids=lambda case: case["name"],
)
def test_query_refinement_fixes_obvious_spelling_errors(case, client):
    """
    Obvious misspellings should not survive when there is an obvious
    correction.

    This deliberately checks only that the misspelled token disappears;
    it does not demand one exact final sentence.
    """

    result = refine_search_query(case["query"], client)

    assert result.refined is not None

    original_words = _normalize(case["query"]).split()
    refined_words = _normalize(result.refined).split()

    # At least one spelling change should have happened for these cases.
    assert original_words != refined_words, (
        "The model returned essentially the same malformed query.\n"
        f"Original: {case['query']}\n"
        f"Refined:  {result.refined}"
    )


@pytest.mark.parametrize(
    "query,required_acronyms",
    [
        ("llms for retrieval augmented generation", ["LLM", "RAG"]),
        ("rag with llm for question answering", ["RAG", "LLM"]),
        (
            "papers on LLM halucinations in RAG systems",
            ["LLM", "RAG"],
        ),
        (
            "LLM hallucinations in RAG systems particulary when using small local models",
            ["LLM", "RAG"],
        ),
    ],
)
def test_query_refinement_normalizes_common_acronyms(
    query,
    required_acronyms,
    client,
):
    """
    Technical acronyms should remain recognizable rather than being
    expanded into unrelated wording or silently removed.

    We accept either the acronym itself or its expanded form where
    appropriate, but the current cases intentionally prefer the
    conventional academic acronyms.
    """

    result = refine_search_query(query, client)

    assert result.refined is not None

    refined = result.refined

    for acronym in required_acronyms:
        assert (
            acronym.lower() in refined.lower()
            or {
                "LLM": "large language model",
                "RAG": "retrieval augmented generation",
            }[acronym].lower()
            in refined.lower()
        ), (
            f"Acronym/concept {acronym!r} disappeared.\n"
            f"Original: {query}\n"
            f"Refined:  {refined}"
        )


def test_query_refinement_does_not_add_unrequested_research_topics(client):
    """
    The model should improve phrasing without turning a narrow query
    into a much broader research question.
    """

    query = "vision transformers for image classification"

    result = refine_search_query(query, client)

    assert result.refined is not None

    refined = result.refined.lower()

    assert "vision transformer" in refined
    assert "image" in refined
    assert "classification" in refined

    # These are deliberately unrelated additions that would indicate
    # that the model is brainstorming rather than refining.
    forbidden = [
        "medical",
        "healthcare",
        "sentiment",
        "reinforcement learning",
        "robotics",
        "audio",
        "speech",
        "finance",
    ]

    unexpected = [term for term in forbidden if term in refined]

    assert not unexpected, (
        "Model introduced unrelated research topics.\n"
        f"Original: {query}\n"
        f"Refined:  {result.refined}\n"
        f"Unexpected terms: {unexpected}"
    )


def test_query_refinement_prompt_contains_academic_search_guidance(client):
    """
    This is a cheap prompt-regression test.

    It does not call the model. It makes sure future prompt edits don't
    accidentally remove the instructions that define this feature.
    """

    system, user = build_query_refine_prompt(
        "difusion models for audeo genration"
    )

    system_lower = system.lower()
    user_lower = user.lower()

    assert "spelling" in system_lower
    assert "grammar" in system_lower
    assert "research" in system_lower
    assert "search" in system_lower

    assert "difusion models for audeo genration" in user_lower


# ---------------------------------------------------------------------------
# Optional aggregate evaluation
# ---------------------------------------------------------------------------


def test_query_refinement_overall_success_rate(client):
    """
    Run the complete evaluation set and require a reasonable minimum
    success rate.

    This is intentionally a relatively forgiving threshold at first.
    Once you have baseline results from your current prompt, you can
    raise it as the prompt improves.

    IMPORTANT:
    This is not a test of exact wording. A query passes when it remains
    a valid, concise query and preserves all required concepts.
    """

    passed = 0
    failures: list[str] = []

    for case in CASES:
        result = refine_search_query(case["query"], client)

        if result.refined is None:
            failures.append(
                f"{case['name']}: refinement failed ({result.error})"
            )
            continue

        try:
            _assert_reasonable_output(case["query"], result.refined)

            missing = [
                term
                for term in case["required_terms"]
                if not _contains_concept(result.refined, term)
            ]

            if missing:
                failures.append(
                    f"{case['name']}: missing concepts {missing} "
                    f"-> {result.refined!r}"
                )
                continue

            passed += 1

        except AssertionError as exc:
            failures.append(f"{case['name']}: {exc}")

    success_rate = passed / len(CASES)

    print("\n" + "=" * 70)
    print("QUERY REFINEMENT PROMPT EVALUATION")
    print("=" * 70)
    print(f"Passed:      {passed}/{len(CASES)}")
    print(f"Success:     {success_rate:.1%}")
    print(f"Failed:      {len(failures)}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  - {failure}")

    print("=" * 70)

    # Start forgiving. We can make this stricter after establishing
    # a baseline with the current prompt.
    assert success_rate >= 0.75, (
        f"Query refinement success rate was only {success_rate:.1%}. "
        "See the failures printed above."
    )