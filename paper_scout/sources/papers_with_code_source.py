import logging
import time

import requests

from paper_scout.sources.base import PaperSource
from paper_scout.utils.models import Paper, SourceName

logger = logging.getLogger(__name__)

BASE_URL = "https://paperswithcode.com/api/v1/papers/"


class PapersWithCodeSource(PaperSource):
    name = SourceName.PAPERS_WITH_CODE

    def search(self, query: str, max_results: int, retries: int = 3) -> list[Paper]:
        params = {"q": query, "items_per_page": max_results}

        data = None
        for attempt in range(retries):
            try:
                resp = requests.get(BASE_URL, params=params, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                logger.warning(f"Papers with Code attempt {attempt + 1}/{retries} failed: {e}")
                if attempt == retries - 1:
                    logger.error(f"Papers with Code search failed for query '{query}' after {retries} attempts")
                    return []
                time.sleep(2 ** attempt)

        results = data.get("results", []) if data else []

        papers = []
        for result in results:
            try:
                abstract = (result.get("abstract") or "").strip()
                if not abstract:
                    continue  # skip entries with no abstract, not useful for summarization

                published_date = None
                if result.get("published"):
                    published_date = result["published"]  # already ISO format (YYYY-MM-DD)

                papers.append(
                    Paper(
                        title=(result.get("title") or "").strip(),
                        authors=[],  # PwC API doesn't return structured author list on search
                        abstract=abstract.replace("\n", " "),
                        source=self.name,
                        published_date=published_date,
                        url=result.get("url_abs"),
                        pdf_url=result.get("url_pdf"),
                        arxiv_id=result.get("arxiv_id"),
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping malformed Papers with Code result: {e}")
                continue

        return papers