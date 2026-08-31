"""
paper_scout.qa.stt

Local speech-to-text via faster-whisper, for the voice-question path
of the report Q&A assistant. Requires ffmpeg on PATH — faster-whisper
uses it to decode browser-recorded audio formats (webm/ogg from
MediaRecorder). See the README for the install note.

Degrades gracefully: returns None on any failure rather than raising,
so a bad/garbled recording surfaces as a friendly message in the UI
instead of a 500 error.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_MODEL_NAME = "tiny.en"

_model = None  # lazy-loaded singleton — loading has real startup cost


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        logger.info("Loading faster-whisper model %r (first use only)", _MODEL_NAME)
        _model = WhisperModel(_MODEL_NAME, device="cpu", compute_type="int8")
    return _model


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """Transcribes a short audio clip (webm/ogg bytes) to text. Returns
    None on any failure — missing ffmpeg, garbled audio, empty result."""
    if not audio_bytes:
        return None

    tmp_path: Optional[Path] = None
    try:
        model = _get_model()
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = Path(tmp.name)

        segments, _info = model.transcribe(str(tmp_path))
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return text or None

    except Exception as exc:  # noqa: BLE001 — never let a bad recording 500 the request
        logger.warning("Speech-to-text failed: %s", exc)
        return None

    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)