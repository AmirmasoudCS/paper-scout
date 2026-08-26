import logging
import time

from semanticscholar import SemanticScholar
from semanticscholar.SemanticScholarException import (
    ObjectNotFoundException,
)

from paper_scout.sources.base import PaperSource
from paper_scout.utils.models import Paper, SourceName

logger = logging.getLogger(__name__)


class SemanticScholarSource(PaperSource):
    name = SourceName.SEMANTIC_SCHOLAR

    def __init__(self, api_key: str | None = None):
        self.client = SemanticScholar(api_key=api_key) if api_key else SemanticScholar()

    def search(self, query: str, max_results: int, retries: int = 3) -> list[Paper]:
        results = []
        for attempt in range(retries):
            try:
                results = self.client.search_paper(
                    query,
                    limit=max_results,
                    fields=[
                        "title",
                        "authors",
                        "abstract",
                        "url",
                        "openAccessPdf",
                        "publicationDate",
                        "citationCount",
                        "externalIds",
                        "tldr",
                    ],
                )
                results = list(results[:max_results])
                break
            except ObjectNotFoundException:
                logger.info(f"Semantic Scholar: no results for query '{query}'")
                return []
            except Exception as e:
                logger.warning(f"Semantic Scholar attempt {attempt + 1}/{retries} failed: {e}")
                if attempt == retries - 1:
                    logger.error(f"Semantic Scholar search failed for query '{query}' after {retries} attempts")
                    return []
                time.sleep(2 ** attempt)

        papers = []
        for result in results:
            try:
                if not result.abstract:
                    continue  # skip papers with no abstract, not useful for summarization

                pdf_url = None
                if result.openAccessPdf:
                    pdf_url = result.openAccessPdf.get("url")

                arxiv_id = None
                if result.externalIds:
                    arxiv_id = result.externalIds.get("ArXiv")

                published_date = None
                if result.publicationDate:
                    published_date = result.publicationDate

                papers.append(
                    Paper(
                        title=result.title.strip(),
                        authors=[a.name for a in (result.authors or [])],
                        abstract=result.abstract.strip().replace("\n", " "),
                        source=self.name,
                        published_date=published_date,
                        url=result.url,
                        pdf_url=pdf_url,
                        arxiv_id=arxiv_id,
                        citation_count=result.citationCount,
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping malformed Semantic Scholar result: {e}")
                continue

        return papers