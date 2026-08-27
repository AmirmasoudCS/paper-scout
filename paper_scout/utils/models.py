from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceName(str, Enum):
    ARXIV = "arxiv"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    HUGGINGFACE_PAPERS = "huggingface_papers"


class ExtractedSections(BaseModel):
    """Sections pulled from the paper's full text (Phase 3)."""
    abstract: Optional[str] = None
    conclusion: Optional[str] = None
    limitations: Optional[str] = None
    future_work: Optional[str] = None


class PaperSummary(BaseModel):
    """Structured per-paper summary produced by the small model (Phase 5)."""
    problem: str
    method: str
    key_result: str
    stated_limitations: Optional[str] = None


class Paper(BaseModel):
    # Core identity — populated at fetch time (Phase 1)
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str
    source: SourceName
    published_date: Optional[date] = None
    url: Optional[HttpUrl] = None
    pdf_url: Optional[HttpUrl] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    citation_count: Optional[int] = None

    # Populated during ranking (Phase 2)
    relevance_score: Optional[float] = None
    composite_score: Optional[float] = None

    # Populated during ingestion (Phase 3)
    extracted_sections: Optional[ExtractedSections] = None
    full_text_available: bool = False

    # Populated during summarization (Phase 5)
    summary: Optional[PaperSummary] = None

    model_config = ConfigDict(use_enum_values=True)

    def dedupe_key(self) -> str:
        """Normalized title used for cross-source deduplication (Phase 2)."""
        return " ".join(self.title.lower().split())


class PipelineRun(BaseModel):
    """Top-level container for one end-to-end pipeline execution."""
    query: str
    run_timestamp: datetime = Field(default_factory=datetime.utcnow)
    papers: list[Paper] = Field(default_factory=list)
    cross_paper_synthesis: Optional[str] = None
    future_work_ideas: Optional[str] = None
    report_path: Optional[str] = None