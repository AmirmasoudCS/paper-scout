import logging
import time

import requests

from paper_scout.sources.base import PaperSource
from paper_scout.utils.models import Paper, SourceName

logger = logging.getLogger(__name__)

BASE_URL = "https://huggingface.co/api/papers/search"


class HuggingFacePapersSource(PaperSource):
    name = SourceName.PAPERS_WITH_CODE  # keeping enum name for now, see note below

    def search(self, query: str, max_results: int, retries: int = 3) -> list[Paper]:
        params = {"q": query, "limit": max_results}
        headers = {"User-Agent": "Mozilla/5.0 (compatible; paper-scout/0.1)"}

        data = None
        for attempt in range(retries):
            try:
                resp = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                logger.warning(f"Hugging Face Papers attempt {attempt + 1}/{retries} failed: {e}")
                if attempt == retries - 1:
                    logger.error(f"Hugging Face Papers search failed for query '{query}' after {retries} attempts")
                    return []
                time.sleep(2 ** attempt)

        results = data if isinstance(data, list) else data.get("papers", []) if data else []

        papers = []
        for result in results:
            try:
                paper_info = result.get("paper", result)  # search results sometimes nest under "paper"
                abstract = (paper_info.get("summary") or "").strip()
                if not abstract:
                    continue

                arxiv_id = paper_info.get("id")
                published_date = paper_info.get("publishedAt")
                if published_date:
                    published_date = published_date.split("T")[0]  # ISO datetime -> date

                authors = [
                    a.get("name", "") for a in paper_info.get("authors", []) if a.get("name")
                ]

                papers.append(
                    Paper(
                        title=(paper_info.get("title") or "").strip(),
                        authors=authors,
                        abstract=abstract.replace("\n", " "),
                        source=self.name,
                        published_date=published_date,
                        url=f"https://huggingface.co/papers/{arxiv_id}" if arxiv_id else None,
                        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else None,
                        arxiv_id=arxiv_id,
                    )
                )
            except Exception as e:
                logger.warning(f"Skipping malformed Hugging Face Papers result: {e}")
                continue

        return papers