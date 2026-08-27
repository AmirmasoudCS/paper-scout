# tests/test_sources.py
import pytest

from paper_scout.sources.arxiv_source import ArxivSource
from paper_scout.sources.semantic_scholar_source import SemanticScholarSource
from paper_scout.sources.huggingface_papers_source import HuggingFacePapersSource
from paper_scout.utils.models import Paper

TEST_QUERY = "diffusion models for audio generation"
MAX_RESULTS = 5


def _assert_valid_papers(papers: list[Paper], min_expected: int = 1):
    assert isinstance(papers, list)
    assert len(papers) >= min_expected, f"Expected at least {min_expected} papers, got {len(papers)}"
    for p in papers:
        assert isinstance(p, Paper)
        assert p.title.strip() != ""
        assert p.abstract.strip() != ""


@pytest.mark.network
def test_arxiv_source_returns_relevant_papers():
    source = ArxivSource()
    papers = source.search(TEST_QUERY, max_results=MAX_RESULTS)
    _assert_valid_papers(papers)
    # sanity check relevance: at least one result should mention a query keyword
    combined_text = " ".join(p.title.lower() + p.abstract.lower() for p in papers)
    assert "diffusion" in combined_text or "audio" in combined_text


@pytest.mark.network
def test_semantic_scholar_source_returns_relevant_papers():
    source = SemanticScholarSource()
    papers = source.search(TEST_QUERY, max_results=MAX_RESULTS)
    _assert_valid_papers(papers)
    combined_text = " ".join(p.title.lower() + p.abstract.lower() for p in papers)
    assert "diffusion" in combined_text or "audio" in combined_text


@pytest.mark.network
def test_huggingface_papers_source_returns_relevant_papers():
    source = HuggingFacePapersSource()
    papers = source.search(TEST_QUERY, max_results=MAX_RESULTS)
    _assert_valid_papers(papers)
    combined_text = " ".join(p.title.lower() + p.abstract.lower() for p in papers)
    assert "diffusion" in combined_text or "audio" in combined_text


@pytest.mark.network
def test_all_sources_degrade_gracefully_on_bad_query():
    """A nonsense query should return an empty list, not raise."""
    nonsense_query = "zzxxqq_nonexistent_topic_asdkjaslkjd"
    for source_cls in (ArxivSource, SemanticScholarSource, HuggingFacePapersSource):
        source = source_cls()
        papers = source.search(nonsense_query, max_results=5)
        assert isinstance(papers, list)  # should never raise, even with 0 results