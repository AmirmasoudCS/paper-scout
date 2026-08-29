# tests/test_sources.py
import pytest

from paper_scout.sources.arxiv_source import ArxivSource
from paper_scout.sources.semantic_scholar_source import SemanticScholarSource
from paper_scout.sources.huggingface_papers_source import HuggingFacePapersSource
from paper_scout.utils.models import Paper
from paper_scout.sources.runner import fetch_all_sources_with_stats


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

def test_fetch_all_sources_with_stats_reports_counts_per_source(monkeypatch):
    fetcher_a = MagicMock()
    fetcher_a.name = "arxiv"
    fetcher_a.search.return_value = [_sample_paper("From A"), _sample_paper("From A2")]

    fetcher_b = MagicMock()
    fetcher_b.name = "huggingface_papers"
    fetcher_b.search.return_value = [_sample_paper("From B")]

    monkeypatch.setattr(
        "paper_scout.sources.runner.build_source_fetchers", lambda config: [fetcher_a, fetcher_b]
    )
    config = {
        "search": {"max_papers_per_source": 10},
        "sources": {
            "arxiv": {"enabled": True},
            "semantic_scholar": {"enabled": False},
            "huggingface_papers": {"enabled": True},
        },
    }

    papers, stats = fetch_all_sources_with_stats("test query", config)

    assert len(papers) == 3
    assert stats["arxiv"] == {"enabled": True, "papers_found": 2}
    assert stats["huggingface_papers"] == {"enabled": True, "papers_found": 1}


def test_fetch_all_sources_with_stats_records_error_on_source_failure(monkeypatch):
    broken_fetcher = MagicMock()
    broken_fetcher.name = "semantic_scholar"
    broken_fetcher.search.side_effect = Exception("HTTP 403 Forbidden")

    monkeypatch.setattr(
        "paper_scout.sources.runner.build_source_fetchers", lambda config: [broken_fetcher]
    )
    config = {
        "search": {"max_papers_per_source": 10},
        "sources": {
            "arxiv": {"enabled": False},
            "semantic_scholar": {"enabled": True},
            "huggingface_papers": {"enabled": False},
        },
    }

    papers, stats = fetch_all_sources_with_stats("test query", config)

    assert papers == []
    assert stats["semantic_scholar"]["papers_found"] == 0
    assert "403 Forbidden" in stats["semantic_scholar"]["error"]


def test_fetch_all_sources_with_stats_backfills_disabled_sources(monkeypatch):
    monkeypatch.setattr("paper_scout.sources.runner.build_source_fetchers", lambda config: [])
    config = {
        "search": {"max_papers_per_source": 10},
        "sources": {
            "arxiv": {"enabled": False},
            "semantic_scholar": {"enabled": False},
            "huggingface_papers": {"enabled": False},
        },
    }

    papers, stats = fetch_all_sources_with_stats("test query", config)

    assert papers == []
    assert stats["arxiv"] == {"enabled": False, "papers_found": 0}
    assert stats["semantic_scholar"] == {"enabled": False, "papers_found": 0}
    assert stats["huggingface_papers"] == {"enabled": False, "papers_found": 0}


def test_fetch_all_sources_still_returns_just_papers():
    """Existing callers of fetch_all_sources() must be unaffected by the stats addition."""
    from paper_scout.sources.runner import fetch_all_sources

    result = fetch_all_sources("diffusion models", SAMPLE_CONFIG)
    assert isinstance(result, list)