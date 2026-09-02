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