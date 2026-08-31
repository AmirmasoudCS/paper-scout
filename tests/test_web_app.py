"""
Tests for paper_scout.web.app — route-level tests using FastAPI's
TestClient. load_config() is mocked to point at tmp_path, but list_runs
/get_run/get_run_report_markdown are the REAL functions from runs.py
running against real files written to tmp_path, so these exercise real
template rendering end to end. jobs.py's start_job/get_job/stage_progress
are mocked directly, since exercising the real background-thread/
pipeline path belongs in test_web_jobs.py, not here.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import paper_scout.web.app as app_module
from paper_scout.web.app import app
from paper_scout.web.jobs import JobState


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def patch_output_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(
        app_module, "load_config", lambda: {"report": {"output_dir": str(tmp_path)}}
    )
    return tmp_path


def _make_run_dir(tmp_path, name, metadata=None, report_text="# Report\n\nSome content."):
    run_dir = tmp_path / name
    run_dir.mkdir()
    if metadata is not None:
        (run_dir / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (run_dir / "report.md").write_text(report_text, encoding="utf-8")
    return run_dir


# ── GET / ──────────────────────────────────────────────────────────


def test_index_with_no_runs_shows_empty_state(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "No runs yet" in response.text


def test_index_shows_most_recent_run_by_default(client, patch_output_dir):
    _make_run_dir(
        patch_output_dir,
        "diffusion-models_2026-08-28",
        metadata={"query": "diffusion models", "paper_count": 5},
        report_text="# Research Report\n\n## Cross-Paper Synthesis\n\nSome synthesis text.",
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "diffusion models" in response.text
    assert "Some synthesis text" in response.text


def test_index_renders_markdown_headings_with_ids_for_toc(client, patch_output_dir):
    _make_run_dir(
        patch_output_dir,
        "topic_2026-08-29",
        metadata={"query": "topic"},
        report_text="## Cross-Paper Synthesis\n\nBody text here.",
    )

    response = client.get("/")

    # the toc extension should give the heading an id matching report_writer's anchor scheme
    assert 'id="cross-paper-synthesis"' in response.text


# ── GET /runs/{run_id} ────────────────────────────────────────────


def test_view_run_returns_report_partial(client, patch_output_dir):
    _make_run_dir(
        patch_output_dir,
        "topic_2026-08-29",
        metadata={"query": "topic", "paper_count": 3},
        report_text="# Report\n\nUnique marker text here.",
    )

    response = client.get("/runs/topic_2026-08-29")

    assert response.status_code == 200
    assert "Unique marker text here" in response.text


def test_view_run_returns_404_for_unknown_run(client):
    response = client.get("/runs/does-not-exist")
    assert response.status_code == 404


# ── POST /runs ─────────────────────────────────────────────────────


def test_create_run_rejects_empty_query(client):
    response = client.post("/runs", data={"query": "   "})
    assert response.status_code == 400
    assert "Please enter a research topic" in response.text


def test_create_run_starts_job_and_returns_progress_view(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "start_job",
        lambda *args, **kwargs: "job123",
    )

    monkeypatch.setattr(
        app_module,
        "get_job",
        lambda job_id: JobState(job_id="job123", query="my topic")
    )

    monkeypatch.setattr(
        app_module,
        "stage_progress",
        lambda job: [
            {
                "key": "fetch_sources",
                "label": "Fetching sources",
                "status": "current",
            }
        ],
    )

    response = client.post("/runs", data={"query": "my topic"})

    assert response.status_code == 200
    assert "my topic" in response.text
    assert "Fetching sources" in response.text


def test_create_run_returns_409_when_a_run_is_already_in_progress(client, monkeypatch):
    monkeypatch.setattr(app_module, "start_job", lambda query, config: None)

    response = client.post("/runs", data={"query": "another topic"})

    assert response.status_code == 409
    assert "already in progress" in response.text


# ── GET /jobs/{job_id} ─────────────────────────────────────────────


def test_job_status_returns_404_for_unknown_job(client, monkeypatch):
    monkeypatch.setattr(app_module, "get_job", lambda job_id: None)

    response = client.get("/jobs/unknown")

    assert response.status_code == 404


def test_job_status_returns_progress_view_while_running(client, monkeypatch):
    job = JobState(job_id="job123", query="my topic", status="running")
    monkeypatch.setattr(app_module, "get_job", lambda job_id: job)
    monkeypatch.setattr(
        app_module,
        "stage_progress",
        lambda j: [{"key": "summarize", "label": "Summarizing papers", "status": "current"}],
    )

    response = client.get("/jobs/job123")

    assert response.status_code == 200
    assert "Summarizing papers" in response.text


def test_job_status_returns_error_view_when_job_failed(client, monkeypatch):
    job = JobState(job_id="job123", query="my topic", status="error", error="Ollama not reachable")
    monkeypatch.setattr(app_module, "get_job", lambda job_id: job)

    response = client.get("/jobs/job123")

    assert response.status_code == 200
    assert "Run failed" in response.text
    assert "Ollama not reachable" in response.text


def test_job_status_returns_report_and_triggers_sidebar_refresh_when_done(
    client, monkeypatch, patch_output_dir
):
    _make_run_dir(
        patch_output_dir,
        "my-topic_2026-08-29",
        metadata={"query": "my topic", "paper_count": 7},
        report_text="# Report\n\nFinished run content.",
    )
    job = JobState(job_id="job123", query="my topic", status="done", run_id="my-topic_2026-08-29")
    monkeypatch.setattr(app_module, "get_job", lambda job_id: job)

    response = client.get("/jobs/job123")

    assert response.status_code == 200
    assert "Finished run content" in response.text
    assert response.headers.get("HX-Trigger") == "runsChanged"


# ── GET /partials/run-list ─────────────────────────────────────────


def test_run_list_partial_reflects_real_runs(client, patch_output_dir):
    _make_run_dir(patch_output_dir, "topic-a_2026-08-29", metadata={"query": "topic a"})
    _make_run_dir(patch_output_dir, "topic-b_2026-08-28", metadata={"query": "topic b"})

    response = client.get("/partials/run-list")

    assert response.status_code == 200
    assert "topic a" in response.text
    assert "topic b" in response.text


def test_run_list_partial_shows_empty_state_when_no_runs(client):
    response = client.get("/partials/run-list")

    assert response.status_code == 200
    assert "No runs yet" in response.text

def test_index_renders_grounded_and_inferred_future_work_as_distinct_cards(client, patch_output_dir):
    report_text = (
        "# Research Report\n\n"
        "## Future Work Ideas\n\n"
        "1. Multilingual grounding — extend beyond English-only evaluation.\n\n"
        "## Future Work Ideas (Inferred)\n\n"
        "[Inferred, not author-stated] Cross-lingual transfer.\n\n"
        "## Papers\n\n"
        "Some paper content.\n"
    )
    _make_run_dir(
        patch_output_dir, "topic_2026-08-29", metadata={"query": "topic"}, report_text=report_text
    )

    response = client.get("/")

    assert 'class="fw-card grounded"' in response.text
    assert 'class="fw-card inferred"' in response.text
    assert "Multilingual grounding" in response.text
    assert "Cross-lingual transfer" in response.text


def test_index_does_not_wrap_future_work_section_when_no_ideas_generated(client, patch_output_dir):
    report_text = (
        "# Research Report\n\n"
        "## Future Work Ideas\n\n"
        "*No grounded future-work ideas were generated for this run — this can happen "
        "if no paper had extractable Limitations/Future Work sections.*\n\n"
        "## Papers\n\n"
        "Some paper content.\n"
    )
    _make_run_dir(
        patch_output_dir, "topic_2026-08-29", metadata={"query": "topic"}, report_text=report_text
    )

    response = client.get("/")

    assert 'class="fw-card grounded"' not in response.text
    assert "No grounded future-work ideas" in response.text