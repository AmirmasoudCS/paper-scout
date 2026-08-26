import logging
logging.basicConfig(level=logging.INFO)

from paper_scout.sources.semantic_scholar_source import SemanticScholarSource

source = SemanticScholarSource()
papers = source.search("diffusion models for audio generation", max_results=5)

for p in papers:
    print(f"- {p.title} ({p.published_date}) [citations: {p.citation_count}]")
    print(f"  {p.abstract[:150]}...")
    print()