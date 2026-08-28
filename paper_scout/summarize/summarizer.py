"""
paper_scout.summarize.summarizer

Phase 5 — turns each Paper's abstract + extracted Conclusion/Limitations
text into a structured PaperSummary, using the small local model
(qwen3.5:9b) via OllamaClient in json_mode.

Consistent with the rest of the pipeline: never raises on a per-paper
basis. A paper that fails to summarize (LLM unreachable, malformed JSON,
missing required fields) is logged and skipped — `paper.summary` stays
None and the pipeline continues with the papers that did succeed.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.prompts import build_summarize_prompt
from paper_scout.utils.models import Paper, PaperSummary

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"problem", "method", "key_result"}
_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _clean_json_text(raw: str) -> str:
    """
    Strip markdown code fences if the model wrapped its JSON in them
    despite json_mode — some models do this inconsistently. Cheap
    insurance, doesn't hurt if there's nothing to strip.
    """
    return _JSON_FENCE_RE.sub("", raw).strip()


def _extract_json_object(text: str) -> str:
    """
    Best-effort extraction of a JSON object from text that may contain
    leading/trailing prose. Needed because format="json" is known to be
    silently ignored on some thinking-capable models once think=False
    is set (ollama/ollama#14645) — so json_mode isn't a hard guarantee
    of clean JSON-only output. Falls back to the original text if no
    `{...}` span is found (json.loads will then fail with a clear error).
    """
    match = _JSON_OBJECT_RE.search(text)
    return match.group(0) if match else text


def _parse_summary_json(raw: str, paper_title: str) -> Optional[PaperSummary]:
    cleaned = _clean_json_text(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # format="json" may have been silently ignored (see _extract_json_object
        # docstring) — try pulling a {...} span out of surrounding prose before
        # giving up.
        extracted = _extract_json_object(cleaned)
        try:
            data = json.loads(extracted)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Malformed JSON summary for %r: %s\nRaw: %.200s", paper_title, exc, raw
            )
            return None

    if not isinstance(data, dict):
        logger.warning("Summary for %r was valid JSON but not an object: %r", paper_title, data)
        return None

    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        logger.warning("Summary for %r missing required keys %s: %r", paper_title, missing, data)
        return None

    try:
        return PaperSummary(
            problem=str(data["problem"]).strip(),
            method=str(data["method"]).strip(),
            key_result=str(data["key_result"]).strip(),
            stated_limitations=(
                str(data["stated_limitations"]).strip()
                if data.get("stated_limitations")
                else None
            ),
        )
    except Exception as exc:  # pydantic ValidationError or similar
        logger.warning("Failed to build PaperSummary for %r: %s", paper_title, exc)
        return None


def summarize_paper(paper: Paper, client: OllamaClient) -> Optional[PaperSummary]:
    """
    Summarize a single paper using the small model. Returns None (never
    raises) if the LLM call fails or returns unusable output.
    """
    system, user = build_summarize_prompt(paper)
    raw = client.generate_small(user, system=system, json_mode=True)

    if raw is None:
        logger.warning("No response from small model while summarizing %r", paper.title)
        return None

    return _parse_summary_json(raw, paper.title)


def summarize_papers(papers: list[Paper], client: OllamaClient) -> list[Paper]:
    """
    Summarize a list of papers in place (sets paper.summary where
    successful) and returns the same list. One paper's failure never
    stops the batch — matches the source-fetcher degrade-gracefully
    contract used throughout the pipeline.

    Papers are processed sequentially: the small model runs on
    constrained local hardware (32GB RAM / 4GB VRAM) where concurrent
    requests would just contend for the same resources rather than
    speeding things up.
    """
    succeeded = 0
    for paper in papers:
        summary = summarize_paper(paper, client)
        if summary is not None:
            paper.summary = summary
            succeeded += 1
        else:
            logger.info("Skipping summary for %r — see warnings above", paper.title)

    logger.info("Summarized %d/%d papers successfully", succeeded, len(papers))
    return papers