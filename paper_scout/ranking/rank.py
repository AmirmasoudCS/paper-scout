# paper_scout/ranking/rank.py
import logging
import math
from datetime import date, datetime, timedelta

import numpy as np
from sentence_transformers import SentenceTransformer

from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)

_model_cache: dict[str, SentenceTransformer] = {}


def _get_embedding_model(model_name: str, device: str = "cpu") -> SentenceTransformer:
    """Cache the embedding model so it's only loaded once per run."""
    if model_name not in _model_cache:
        logger.info(f"Loading embedding model '{model_name}' on {device}")
        _model_cache[model_name] = SentenceTransformer(model_name, device=device)
    return _model_cache[model_name]


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _recency_score(published: date | None, date_range_days: int) -> float:
    """1.0 for a paper published today, decaying linearly to 0.0 at the edge of the window."""
    if published is None:
        return 0.0
    today = datetime.utcnow().date()
    age_days = (today - published).days
    if age_days < 0:
        age_days = 0
    score = 1.0 - (age_days / date_range_days)
    return max(0.0, min(1.0, score))


def _citation_score(citation_count: int | None, max_citations_in_batch: int) -> float:
    """Log-scaled, normalized against the max citation count in this batch of papers."""
    if not citation_count or citation_count <= 0:
        return 0.0
    if max_citations_in_batch <= 0:
        return 0.0
    return math.log1p(citation_count) / math.log1p(max_citations_in_batch)


def rank_papers(
    papers: list[Paper],
    query: str,
    embedding_model_name: str,
    embedding_device: str,
    weights: dict[str, float],
    date_range_days: int,
) -> list[Paper]:
    """
    Score and sort papers by a composite of relevance, recency, and citation count.
    Mutates and returns Paper objects with relevance_score and composite_score populated.
    """
    if not papers:
        return []

    model = _get_embedding_model(embedding_model_name, embedding_device)

    query_embedding = model.encode(query, convert_to_numpy=True)
    abstract_embeddings = model.encode(
        [p.abstract for p in papers], convert_to_numpy=True
    )

    max_citations = max((p.citation_count or 0) for p in papers)

    scored_papers = []
    for paper, abstract_emb in zip(papers, abstract_embeddings):
        relevance = _cosine_similarity(query_embedding, abstract_emb)
        recency = _recency_score(paper.published_date, date_range_days)
        citations = _citation_score(paper.citation_count, max_citations)

        composite = (
            weights.get("relevance", 0.5) * relevance
            + weights.get("recency", 0.3) * recency
            + weights.get("citations", 0.2) * citations
        )

        paper.relevance_score = round(relevance, 4)
        paper.composite_score = round(composite, 4)
        scored_papers.append(paper)

    scored_papers.sort(key=lambda p: p.composite_score, reverse=True)
    logger.info(f"Ranked {len(scored_papers)} papers, top score: {scored_papers[0].composite_score if scored_papers else 'N/A'}")
    return scored_papers