from datetime import date, timedelta

from paper_scout.ranking.dedupe import dedupe_papers
from paper_scout.ranking.rank import rank_papers
from paper_scout.utils.models import Paper, SourceName


def _make_paper(title, source, **kwargs):
    return Paper(
        title=title,
        abstract=kwargs.pop("abstract", "Some abstract text."),
        source=source,
        **kwargs,
    )


# ── Dedup tests ────────────────────────────────────────────────────────────

def test_dedupe_collapses_exact_duplicate_titles():
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV, arxiv_id="1234.5678"),
        _make_paper("Diffusion Models for Audio Generation", SourceName.SEMANTIC_SCHOLAR, citation_count=42),
    ]
    result = dedupe_papers(papers)
    assert len(result) == 1
    assert result[0].citation_count == 42  # merged in from second source
    assert result[0].arxiv_id == "1234.5678"  # preserved from first source


def test_dedupe_collapses_near_duplicate_titles():
    papers = [
        _make_paper("Diffusion Models for Audio Generation.", SourceName.ARXIV),
        _make_paper("Diffusion Models for Audio Generation", SourceName.HUGGINGFACE_PAPERS),
    ]
    result = dedupe_papers(papers, similarity_threshold=0.9)
    assert len(result) == 1


def test_dedupe_keeps_distinct_papers_separate():
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV),
        _make_paper("Transformer Architectures for NLP", SourceName.SEMANTIC_SCHOLAR),
    ]
    result = dedupe_papers(papers)
    assert len(result) == 2


def test_dedupe_handles_empty_list():
    assert dedupe_papers([]) == []


def test_dedupe_prefers_longer_abstract_on_merge():
    short_abstract = "Short version."
    long_abstract = "This is a much longer and more complete version of the abstract."
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV, abstract=short_abstract),
        _make_paper("Diffusion Models for Audio Generation", SourceName.SEMANTIC_SCHOLAR, abstract=long_abstract),
    ]
    result = dedupe_papers(papers)
    assert len(result) == 1
    assert result[0].abstract == long_abstract


def test_dedupe_matches_on_arxiv_id_even_if_titles_differ_slightly():
    papers = [
        _make_paper("Diffusion Models for Audio Gen (v1)", SourceName.ARXIV, arxiv_id="9999.1111"),
        _make_paper("Diffusion Models for Audio Generation", SourceName.HUGGINGFACE_PAPERS, arxiv_id="9999.1111"),
    ]
    result = dedupe_papers(papers, similarity_threshold=0.99)  # too strict for fuzzy match to catch it
    assert len(result) == 1  # arxiv_id match should still catch it


# ── Ranking tests ────────────────────────────────────────────────────────────

def test_rank_papers_orders_by_relevance_and_recency():
    today = date.today()
    papers = [
        Paper(
            title="Diffusion Models for Audio Generation",
            abstract="A method for generating audio using diffusion models.",
            source=SourceName.ARXIV,
            published_date=today,
            citation_count=5,
        ),
        Paper(
            title="A Survey of Ancient Roman Architecture",
            abstract="An overview of Roman columns and aqueducts.",
            source=SourceName.ARXIV,
            published_date=today - timedelta(days=300),
            citation_count=1,
        ),
    ]
    ranked = rank_papers(
        papers,
        query="diffusion models for audio generation",
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
        weights={"relevance": 0.5, "recency": 0.3, "citations": 0.2},
        date_range_days=365,
    )
    assert ranked[0].title.startswith("Diffusion")  # clearly more relevant + recent
    assert ranked[0].composite_score > ranked[1].composite_score
    assert all(p.relevance_score is not None for p in ranked)


def test_rank_papers_handles_empty_list():
    assert rank_papers([], "query", "BAAI/bge-small-en-v1.5", "cpu", {}, 365) == []


def test_rank_papers_populates_scores_on_every_paper():
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV, published_date=date.today(), citation_count=10),
        _make_paper("Reinforcement Learning for Robotics", SourceName.SEMANTIC_SCHOLAR, published_date=date.today(), citation_count=3),
    ]
    ranked = rank_papers(
        papers,
        query="audio generation",
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
        weights={"relevance": 0.5, "recency": 0.3, "citations": 0.2},
        date_range_days=365,
    )
    for p in ranked:
        assert p.relevance_score is not None
        assert p.composite_score is not None
        assert 0.0 <= p.relevance_score <= 1.0


def test_rank_papers_handles_missing_citation_and_date():
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV),  # no date, no citations
    ]
    ranked = rank_papers(
        papers,
        query="audio generation",
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
        weights={"relevance": 0.5, "recency": 0.3, "citations": 0.2},
        date_range_days=365,
    )
    assert len(ranked) == 1
    assert ranked[0].composite_score is not None


# ── Integration: dedupe then rank, as the real pipeline will call them ──────

def test_dedupe_then_rank_full_flow():
    today = date.today()
    papers = [
        _make_paper("Diffusion Models for Audio Generation", SourceName.ARXIV,
                     arxiv_id="1111.1111", published_date=today, citation_count=None),
        _make_paper("Diffusion Models for Audio Generation", SourceName.SEMANTIC_SCHOLAR,
                     arxiv_id="1111.1111", published_date=today, citation_count=50),
        _make_paper("Unrelated Paper on Ancient Pottery", SourceName.HUGGINGFACE_PAPERS,
                     published_date=today - timedelta(days=200), citation_count=1),
    ]
    deduped = dedupe_papers(papers)
    assert len(deduped) == 2  # the two diffusion entries should merge

    ranked = rank_papers(
        deduped,
        query="diffusion models for audio generation",
        embedding_model_name="BAAI/bge-small-en-v1.5",
        embedding_device="cpu",
        weights={"relevance": 0.5, "recency": 0.3, "citations": 0.2},
        date_range_days=365,
    )
    assert ranked[0].title == "Diffusion Models for Audio Generation"
    assert ranked[0].citation_count == 50  # confirms merge carried through to ranking