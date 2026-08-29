"""
Tests for paper_scout.web.jobs.

Uses a fake compiled graph (matching the .stream() contract LangGraph's
compiled graph exposes) so these run without Ollama or the real
pipeline — same mocking philosophy as test_pipeline.py.
"""

from __future__ import annotations

import time

import pytest

from paper_scout.web import jobs as jobs_module
from paper_scout.utils.models import PipelineRun


@pytest.fixture(autouse=True)
def reset_jobs_module():
    """jobs.py uses module-level state (a dict + an active-job flag),
    so each test needs a clean slate."""
    jobs_module._jobs.clear()
    jobs_module._active_job_id = None
    yield
    jobs_module._jobs.clear()
    jobs_module._active_job_id = None


class _FakeClient:
    def is_available(self):
        return True

    def verify_configured_models(self):
        return {"small": True, "large": True}


class _FakeGraph:
    """Fake compiled graph whose .stream() yields controllable chunks."""

    def __init__(self, chunks, delay=0.0):
        self._chunks = chunks
        self._delay = delay

    def stream(self, initial_state):
        for chunk in self._chunks:
            if self._delay:
                time.sleep(self._delay)
            yield chunk


def _make_pipeline_run(report_path="outputs/some-query_2026-08-29/report.md") -> PipelineRun:
    return PipelineRun(query="some query", report_path=report_path)


def test_start_job_returns_job_id_and_job_is_tracked(monkeypatch):
    fake_graph = _FakeGraph([{"write_report": {"pipeline_run": _make_pipeline_run()}}])
    monkeypatch.setattr(jobs_module, "build_pipeline_graph", lambda: fake_graph)
    monkeypatch.setattr(jobs_module, "OllamaClient", type("C", (), {"from_config": staticmethod(lambda cfg: _FakeClient())}))

    job_id = jobs_module.start_job("some query", {})
    assert job_id is not None

    # give the background thread a moment to finish
    time.sleep(0.1)
    job = jobs_module.get_job(job_id)
    assert job is not None
    assert job.status == "done"
    assert job.run_id == "some-query_2026-08-29"


def test_start_job_refuses_second_run_while_one_in_progress(monkeypatch):
    fake_graph = _FakeGraph(
        [{"write_report": {"pipeline_run": _make_pipeline_run()}}], delay=0.3
    )
    monkeypatch.setattr(jobs_module, "build_pipeline_graph", lambda: fake_graph)
    monkeypatch.setattr(jobs_module, "OllamaClient", type("C", (), {"from_config": staticmethod(lambda cfg: _FakeClient())}))

    first_id = jobs_module.start_job("first query", {})
    assert first_id is not None
    assert jobs_module.is_run_in_progress() is True

    second_id = jobs_module.start_job("second query", {})
    assert second_id is None  # refused, since first is still running

    time.sleep(0.5)  # let the first job finish
    assert jobs_module.is_run_in_progress() is False


def test_active_job_clears_after_job_errors(monkeypatch):
    class _UnavailableClient:
        def is_available(self):
            return False

    monkeypatch.setattr(jobs_module, "build_pipeline_graph", lambda: _FakeGraph([]))
    monkeypatch.setattr(
        jobs_module, "OllamaClient", type("C", (), {"from_config": staticmethod(lambda cfg: _UnavailableClient())})
    )

    job_id = jobs_module.start_job("bad query", {})
    time.sleep(0.1)

    job = jobs_module.get_job(job_id)
    assert job.status == "error"
    assert "not reachable" in job.error
    assert jobs_module.is_run_in_progress() is False  # lock released even on failure


def test_start_job_allows_new_run_after_previous_completes(monkeypatch):
    fake_graph = _FakeGraph([{"write_report": {"pipeline_run": _make_pipeline_run()}}])
    monkeypatch.setattr(jobs_module, "build_pipeline_graph", lambda: fake_graph)
    monkeypatch.setattr(jobs_module, "OllamaClient", type("C", (), {"from_config": staticmethod(lambda cfg: _FakeClient())}))

    first_id = jobs_module.start_job("first", {})
    time.sleep(0.1)

    second_id = jobs_module.start_job("second", {})
    assert second_id is not None
    assert second_id != first_id


def test_stage_progress_marks_completed_and_current_stages():
    job = jobs_module.JobState(job_id="abc", query="x")
    job.completed_stages = ["setup_run", "fetch_sources"]

    rows = jobs_module.stage_progress(job)

    by_key = {r["key"]: r["status"] for r in rows}
    assert by_key["setup_run"] == "done"
    assert by_key["fetch_sources"] == "done"
    assert by_key["dedupe_and_rank"] == "current"
    assert by_key["write_report"] == "pending"


def test_stage_progress_all_done_when_job_finished():
    job = jobs_module.JobState(job_id="abc", query="x", status="done")
    job.completed_stages = list(jobs_module._STAGE_ORDER)

    rows = jobs_module.stage_progress(job)

    assert all(r["status"] == "done" for r in rows)


def test_get_job_returns_none_for_unknown_id():
    assert jobs_module.get_job("does-not-exist") is None