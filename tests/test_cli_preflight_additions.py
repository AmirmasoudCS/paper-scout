"""
Additional tests for paper_scout.cli — preflight integration.

Append these to tests/test_cli.py. They reuse that file's existing
patch_logging fixture and _fake_pipeline_run() helper.
"""

from paper_scout.utils.preflight import PreflightResult


def test_main_returns_1_when_preflight_has_errors(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module,
        "run_preflight_checks",
        lambda config: PreflightResult(errors=["Ollama server is not reachable."]),
    )

    called = {"run_pipeline": False}

    def fake_run_pipeline(*args, **kwargs):
        called["run_pipeline"] = True
        return _fake_pipeline_run()

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["some query"])

    assert exit_code == 1
    assert called["run_pipeline"] is False  # must never start the pipeline after a failed preflight
    err = capsys.readouterr().err
    assert "not reachable" in err


def test_main_prints_warnings_but_continues_when_preflight_ok(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module,
        "run_preflight_checks",
        lambda config: PreflightResult(warnings=["ffmpeg was not found on PATH"]),
    )

    def fake_run_pipeline(query, config, client=None, original_query=None):
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["some query"])

    assert exit_code == 0
    err = capsys.readouterr().err
    assert "ffmpeg" in err


def test_main_runs_pipeline_normally_when_preflight_fully_clean(monkeypatch, capsys):
    monkeypatch.setattr(
        cli_module, "run_preflight_checks", lambda config: PreflightResult()
    )

    def fake_run_pipeline(query, config, client=None, original_query=None):
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["some query"])

    assert exit_code == 0
    err = capsys.readouterr().err
    assert err == ""  # nothing to warn about, stderr should be silent