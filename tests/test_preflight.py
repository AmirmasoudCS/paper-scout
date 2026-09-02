"""
Tests for paper_scout.utils.preflight.

Ollama checks are mocked via a stub client (same pattern as
test_query_refine.py). check_ffmpeg/check_weasyprint are tested by
monkeypatching shutil.which and sys.modules respectively, so no real
ffmpeg install or WeasyPrint/GTK3 setup is required to run these.
"""

from __future__ import annotations

import sys
import types

import pytest

from paper_scout.utils.preflight import (
    PreflightResult,
    check_ffmpeg,
    check_ollama,
    check_tts_voice,
    check_weasyprint,
    run_preflight_checks,
)

SAMPLE_CONFIG = {
    "llm": {
        "small_model": {"name": "qwen3.5:9b"},
        "large_model": {"name": "gemma4:e4b"},
    },
    "qa": {"tts_voice_path": "models/en_US-lessac-medium.onnx"},
}


class _StubClient:
    def __init__(self, available, verified=None):
        self._available = available
        self._verified = verified or {"small": True, "large": True}

    def is_available(self):
        return self._available

    def verify_configured_models(self):
        return self._verified


# ── PreflightResult ─────────────────────────────────────────────────


def test_preflight_result_ok_with_no_errors():
    result = PreflightResult()
    assert result.ok is True


def test_preflight_result_ok_false_with_errors():
    result = PreflightResult(errors=["something broke"])
    assert result.ok is False


def test_preflight_result_ok_true_with_only_warnings():
    result = PreflightResult(warnings=["minor issue"])
    assert result.ok is True


def test_preflight_result_format_includes_errors_and_warnings():
    result = PreflightResult(errors=["bad thing"], warnings=["meh thing"])
    formatted = result.format()

    assert "bad thing" in formatted
    assert "meh thing" in formatted


def test_preflight_result_format_empty_when_nothing_wrong():
    result = PreflightResult()
    assert result.format() == ""


# ── check_ollama ─────────────────────────────────────────────────────


def test_check_ollama_errors_when_server_unreachable():
    client = _StubClient(available=False)

    result = check_ollama(SAMPLE_CONFIG, client=client)

    assert not result.ok
    assert "not reachable" in result.errors[0].lower()


def test_check_ollama_errors_when_model_missing():
    client = _StubClient(available=True, verified={"small": False, "large": True})

    result = check_ollama(SAMPLE_CONFIG, client=client)

    assert not result.ok
    assert "small" in result.errors[0]


def test_check_ollama_passes_when_available_and_models_present():
    client = _StubClient(available=True, verified={"small": True, "large": True})

    result = check_ollama(SAMPLE_CONFIG, client=client)

    assert result.ok
    assert result.errors == []
    assert result.warnings == []


def test_check_ollama_does_not_check_models_when_server_unreachable():
    """If the server itself isn't reachable, verify_configured_models()
    would just fail the same way — no need to call it, and doing so
    would produce a redundant/confusing second error."""
    calls = {"verify": 0}

    class TrackingClient(_StubClient):
        def verify_configured_models(self):
            calls["verify"] += 1
            return super().verify_configured_models()

    client = TrackingClient(available=False)
    check_ollama(SAMPLE_CONFIG, client=client)

    assert calls["verify"] == 0


# ── check_tts_voice ───────────────────────────────────────────────────


def test_check_tts_voice_warns_when_file_missing(tmp_path):
    config = {"qa": {"tts_voice_path": str(tmp_path / "does-not-exist.onnx")}}

    result = check_tts_voice(config)

    assert result.ok  # warning only, not an error
    assert len(result.warnings) == 1
    assert "not found" in result.warnings[0]


def test_check_tts_voice_passes_when_file_exists(tmp_path):
    voice_file = tmp_path / "voice.onnx"
    voice_file.write_bytes(b"fake")
    config = {"qa": {"tts_voice_path": str(voice_file)}}

    result = check_tts_voice(config)

    assert result.ok
    assert result.warnings == []


def test_check_tts_voice_no_warning_when_not_configured():
    result = check_tts_voice({"qa": {}})

    assert result.ok
    assert result.warnings == []


def test_check_tts_voice_no_warning_when_qa_section_missing():
    result = check_tts_voice({})

    assert result.ok
    assert result.warnings == []


# ── check_ffmpeg ──────────────────────────────────────────────────────


def test_check_ffmpeg_warns_when_not_on_path(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)

    result = check_ffmpeg()

    assert result.ok
    assert len(result.warnings) == 1
    assert "ffmpeg" in result.warnings[0].lower()


def test_check_ffmpeg_passes_when_on_path(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")

    result = check_ffmpeg()

    assert result.ok
    assert result.warnings == []


# ── check_weasyprint ──────────────────────────────────────────────────


def test_check_weasyprint_warns_on_missing_native_deps(monkeypatch):
    """Simulates WeasyPrint being pip-installed but its GTK3 system
    libraries missing, which surfaces as an OSError on import."""

    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "weasyprint":
            raise OSError("cannot load library 'gobject-2.0-0'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    result = check_weasyprint()

    assert result.ok  # warning only
    assert len(result.warnings) == 1
    assert "GTK3" in result.warnings[0] or "system dependencies" in result.warnings[0]


def test_check_weasyprint_warns_when_not_installed(monkeypatch):
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "weasyprint":
            raise ImportError("No module named 'weasyprint'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    result = check_weasyprint()

    assert result.ok
    assert len(result.warnings) == 1
    assert "not installed" in result.warnings[0].lower()


def test_check_weasyprint_passes_when_importable(monkeypatch):
    fake_module = types.ModuleType("weasyprint")
    monkeypatch.setitem(sys.modules, "weasyprint", fake_module)

    result = check_weasyprint()

    assert result.ok
    assert result.warnings == []


# ── run_preflight_checks ────────────────────────────────────────────


def test_run_preflight_checks_combines_all_checks(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")
    fake_module = types.ModuleType("weasyprint")
    monkeypatch.setitem(sys.modules, "weasyprint", fake_module)

    config = {**SAMPLE_CONFIG, "qa": {"tts_voice_path": str(tmp_path / "missing.onnx")}}
    client = _StubClient(available=True, verified={"small": True, "large": True})

    result = run_preflight_checks(config, client=client)

    assert result.ok  # only a TTS warning, no hard errors
    assert len(result.warnings) == 1
    assert "not found" in result.warnings[0]


def test_run_preflight_checks_reports_ollama_error(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")
    fake_module = types.ModuleType("weasyprint")
    monkeypatch.setitem(sys.modules, "weasyprint", fake_module)

    client = _StubClient(available=False)

    result = run_preflight_checks(SAMPLE_CONFIG, client=client)

    assert not result.ok
    assert any("not reachable" in e.lower() for e in result.errors)


def test_run_preflight_checks_skips_ollama_when_disabled(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/ffmpeg")
    fake_module = types.ModuleType("weasyprint")
    monkeypatch.setitem(sys.modules, "weasyprint", fake_module)

    calls = {"n": 0}

    class TrackingClient(_StubClient):
        def is_available(self):
            calls["n"] += 1
            return super().is_available()

    client = TrackingClient(available=False)

    result = run_preflight_checks(SAMPLE_CONFIG, client=client, check_ollama_server=False)

    assert calls["n"] == 0
    assert result.ok  # ollama error skipped entirely