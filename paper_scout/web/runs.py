"""
paper_scout.web.runs

Reads already-completed run folders from outputs/ for display in the
web UI. Never touches the pipeline itself here — this module is
read-only, purely for browsing past runs. Each run folder is expected
to contain report.md, report.pdf, run_metadata.json, and a pdfs/
subfolder, per pipeline.py's node_write_report.

Degrades gracefully per the rest of the project's philosophy: a run
folder missing its metadata file (e.g. an interrupted run) is still
listed, just with whatever fields we can infer from the folder itself.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RunSummary:
    """Lightweight view of one run folder, for the sidebar list."""

    run_id: str  # the folder name itself, e.g. "diffusion-models_2026-08-29"
    query: str
    run_timestamp: Optional[str]
    paper_count: int
    sources: dict
    extraction_summary: dict
    future_work_ideation: dict
    has_report: bool
    has_pdf: bool


def _folder_name_to_query_guess(folder_name: str) -> str:
    """Fallback query text if run_metadata.json is missing — strips the
    trailing _YYYY-MM-DD and turns hyphens back into spaces."""
    parts = folder_name.rsplit("_", 1)
    slug = parts[0] if len(parts) == 2 else folder_name
    return slug.replace("-", " ")


def _load_run_summary(run_dir: Path) -> RunSummary:
    metadata_path = run_dir / "run_metadata.json"
    metadata: dict = {}
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read run_metadata.json in %s: %s", run_dir, exc)

    return RunSummary(
        run_id=run_dir.name,
        query=metadata.get("query") or _folder_name_to_query_guess(run_dir.name),
        run_timestamp=metadata.get("run_timestamp"),
        paper_count=metadata.get("paper_count", 0),
        sources=metadata.get("sources", {}),
        extraction_summary=metadata.get("extraction_summary", {}),
        future_work_ideation=metadata.get("future_work_ideation", {}),
        has_report=(run_dir / "report.md").exists(),
        has_pdf=(run_dir / "report.pdf").exists(),
    )


def list_runs(output_dir: str | Path) -> list[RunSummary]:
    """
    List every run folder under output_dir, most recent first.
    Returns [] (never raises) if output_dir doesn't exist yet — e.g.
    on a completely fresh install before any run has happened.
    """
    output_dir = Path(output_dir)
    if not output_dir.exists():
        return []

    run_dirs = sorted(
        (p for p in output_dir.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return [_load_run_summary(run_dir) for run_dir in run_dirs]


def get_run(output_dir: str | Path, run_id: str) -> Optional[RunSummary]:
    """Look up a single run by its folder name. None if it doesn't exist."""
    run_dir = Path(output_dir) / run_id
    if not run_dir.is_dir():
        return None
    return _load_run_summary(run_dir)


def get_run_report_markdown(output_dir: str | Path, run_id: str) -> Optional[str]:
    """Raw markdown content of a run's report.md, or None if missing."""
    report_path = Path(output_dir) / run_id / "report.md"
    if not report_path.exists():
        return None
    return report_path.read_text(encoding="utf-8")

# ── Replaces get_qa_history / append_qa_turn at the bottom of runs.py ──

_EMPTY_QA_HISTORY = {"turns": [], "summary": None, "summarized_through": 0}


def get_qa_history(output_dir: str | Path, run_id: str) -> dict:
    """Loads a run's saved Q&A state: {"turns": [...], "summary":
    str|None, "summarized_through": int}. "turns" holds every raw
    question/answer pair (for display); "summary" and
    "summarized_through" track how much of the older conversation has
    already been condensed by qa/history.py's sliding window. Returns
    a fresh empty structure (never raises) if no history exists yet or
    the file is corrupted."""
    path = Path(output_dir) / run_id / "qa_history.json"
    if not path.exists():
        return dict(_EMPTY_QA_HISTORY)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read qa_history.json in %s: %s", path, exc)
        return dict(_EMPTY_QA_HISTORY)

    # Merge over the defaults so older/partial files (or a corrupted
    # write) don't blow up callers expecting all three keys present.
    return {**_EMPTY_QA_HISTORY, **loaded}


def save_qa_history(output_dir: str | Path, run_id: str, history: dict) -> None:
    """Writes a run's full Q&A state back to disk. Best-effort — a
    write failure here shouldn't break the answer already returned to
    the user, so this logs rather than raises."""
    run_dir = Path(output_dir) / run_id
    path = run_dir / "qa_history.json"
    try:
        path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed to write qa_history.json in %s: %s", path, exc)


def append_qa_turn(output_dir: str | Path, run_id: str, history: dict, question: str, answer: str) -> None:
    """Appends one new Q&A turn to an (already-loaded, possibly
    summary-updated) history dict and persists the result. Callers
    should pass the history dict returned by
    qa.history.build_conversation_context (or get_qa_history, if no
    summarization was needed) so any summary progress made this
    request isn't lost."""
    updated = {
        **history,
        "turns": history.get("turns", []) + [{"question": question, "answer": answer}],
    }
    save_qa_history(output_dir, run_id, updated)