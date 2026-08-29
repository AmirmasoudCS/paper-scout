"""
paper_scout.web.app

FastAPI app for browsing and kicking off paper-scout runs. Read-only
browsing (this step) comes first — starting new runs and live progress
are added in a later step, once the browsing experience works end to
end against real output folders.

Run locally with:
    uvicorn paper_scout.web.app:app --reload
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown as md_lib

from paper_scout.web.jobs import get_job, stage_progress, start_job
from paper_scout.utils.config import load_config
from paper_scout.web.runs import get_run, get_run_report_markdown, list_runs

logger = logging.getLogger(__name__)

app = FastAPI(title="paper-scout")

_WEB_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=_WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=_WEB_DIR / "templates")


def _output_dir() -> Path:
    config = load_config()
    return Path(config.get("report", {}).get("output_dir", "outputs"))


def _render_markdown(markdown_text: Optional[str]) -> Optional[str]:
    if markdown_text is None:
        return None
    return md_lib.markdown(markdown_text, extensions=["extra", "sane_lists", "toc"])


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    runs = list_runs(_output_dir())
    selected = runs[0] if runs else None
    report_html = None
    if selected is not None:
        report_html = _render_markdown(get_run_report_markdown(_output_dir(), selected.run_id))

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "runs": runs,
            "selected_run_id": selected.run_id if selected else None,
            "run": selected,
            "report_html": report_html,
        },
    )


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def view_run(request: Request, run_id: str):
    """HTMX partial: swaps the report pane when a sidebar run is clicked."""
    run = get_run(_output_dir(), run_id)
    if run is None:
        return HTMLResponse("<p>Run not found.</p>", status_code=404)

    report_html = _render_markdown(get_run_report_markdown(_output_dir(), run_id))

    return templates.TemplateResponse(
        request,
        "partials/report.html",
        {
            "run": run,
            "report_html": report_html,
        },
    )

@app.post("/runs", response_class=HTMLResponse)
def create_run(request: Request, query: str = Form(...)):
    query = query.strip()
    if not query:
        return HTMLResponse(
            "<p class='body-text'>Please enter a research topic.</p>", status_code=400
        )

    config = load_config()
    job_id = start_job(query, config)

    if job_id is None:
        return HTMLResponse(
            "<p class='body-text'>A run is already in progress. Wait for it to finish before starting another.</p>",
            status_code=409,
        )

    job = get_job(job_id)
    return templates.TemplateResponse(
        request,
        "partials/progress.html",
        {"job_id": job_id, "query": query, "stages": stage_progress(job)},
    )


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_status(request: Request, job_id: str):
    job = get_job(job_id)
    if job is None:
        return HTMLResponse("<p>Unknown job.</p>", status_code=404)

    if job.status == "error":
        return templates.TemplateResponse(
            request, "partials/job_error.html", {"query": job.query, "error": job.error}
        )

    if job.status == "done":
        run = get_run(_output_dir(), job.run_id)
        report_html = _render_markdown(get_run_report_markdown(_output_dir(), job.run_id))
        response = templates.TemplateResponse(
            request, "partials/report.html", {"run": run, "report_html": report_html}
        )
        response.headers["HX-Trigger"] = "runsChanged"
        return response

    return templates.TemplateResponse(
        request,
        "partials/progress.html",
        {"job_id": job_id, "query": job.query, "stages": stage_progress(job)},
    )


@app.get("/partials/run-list", response_class=HTMLResponse)
def run_list_partial(request: Request):
    runs = list_runs(_output_dir())
    return templates.TemplateResponse(
        request, "partials/run_list.html", {"runs": runs, "selected_run_id": None}
    )