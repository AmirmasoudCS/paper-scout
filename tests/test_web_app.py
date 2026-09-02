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
        lambda query, config, original_query=None: "job123",
    )
    monkeypatch.setattr(
        app_module,
        "get_job",
        lambda job_id: JobState(job_id="job123", query="my topic"),
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


def test_create_run_returns_409_when_a_run_is_already_in_progress(
    client, monkeypatch
):
    monkeypatch.setattr(
        app_module,
        "start_job",
        lambda query, config, original_query=None: None,
    )

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

"""
Additional tests for paper_scout.web.app — preflight integration.

Append these to tests/test_web_app.py. They reuse that file's existing
`client` and `patch_output_dir` fixtures.
"""

from paper_scout.utils.preflight import PreflightResult


# ── startup event ────────────────────────────────────────────────────


def test_startup_event_caches_preflight_result(monkeypatch, patch_output_dir):
    monkeypatch.setattr(
        app_module,
        "run_preflight_checks",
        lambda config: PreflightResult(warnings=["ffmpeg was not found on PATH"]),
    )
    monkeypatch.setattr(app_module, "_last_preflight", None)

    with TestClient(app) as started_client:
        started_client.get("/")  # any request; startup already ran on context entry

    assert app_module._last_preflight is not None
    assert app_module._last_preflight.ok
    assert "ffmpeg" in app_module._last_preflight.warnings[0]


def test_startup_event_caches_errors(monkeypatch, patch_output_dir):
    monkeypatch.setattr(
        app_module,
        "run_preflight_checks",
        lambda config: PreflightResult(errors=["Ollama server is not reachable."]),
    )
    monkeypatch.setattr(app_module, "_last_preflight", None)

    with TestClient(app) as started_client:
        started_client.get("/")

    assert app_module._last_preflight is not None
    assert not app_module._last_preflight.ok


# ── POST /runs blocked by a failed preflight ─────────────────────────


def test_create_run_blocked_when_preflight_failed(client, monkeypatch):
    monkeypatch.setattr(
        app_module,
        "_last_preflight",
        PreflightResult(errors=["Ollama server is not reachable."]),
    )

    response = client.post("/runs", data={"query": "some topic"})

    assert response.status_code == 503
    assert "not reachable" in response.text


def test_create_run_allowed_when_preflight_ok(client, monkeypatch):
    monkeypatch.setattr(app_module, "_last_preflight", PreflightResult())
    monkeypatch.setattr(
        app_module, "start_job", lambda query, config, original_query=None: "job123"
    )
    monkeypatch.setattr(
        app_module, "get_job", lambda job_id: JobState(job_id="job123", query="some topic")
    )
    monkeypatch.setattr(app_module, "stage_progress", lambda job: [])

    response = client.post("/runs", data={"query": "some topic"})

    assert response.status_code == 200


def test_create_run_allowed_when_preflight_never_ran(client, monkeypatch):
    """If _last_preflight is still None (e.g. startup hasn't fired,
    shouldn't happen under normal uvicorn use but worth being
    defensive), create_run must not block on it."""
    monkeypatch.setattr(app_module, "_last_preflight", None)
    monkeypatch.setattr(
        app_module, "start_job", lambda query, config, original_query=None: "job123"
    )
    monkeypatch.setattr(
        app_module, "get_job", lambda job_id: JobState(job_id="job123", query="some topic")
    )
    monkeypatch.setattr(app_module, "stage_progress", lambda job: [])

    response = client.post("/runs", data={"query": "some topic"})

    assert response.status_code == 200


def test_create_run_allowed_when_preflight_has_only_warnings(client, monkeypatch):
    monkeypatch.setattr(
        app_module, "_last_preflight", PreflightResult(warnings=["ffmpeg not found"])
    )
    monkeypatch.setattr(
        app_module, "start_job", lambda query, config, original_query=None: "job123"
    )
    monkeypatch.setattr(
        app_module, "get_job", lambda job_id: JobState(job_id="job123", query="some topic")
    )
    monkeypatch.setattr(app_module, "stage_progress", lambda job: [])

    response = client.post("/runs", data={"query": "some topic"})

    assert response.status_code == 200

"""
Additional tests for paper_scout.web.app — Q&A conversation memory
integration. Append these to tests/test_web_app.py (reuses that
file's `client`, `patch_output_dir` fixtures and `_make_run_dir`
helper). get_qa_history/append_qa_turn are the REAL functions from
runs.py operating on tmp_path, same philosophy as the rest of this
file — only OllamaClient, answer_question, and
build_conversation_context are mocked, since those are what would
otherwise need a live Ollama server.
"""

import json

from unittest.mock import MagicMock


# ── POST /runs/{run_id}/ask ──────────────────────────────────────────


def test_ask_report_persists_the_new_turn(client, monkeypatch, patch_output_dir):
    _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report\n\nSome content.")

    monkeypatch.setattr(app_module.OllamaClient, "from_config", lambda config: MagicMock())
    monkeypatch.setattr(
        app_module, "build_conversation_context", lambda history, client: (None, [], history)
    )
    monkeypatch.setattr(app_module, "answer_question", lambda *a, **k: "The answer is 42.")

    response = client.post(
        "/runs/topic_2026-08-29/ask", data={"question": "What is the answer?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "The answer is 42."

    saved = json.loads((patch_output_dir / "topic_2026-08-29" / "qa_history.json").read_text())
    assert saved["turns"] == [{"question": "What is the answer?", "answer": "The answer is 42."}]


def test_ask_report_passes_conversation_context_to_answer_question(
    client, monkeypatch, patch_output_dir
):
    run_dir = _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report")
    run_dir.joinpath("qa_history.json").write_text(
        json.dumps(
            {
                "turns": [{"question": "q1", "answer": "a1"}],
                "summary": "prior summary",
                "summarized_through": 0,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(app_module.OllamaClient, "from_config", lambda config: MagicMock())
    monkeypatch.setattr(
        app_module,
        "build_conversation_context",
        lambda history, client: (
            "prior summary",
            history["turns"],
            history,
        ),
    )

    captured = {}

    def fake_answer_question(report_markdown, question, client, conversation_summary=None, recent_turns=None):
        captured["conversation_summary"] = conversation_summary
        captured["recent_turns"] = recent_turns
        return "an answer"

    monkeypatch.setattr(app_module, "answer_question", fake_answer_question)

    client.post("/runs/topic_2026-08-29/ask", data={"question": "q2"})

    assert captured["conversation_summary"] == "prior summary"
    assert captured["recent_turns"] == [{"question": "q1", "answer": "a1"}]


def test_ask_report_preserves_updated_summary_after_append(client, monkeypatch, patch_output_dir):
    """If build_conversation_context advances summarized_through/summary
    this request, that progress must survive the subsequent
    append_qa_turn call, not get overwritten by stale state."""
    _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report")

    monkeypatch.setattr(app_module.OllamaClient, "from_config", lambda config: MagicMock())
    monkeypatch.setattr(
        app_module,
        "build_conversation_context",
        lambda history, client: (
            "newly condensed summary",
            [],
            {"turns": history["turns"], "summary": "newly condensed summary", "summarized_through": 5},
        ),
    )
    monkeypatch.setattr(app_module, "answer_question", lambda *a, **k: "an answer")

    client.post("/runs/topic_2026-08-29/ask", data={"question": "a new question"})

    saved = json.loads((patch_output_dir / "topic_2026-08-29" / "qa_history.json").read_text())
    assert saved["summary"] == "newly condensed summary"
    assert saved["summarized_through"] == 5


def test_ask_report_returns_404_for_unknown_run(client):
    response = client.post("/runs/does-not-exist/ask", data={"question": "hi"})
    assert response.status_code == 404


def test_ask_report_rejects_empty_question(client, patch_output_dir):
    _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report")

    response = client.post("/runs/topic_2026-08-29/ask", data={"question": "   "})

    assert response.status_code == 400


# ── GET /runs/{run_id} — ask panel restored via OOB swap ────────────


def test_view_run_includes_saved_qa_history_in_response(client, patch_output_dir):
    run_dir = _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report")
    run_dir.joinpath("qa_history.json").write_text(
        json.dumps(
            {
                "turns": [{"question": "What did they find?", "answer": "A 12% improvement."}],
                "summary": None,
                "summarized_through": 0,
            }
        ),
        encoding="utf-8",
    )

    response = client.get("/runs/topic_2026-08-29")

    assert response.status_code == 200
    assert "What did they find?" in response.text
    assert "A 12% improvement." in response.text
    assert 'id="ask-pane"' in response.text  # OOB swap target present


def test_view_run_shows_empty_thread_when_no_history_yet(client, patch_output_dir):
    _make_run_dir(patch_output_dir, "topic_2026-08-29", report_text="# Report")

    response = client.get("/runs/topic_2026-08-29")

    assert response.status_code == 200
    assert 'id="qa-thread"' in response.text


# ── GET / — initial load restores history for the selected run ─────


def test_index_includes_saved_qa_history_for_most_recent_run(client, patch_output_dir):
    run_dir = _make_run_dir(
        patch_output_dir, "topic_2026-08-29", metadata={"query": "topic"}, report_text="# Report"
    )
    run_dir.joinpath("qa_history.json").write_text(
        json.dumps(
            {
                "turns": [{"question": "earlier question", "answer": "earlier answer"}],
                "summary": None,
                "summarized_through": 0,
            }
        ),
        encoding="utf-8",
    )

    response = client.get("/")

    assert "earlier question" in response.text
    assert "earlier answer" in response.text


def test_index_with_no_runs_does_not_error_on_missing_history(client):
    response = client.get("/")

    assert response.status_code == 200  # no run selected — history defaults, no crash