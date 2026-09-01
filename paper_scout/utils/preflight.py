"""
paper_scout.utils.preflight

Startup-time environment checks, run once before the pipeline (CLI or
web) starts accepting real work. Ollama reachability and configured
models are treated as hard errors — nothing in the pipeline works
without them, matching what run_pipeline() already enforces internally.
TTS voice path, ffmpeg, and WeasyPrint are soft warnings, since those
features already degrade gracefully on their own (see qa/stt.py,
qa/tts.py) and shouldn't block a text-only run.

The goal is one clear message at startup instead of a confusing
failure several pipeline stages in.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class PreflightResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True if there are no hard errors. Warnings don't affect this —
        a run can still start with degraded features (no TTS, no PDF)."""
        return not self.errors

    def format(self) -> str:
        lines: list[str] = []
        if self.errors:
            lines.append("Errors (must fix before running):")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("Warnings (some features will be unavailable):")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


def check_ollama(config: dict, client: Optional[OllamaClient] = None) -> PreflightResult:
    result = PreflightResult()
    client = client or OllamaClient.from_config(config)

    if not client.is_available():
        result.errors.append(
            "Ollama server is not reachable. Make sure `ollama serve` is running "
            "before starting the pipeline."
        )
        return result

    verified = client.verify_configured_models()
    missing = [tier for tier, ok in verified.items() if not ok]
    if missing:
        result.errors.append(
            f"Configured model(s) for {missing} not found locally. "
            "Run `ollama pull <model>` for the models named in config.yaml's llm section."
        )
    return result


def check_tts_voice(config: dict) -> PreflightResult:
    result = PreflightResult()
    voice_path = config.get("qa", {}).get("tts_voice_path")

    if not voice_path:
        return result  # not configured — TTS simply won't be offered, nothing to warn about

    if not Path(voice_path).exists():
        result.warnings.append(
            f"Piper TTS voice model not found at {voice_path!r} — spoken answers "
            "will be unavailable until it is downloaded (see README, Requirements)."
        )
    return result


def check_ffmpeg() -> PreflightResult:
    result = PreflightResult()
    if shutil.which("ffmpeg") is None:
        result.warnings.append(
            "ffmpeg was not found on PATH — voice questions (speech-to-text) "
            "will be unavailable until it is installed and added to PATH."
        )
    return result


def check_weasyprint() -> PreflightResult:
    result = PreflightResult()
    try:
        import weasyprint  # noqa: F401
    except OSError as exc:
        # WeasyPrint imports fine but its native deps (GTK3 on Windows) are missing.
        result.warnings.append(
            f"WeasyPrint's system dependencies are missing ({exc}) — PDF report "
            "generation will fail. On Windows, install the GTK3 runtime and restart "
            "your terminal (see README, Requirements)."
        )
    except ImportError:
        result.warnings.append(
            "WeasyPrint is not installed — PDF report generation will be unavailable. "
            "Run `pip install -r requirements.txt`."
        )
    return result


def run_preflight_checks(
    config: dict,
    client: Optional[OllamaClient] = None,
    check_ollama_server: bool = True,
) -> PreflightResult:
    """
    Runs all startup checks and merges them into one PreflightResult.

    check_ollama_server can be set False to skip the Ollama check when
    the caller has already verified it separately (e.g. the CLI's
    --refine-query path constructs and checks a client before this
    would otherwise run again).
    """
    combined = PreflightResult()

    if check_ollama_server:
        r = check_ollama(config, client=client)
        combined.errors.extend(r.errors)
        combined.warnings.extend(r.warnings)

    for check_fn in (check_tts_voice,):
        r = check_fn(config)
        combined.errors.extend(r.errors)
        combined.warnings.extend(r.warnings)

    for check_fn in (check_ffmpeg, check_weasyprint):
        r = check_fn()
        combined.errors.extend(r.errors)
        combined.warnings.extend(r.warnings)

    return combined