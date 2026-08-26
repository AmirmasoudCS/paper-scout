import logging
import time

import arxiv

from paper_scout.sources.base import PaperSource
from paper_scout.utils.models import Paper, SourceName

logger = logging.getLogger(__name__)


class ArxivSource(PaperSource):
    name = SourceName.ARXIV

    def __init__(self, categories: list[str] | None = None):
        self.categories = categories or []

    def search(self, query: str, max_results: int, retries: int = 3) -> list[Paper]:
        full_query = f"all:{query}"
        if self.categories:
            cat_filter = " OR ".join(f"cat:{c}" for c in self.categories)
            full_query = f"({full_query}) AND ({cat_filter})"

        results = []
        for attempt in range(retries):
            try:
                search = arxiv.Search(
                    query=full_query,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.Relevance,
                )
                client = arxiv.Client(page_size=max_results, delay_seconds=3.0, num_retries=1)
                results = list(client.results(search))
                break
            except Exception as e:
                logger.warning(f"arXiv attempt {attempt + 1}/{retries} failed: {e}")
                if attempt == retries - 1:
                    logger.error(f"arXiv search failed for query '{query}' after {retries} attempts")
                    return []
                time.sleep(2 ** attempt)

        papers = []
        for result in results:
            try:
                papers.append(
                    Paper(
                        title=result.title.strip(),
                        authors=[a.name for a in result.authors],
                        abstract=result.summary.strip().replace("\n", " "),
                        source=self.name,
                        published_date=result.published.date(),
                        url=result.entry_id,
                        pdf_url=result.pdf_url,
                        arxiv_id=result.get_short_id(),
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping malformed arXiv result: {e}")
                continue

        return papers