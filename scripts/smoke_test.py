# scripts/smoke_test.py (temporary content for this phase)
import logging
logging.basicConfig(level=logging.INFO)

from paper_scout.sources.arxiv_source import ArxivSource

source = ArxivSource()
papers = source.search("diffusion models for audio generation", max_results=5)

for p in papers:
    print(f"- {p.title} ({p.published_date}) [{p.arxiv_id}]")
    print(f"  {p.abstract[:150]}...")
    print()