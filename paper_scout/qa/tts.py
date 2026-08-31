"""
paper_scout.qa.tts

Local text-to-speech via Piper, used to speak Q&A answers aloud.
Requires a downloaded Piper voice model (a .onnx file plus its .json
config) — set its path in config.yaml under qa.tts_voice_path.

NOTE: written against the common PiperVoice.load()/voice.synthesize()
API surface, but not verified against a live install as part of this
change — run a quick smoke test after installing piper-tts, and adjust
_get_voice()/synthesize_speech() if your installed version's API
differs.

Degrades gracefully: returns None on any failure (missing voice model,
Piper not installed, synthesis error) rather than raising — the answer
TEXT is always shown regardless, audio is a bonus, never a requirement.
"""

from __future__ import annotations

import io
import logging
import wave
from typing import Optional

logger = logging.getLogger(__name__)

_voice = None
_voice_path_loaded: Optional[str] = None


def _get_voice(voice_path: str):
    global _voice, _voice_path_loaded
    if _voice is None or _voice_path_loaded != voice_path:
        from piper import PiperVoice

        logger.info("Loading Piper voice from %r (first use only)", voice_path)
        _voice = PiperVoice.load(voice_path)
        _voice_path_loaded = voice_path
    return _voice


def synthesize_speech(text: str, voice_path: str) -> Optional[bytes]:
    """Synthesizes text to WAV bytes using the Piper voice at
    voice_path. Returns None on any failure."""
    text = text.strip()
    if not text:
        return None

    try:
        voice = _get_voice(voice_path)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            voice.synthesize(text, wav_file)

        return buffer.getvalue()

    except Exception as exc:  # noqa: BLE001 — audio is a bonus, never block the answer on it
        logger.warning("Text-to-speech failed: %s", exc)
        return None