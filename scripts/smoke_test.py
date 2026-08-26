# scripts/smoke_test.py (temporary content for this phase)
import logging
logging.basicConfig(level=logging.INFO)

from paper_scout.sources.arxiv_source import ArxivSource


import socket
import requests

# Force requests to only use IPv4
requests.packages.urllib3.util.connection.HAS_IPV6 = False

r = requests.get(
    "https://export.arxiv.org/api/query",
    params={"search_query": "all:test", "max_results": 1},
    timeout=15,
)
print(r.status_code)
print(r.text[:300])

"""
source = ArxivSource()
papers = source.search("diffusion models for audio generation", max_results=5)


for p in papers:
    print(f"- {p.title} ({p.published_date}) [{p.arxiv_id}]")
    print(f"  {p.abstract[:150]}...")
    print()
    """