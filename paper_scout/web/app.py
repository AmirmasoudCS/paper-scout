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

import re

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

_FW_GROUNDED_HEADING_RE = re.compile(r"^## Future Work Ideas$", re.MULTILINE)
_FW_INFERRED_HEADING_RE = re.compile(r"^## Future Work Ideas \(Inferred\)$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^## ", re.MULTILINE)

_FW_GROUNDED_EMPTY_MARKER = "No grounded future-work ideas were generated"
_FW_INFERRED_EMPTY_MARKER = "No inferred future-work ideas were generated"

_FW_LEGEND_HTML = (
    '<div class="fw-legend">'
    '<div class="fw-legend-item"><span class="fw-swatch grounded"></span> '
    "Grounded — traceable to the authors' own words</div>"
    '<div class="fw-legend-item"><span class="fw-swatch inferred"></span> '
    "Inferred — model-derived, not author-stated</div>"
    "</div>\n\n"
)


def _section_body_span(markdown_text: str, heading_re: re.Pattern) -> Optional[tuple[int, int]]:
    """(start, end) char offsets for the section body right after a
    heading matched by heading_re, up to the next '## ' heading or end
    of text. None if the heading isn't present."""
    match = heading_re.search(markdown_text)
    if match is None:
        return None
    body_start = match.end()
    next_heading = _NEXT_HEADING_RE.search(markdown_text, pos=body_start + 1)
    body_end = next_heading.start() if next_heading else len(markdown_text)
    return body_start, body_end


def _wrap_future_work_section(
    markdown_text: str,
    heading_re: re.Pattern,
    css_class: str,
    label: str,
    empty_marker: str,
    prefix_html: str = "",
) -> str:
    span = _section_body_span(markdown_text, heading_re)
    if span is None:
        return markdown_text

    body_start, body_end = span
    body = markdown_text[body_start:body_end]

    if empty_marker in body:
        # Nothing to visually distinguish — leave the "not available" note as plain text.
        return markdown_text

    wrapped = (
        f"\n\n{prefix_html}"
        f'<div class="fw-card {css_class}" markdown="1">\n\n'
        f'<span class="fw-tag {css_class}">{label}</span>\n\n'
        f"{body.strip()}\n\n"
        f"</div>\n\n"
    )
    return markdown_text[:body_start] + wrapped + markdown_text[body_end:]


def _wrap_future_work_sections(markdown_text: str) -> str:
    """
    Wraps the Future Work Ideas / Future Work Ideas (Inferred) section
    bodies in distinguishing containers (solid grounded card, dashed
    inferred card) — the same visual distinction established in the
    design mockup. Only affects this web rendering path: report.md and
    report.pdf are untouched, since raw HTML wrappers with markdown="1"
    won't render correctly on GitHub's plain markdown viewer.
    """
    markdown_text = _wrap_future_work_section(
        markdown_text,
        _FW_GROUNDED_HEADING_RE,
        "grounded",
        "Grounded",
        _FW_GROUNDED_EMPTY_MARKER,
        prefix_html=_FW_LEGEND_HTML,
    )
    markdown_text = _wrap_future_work_section(
        markdown_text,
        _FW_INFERRED_HEADING_RE,
        "inferred",
        "Inferred",
        _FW_INFERRED_EMPTY_MARKER,
    )
    return markdown_text

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