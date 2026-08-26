import logging
logging.basicConfig(level=logging.INFO)

from paper_scout.sources.papers_with_code_source import PapersWithCodeSource

source = PapersWithCodeSource()
papers = source.search("diffusion models for audio generation", max_results=5)

for p in papers:
    print(f"- {p.title} ({p.published_date}) [arxiv: {p.arxiv_id}]")
    print(f"  {p.abstract[:150]}...")
    print()