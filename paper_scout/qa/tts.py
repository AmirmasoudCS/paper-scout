"""
paper_scout.qa.tts

Local text-to-speech via Piper, used to speak Q&A answers aloud.
Requires a downloaded Piper voice model (a .onnx file plus its .json
config) — set its path in config.yaml under qa.tts_voice_path.

Uses PiperVoice.synthesize_wav(), which writes a properly-configured
WAV file (sets channels/sample width/frame rate from the first audio
chunk automatically) — confirmed against the installed piper-tts
source. voice.synthesize() alone is a generator yielding raw audio
chunks with no WAV header, calling it directly against a bare
wave.Wave_write raises "# channels not specified".

Degrades gracefully: returns None on any failure (missing voice model,
Piper not installed, synthesis error) rather than raising — the answer
TEXT is always shown regardless, audio is a bonus, never a requirement.
"""

from __future__ import annotations

import io
import logging
import wave
import re
from typing import Optional
from piper.config import SynthesisConfig


logger = logging.getLogger(__name__)

_voice = None
_voice_path_loaded: Optional[str] = None

_DEFAULT_SYN_CONFIG = SynthesisConfig(length_scale=1.15)  # >1.0 = slower, 1.0 = default pace

_MD_BOLD_RE = re.compile(r"\*\*(.*?)\*\*")
_MD_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)")
_CITATION_RE = re.compile(r"\s*\[\d+(?:,\s*\d+)*\]")
_MULTI_SPACE_RE = re.compile(r" {2,}")


def _clean_text_for_speech(text: str) -> str:
    """Strips markdown emphasis and citation brackets before synthesis
    — Piper reads raw markup literally (e.g. "asterisk asterisk"), and
    citation numbers like [3] add no value spoken aloud."""
    text = _CITATION_RE.sub("", text)
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_ITALIC_RE.sub(r"\1", text)
    text = _MULTI_SPACE_RE.sub(" ", text)
    return text.strip()

def _get_voice(voice_path: str):
    global _voice, _voice_path_loaded
    if _voice is None or _voice_path_loaded != voice_path:
        from piper import PiperVoice

        logger.info("Loading Piper voice from %r (first use only)", voice_path)
        _voice = PiperVoice.load(voice_path)
        _voice_path_loaded = voice_path
    return _voice


def synthesize_speech(text: str, voice_path: str) -> Optional[bytes]:
    text = _clean_text_for_speech(text)
    if not text:
        return None

    try:
        voice = _get_voice(voice_path)

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file, syn_config=_DEFAULT_SYN_CONFIG)

        return buffer.getvalue()

    except Exception as exc:  # noqa: BLE001
        logger.warning("Text-to-speech failed: %s", exc)
        return None