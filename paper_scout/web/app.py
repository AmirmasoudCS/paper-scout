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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown as md_lib

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
    return md_lib.markdown(markdown_text, extensions=["extra", "sane_lists"])


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    runs = list_runs(_output_dir())
    selected = runs[0] if runs else None
    report_html = None
    if selected is not None:
        report_html = _render_markdown(get_run_report_markdown(_output_dir(), selected.run_id))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "runs": runs,
            "selected_run_id": selected.run_id if selected else None,
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
        "partials/report.html",
        {
            "request": request,
            "run": run,
            "report_html": report_html,
        },
    )