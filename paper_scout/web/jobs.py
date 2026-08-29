"""
paper_scout.web.jobs

In-memory background job tracking for pipeline runs kicked off from
the web UI. Single-process, single-user local tool, so a plain dict
guarded by a lock is enough, no database, no task queue. Jobs are
ephemeral: if the server restarts mid-run, the web UI loses track of
that job's progress, but the pipeline's own side effects (downloaded
PDFs, written report) are unaffected since they happen in the
background thread regardless.

Uses the compiled LangGraph's .stream() rather than pipeline.py's own
run_pipeline() (which uses .invoke()), so the web UI can show real
per-node progress instead of one opaque spinner. Every stage name here
maps 1:1 to pipeline.py's actual graph node names, so this can't drift
out of sync with the pipeline's real stages without someone noticing
immediately (an unmapped node name would just show as "pending"
forever instead of progressing).
"""

from __future__ import annotations

import logging
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.pipeline import build_pipeline_graph

logger = logging.getLogger(__name__)

_STAGE_LABELS = {
    "setup_run": "Setting up run folder",
    "fetch_sources": "Fetching sources",
    "dedupe_and_rank": "Deduplicating & ranking",
    "ingest": "Downloading PDFs & extracting sections",
    "summarize": "Summarizing papers",
    "cross_paper_synthesis": "Synthesizing across papers",
    "future_work": "Generating grounded future work",
    "inferred_future_work": "Generating inferred future work",
    "write_report": "Writing report",
}

_STAGE_ORDER = list(_STAGE_LABELS.keys())


@dataclass
class JobState:
    job_id: str
    query: str
    status: str = "running"  # running | done | error
    completed_stages: list[str] = field(default_factory=list)
    error: Optional[str] = None
    run_id: Optional[str] = None


_jobs: dict[str, JobState] = {}
_lock = threading.Lock()


def get_job(job_id: str) -> Optional[JobState]:
    with _lock:
        return _jobs.get(job_id)


def stage_progress(job: JobState) -> list[dict]:
    """
    Full stage list with each stage's status, for the progress
    template. The "current" stage is inferred as the first stage not
    yet in completed_stages — we only learn a stage finished when
    .stream() yields it, so there's no true mid-stage signal, this is
    the standard approximation: mark the next unstarted stage as
    active while the run is still going.
    """
    rows = []
    still_running = job.status == "running"
    reached_current = False
    for stage in _STAGE_ORDER:
        if stage in job.completed_stages:
            status = "done"
        elif still_running and not reached_current:
            status = "current"
            reached_current = True
        else:
            status = "pending"
        rows.append({"key": stage, "label": _STAGE_LABELS[stage], "status": status})
    return rows


def start_job(query: str, config: dict) -> str:
    job_id = uuid.uuid4().hex[:12]
    job = JobState(job_id=job_id, query=query)
    with _lock:
        _jobs[job_id] = job

    thread = threading.Thread(target=_run_job, args=(job, query, config), daemon=True)
    thread.start()
    return job_id


def _run_job(job: JobState, query: str, config: dict) -> None:
    try:
        client = OllamaClient.from_config(config)

        if not client.is_available():
            raise RuntimeError(
                "Ollama server is not reachable. Make sure `ollama serve` is running."
            )
        verified = client.verify_configured_models()
        missing = [tier for tier, ok in verified.items() if not ok]
        if missing:
            raise RuntimeError(f"Configured model(s) for {missing} not found locally.")

        graph = build_pipeline_graph()
        final_state: dict = {}

        for chunk in graph.stream({"query": query, "config": config, "client": client}):
            for node_name, node_output in chunk.items():
                final_state.update(node_output)
                job.completed_stages.append(node_name)

        pipeline_run = final_state.get("pipeline_run")
        if pipeline_run is None or pipeline_run.report_path is None:
            raise RuntimeError("Pipeline finished without producing a report.")

        job.run_id = Path(pipeline_run.report_path).parent.name
        job.status = "done"

    except Exception as exc:  # noqa: BLE001 — any failure should surface to the UI, not vanish
        logger.exception("Web-triggered pipeline run failed for query %r", query)
        job.status = "error"
        job.error = str(exc)