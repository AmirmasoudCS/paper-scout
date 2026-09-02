"""
Tests for paper_scout.cli.

Mocks load_config, run_pipeline, OllamaClient, and query refinement so
these run without a live Ollama server or real config.yaml. Follows
the same monkeypatch-the-imported-name pattern as test_pipeline.py.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import paper_scout.cli as cli_module
from paper_scout.llm.query_refine import QueryRefinement
from paper_scout.utils.models import PipelineRun

SAMPLE_CONFIG = {
    "logging": {"log_dir": "log", "level": "INFO"},
    "llm": {
        "small_model": {"name": "qwen3.5:9b"},
        "large_model": {"name": "gemma4:e4b"},
    },
}


@pytest.fixture(autouse=True)
def patch_logging(monkeypatch, tmp_path):
    """Avoid writing real log files into the repo during tests."""
    config = {**SAMPLE_CONFIG, "logging": {"log_dir": str(tmp_path / "log"), "level": "INFO"}}
    monkeypatch.setattr(cli_module, "load_config", lambda path: config)
    return config


def _fake_pipeline_run(query="test query") -> PipelineRun:
    return PipelineRun(query=query, papers=[], report_path="outputs/test-query_2026-08-29/report.md")


# ── main(): basic flow, no refinement ──────────────────────────────


def test_main_without_refine_flag_runs_pipeline_with_original_query(monkeypatch, capsys):
    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["original_query"] = original_query
        captured["client"] = client
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["diffusion models for audio"])

    assert exit_code == 0
    assert captured["query"] == "diffusion models for audio"
    assert captured["original_query"] is None
    assert captured["client"] is None  # refinement never ran, so no client was built
    out = capsys.readouterr().out
    assert "Researching: diffusion models for audio" in out
    assert "Report written to:" in out


def test_main_returns_1_on_missing_config(monkeypatch):
    monkeypatch.setattr(
        cli_module, "load_config", lambda path: (_ for _ in ()).throw(FileNotFoundError("no config"))
    )

    exit_code = cli_module.main(["some query"])

    assert exit_code == 1


def test_main_returns_1_when_pipeline_raises_runtime_error(monkeypatch, capsys):
    def fake_run_pipeline(query, config, client=None, original_query=None):
        raise RuntimeError("Ollama server is not reachable.")

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["some query"])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "not reachable" in err


def test_main_returns_1_on_unexpected_exception(monkeypatch, capsys):
    def fake_run_pipeline(query, config, client=None, original_query=None):
        raise ValueError("something broke")

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["some query"])

    assert exit_code == 1
    err = capsys.readouterr().err
    assert "Something went wrong" in err


# ── main(): --refine-query flag ────────────────────────────────────


def test_main_with_refine_flag_skips_refinement_when_ollama_unavailable(monkeypatch, capsys):
    mock_client = MagicMock()
    mock_client.is_available.return_value = False
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["client"] = client
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "some querry"])

    assert exit_code == 0
    assert captured["query"] == "some querry"  # unchanged, refinement was skipped
    err = capsys.readouterr().err
    assert "not reachable" in err.lower()


def test_main_with_refine_flag_accepts_suggestion_on_enter(monkeypatch, capsys):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="difusion modles", refined="diffusion models", changed=True
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)
    monkeypatch.setattr("builtins.input", lambda prompt="": "")  # press Enter

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["original_query"] = original_query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "difusion modles"])

    assert exit_code == 0
    assert captured["query"] == "diffusion models"
    assert captured["original_query"] == "difusion modles"


def test_main_with_refine_flag_uses_custom_edit(monkeypatch):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="difusion modles", refined="diffusion models", changed=True
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)
    monkeypatch.setattr("builtins.input", lambda prompt="": "diffusion models for speech")

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["original_query"] = original_query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    cli_module.main(["--refine-query", "difusion modles"])

    assert captured["query"] == "diffusion models for speech"
    assert captured["original_query"] == "difusion modles"


def test_main_with_refine_flag_cancel_keeps_original(monkeypatch):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="difusion modles", refined="diffusion models", changed=True
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)
    monkeypatch.setattr("builtins.input", lambda prompt="": "cancel")

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["original_query"] = original_query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    cli_module.main(["--refine-query", "difusion modles"])

    assert captured["query"] == "difusion modles"
    assert captured["original_query"] is None


def test_main_with_refine_flag_and_no_change_needed(monkeypatch, capsys):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(original="clean query", refined="clean query", changed=False)
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        captured["original_query"] = original_query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "clean query"])

    assert exit_code == 0
    assert captured["query"] == "clean query"
    assert captured["original_query"] is None
    out = capsys.readouterr().out
    assert "already looked good" in out


def test_main_with_refine_flag_and_failed_refinement_falls_back(monkeypatch, capsys):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="some query", refined=None, changed=False, error="model unreachable"
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "some query"])

    assert exit_code == 0
    assert captured["query"] == "some query"
    out = capsys.readouterr().out
    assert "Could not refine" in out
    assert "model unreachable" in out


def test_main_with_refine_flag_ctrl_c_during_prompt_aborts(monkeypatch, capsys):
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="difusion modles", refined="diffusion models", changed=True
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)

    def raise_keyboard_interrupt(prompt=""):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", raise_keyboard_interrupt)

    called = {"run_pipeline": False}

    def fake_run_pipeline(*args, **kwargs):
        called["run_pipeline"] = True
        return _fake_pipeline_run()

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "difusion modles"])

    assert exit_code == 130
    assert called["run_pipeline"] is False  # pipeline must never start after an abort


def test_main_with_refine_flag_eof_during_prompt_uses_suggestion(monkeypatch):
    """Non-interactive input (e.g. piped stdin) should fall back to the
    suggested query rather than hang or crash."""
    mock_client = MagicMock()
    mock_client.is_available.return_value = True
    monkeypatch.setattr(cli_module.OllamaClient, "from_config", lambda config: mock_client)

    refinement = QueryRefinement(
        original="difusion modles", refined="diffusion models", changed=True
    )
    monkeypatch.setattr(cli_module, "refine_search_query", lambda raw, client: refinement)

    def raise_eof(prompt=""):
        raise EOFError()

    monkeypatch.setattr("builtins.input", raise_eof)

    captured = {}

    def fake_run_pipeline(query, config, client=None, original_query=None):
        captured["query"] = query
        return _fake_pipeline_run(query)

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)

    exit_code = cli_module.main(["--refine-query", "difusion modles"])

    assert exit_code == 0
    assert captured["query"] == "diffusion models"

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