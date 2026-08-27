# paper_scout/ranking/dedupe.py
import logging

from rapidfuzz import fuzz

from paper_scout.utils.models import Paper

logger = logging.getLogger(__name__)


def _merge_papers(primary: Paper, secondary: Paper) -> Paper:
    """Merge two Paper objects believed to be the same paper.
    `primary` is kept as the base; missing fields are filled in from `secondary`."""
    merged_data = primary.model_dump()

    for field in ("pdf_url", "citation_count", "doi", "arxiv_id", "url"):
        if merged_data.get(field) is None:
            secondary_value = getattr(secondary, field)
            if secondary_value is not None:
                merged_data[field] = secondary_value

    # prefer the longer abstract (some sources truncate)
    if len(secondary.abstract) > len(primary.abstract):
        merged_data["abstract"] = secondary.abstract

    # keep authors list if primary's is empty (e.g. Papers with Code style gaps)
    if not merged_data.get("authors"):
        merged_data["authors"] = secondary.authors

    return Paper(**merged_data)


def dedupe_papers(papers: list[Paper], similarity_threshold: float = 0.9) -> list[Paper]:
    """
    Deduplicate papers across sources.
    Exact-match pass on normalized title first, then fuzzy match for near-duplicates.
    Merges data from duplicate entries rather than discarding it.
    """
    if not papers:
        return []

    deduped: list[Paper] = []
    merged_count = 0

    for paper in papers:
        match_index = None

        for i, existing in enumerate(deduped):
            # fast path: exact match on normalized key
            if paper.dedupe_key() == existing.dedupe_key():
                match_index = i
                break

            # also check arxiv_id/doi as strong identity signals if present
            if paper.arxiv_id and existing.arxiv_id and paper.arxiv_id == existing.arxiv_id:
                match_index = i
                break
            if paper.doi and existing.doi and paper.doi == existing.doi:
                match_index = i
                break

            # fuzzy fallback on title similarity
            score = fuzz.ratio(paper.dedupe_key(), existing.dedupe_key()) / 100.0
            if score >= similarity_threshold:
                match_index = i
                break

        if match_index is not None:
            deduped[match_index] = _merge_papers(deduped[match_index], paper)
            merged_count += 1
        else:
            deduped.append(paper)

    logger.info(f"Deduped {len(papers)} papers -> {len(deduped)} unique ({merged_count} merged)")
    return deduped