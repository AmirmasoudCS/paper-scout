"""
Unit tests for paper_scout.qa (answer, stt, tts).

Each module is designed to never raise, missing models, unreachable
Ollama, garbled audio, or missing Piper voices should all degrade to a
friendly fallback (a string for answer.py, None for stt.py/tts.py)
rather than a 500 in the web layer. These tests mock the underlying
model/client calls directly, in the same style as test_llm.py and
test_query_refine.py, so no real Ollama server, ffmpeg, or Piper voice
model is required to run them.
"""

from __future__ import annotations

import wave

import pytest

from paper_scout.qa import answer as answer_module
from paper_scout.qa import stt as stt_module
from paper_scout.qa import tts as tts_module
from paper_scout.qa.answer import answer_question
from paper_scout.qa.stt import transcribe_audio
from paper_scout.qa.tts import synthesize_speech


# ── answer_question ───────────────────────────────────────────────────


class _StubClient:
    """Minimal stand-in for OllamaClient.generate_large."""

    def __init__(self, response):
        self._response = response
        self.calls = []

    def generate_large(self, prompt, system=None):
        self.calls.append((prompt, system))
        return self._response


def test_answer_question_returns_model_output_on_success():
    client = _StubClient("The paper reports a 12% accuracy improvement.")

    result = answer_question("## Results\n...", "What accuracy did they report?", client)

    assert result == "The paper reports a 12% accuracy improvement."


def test_answer_question_strips_whitespace():
    client = _StubClient("   padded answer   ")

    result = answer_question("report text", "a question", client)

    assert result == "padded answer"


def test_answer_question_calls_client_once_with_prompt_and_system():
    client = _StubClient("some answer")

    answer_question("report text", "a question", client)

    assert len(client.calls) == 1
    prompt, system = client.calls[0]
    assert prompt is not None
    assert system is not None


def test_answer_question_falls_back_when_client_returns_none():
    client = _StubClient(None)

    result = answer_question("report text", "a question", client)

    assert "couldn't reach" in result.lower()


def test_answer_question_falls_back_on_empty_response():
    client = _StubClient("")

    result = answer_question("report text", "a question", client)

    assert "couldn't reach" in result.lower()


def test_answer_question_falls_back_on_too_short_response():
    client = _StubClient("ok")  # 2 chars, below _MIN_VALID_ANSWER_CHARS (3)

    result = answer_question("report text", "a question", client)

    assert "couldn't reach" in result.lower()


def test_answer_question_accepts_response_at_minimum_length():
    client = _StubClient("yes")  # exactly 3 chars

    result = answer_question("report text", "a question", client)

    assert result == "yes"


def test_answer_question_never_raises_on_client_exception(monkeypatch):
    """answer_question is documented as never raising. If build_qa_prompt
    or the client blow up unexpectedly, that's a bug elsewhere, but this
    locks in that a client returning None (its documented failure mode)
    is handled, rather than letting an exception surface as a 500."""

    class ExplodingClient:
        def generate_large(self, prompt, system=None):
            return None

    result = answer_question("report text", "a question", ExplodingClient())

    assert isinstance(result, str)
    assert len(result) > 0


# ── transcribe_audio ─────────────────────────────────────────────────


class _FakeSegment:
    def __init__(self, text):
        self.text = text


class _FakeWhisperModel:
    def __init__(self, segments):
        self._segments = segments

    def transcribe(self, path):
        return self._segments, {}


def test_transcribe_audio_returns_none_for_empty_bytes():
    assert transcribe_audio(b"") is None


def test_transcribe_audio_joins_segment_text(monkeypatch):
    fake_model = _FakeWhisperModel([_FakeSegment(" hello "), _FakeSegment("world ")])
    monkeypatch.setattr(stt_module, "_get_model", lambda: fake_model)

    result = transcribe_audio(b"fake-audio-bytes")

    assert result == "hello world"


def test_transcribe_audio_returns_none_when_no_segments(monkeypatch):
    fake_model = _FakeWhisperModel([])
    monkeypatch.setattr(stt_module, "_get_model", lambda: fake_model)

    result = transcribe_audio(b"fake-audio-bytes")

    assert result is None


def test_transcribe_audio_returns_none_on_model_load_failure(monkeypatch):
    def raise_error():
        raise RuntimeError("ffmpeg not found")

    monkeypatch.setattr(stt_module, "_get_model", raise_error)

    result = transcribe_audio(b"fake-audio-bytes")

    assert result is None


def test_transcribe_audio_returns_none_on_transcribe_failure(monkeypatch):
    class BrokenModel:
        def transcribe(self, path):
            raise RuntimeError("garbled audio")

    monkeypatch.setattr(stt_module, "_get_model", lambda: BrokenModel())

    result = transcribe_audio(b"fake-audio-bytes")

    assert result is None


def test_transcribe_audio_cleans_up_temp_file(monkeypatch, tmp_path):
    """The temp file written for faster-whisper to read should be deleted
    afterward, regardless of success or failure."""
    written_paths = []

    class TrackingModel:
        def transcribe(self, path):
            written_paths.append(path)
            return [_FakeSegment("text")], {}

    monkeypatch.setattr(stt_module, "_get_model", lambda: TrackingModel())

    transcribe_audio(b"fake-audio-bytes")

    assert len(written_paths) == 1
    from pathlib import Path

    assert not Path(written_paths[0]).exists()


# ── synthesize_speech ────────────────────────────────────────────────


class _FakeVoice:
    """Writes a minimal valid WAV so wave.open() doesn't choke, mirroring
    what PiperVoice.synthesize_wav() does to the passed-in wave.Wave_write."""

    def synthesize_wav(self, text, wav_file, syn_config=None):
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes(b"\x00\x00" * 100)


class _ExplodingVoice:
    def synthesize_wav(self, text, wav_file, syn_config=None):
        raise RuntimeError("synthesis failed")


def test_synthesize_speech_returns_none_for_empty_text():
    assert synthesize_speech("", "models/voice.onnx") is None


def test_synthesize_speech_returns_none_when_text_is_only_markup():
    # Bullets and asterisks with nothing left after cleaning.
    assert synthesize_speech("* **", "models/voice.onnx") is None


def test_synthesize_speech_returns_wav_bytes_on_success(monkeypatch):
    monkeypatch.setattr(tts_module, "_get_voice", lambda voice_path: _FakeVoice())

    result = synthesize_speech("Hello world.", "models/voice.onnx")

    assert result is not None
    assert result.startswith(b"RIFF")  # WAV file signature


def test_synthesize_speech_returns_none_on_voice_load_failure(monkeypatch):
    def raise_error(voice_path):
        raise RuntimeError("voice model not found")

    monkeypatch.setattr(tts_module, "_get_voice", raise_error)

    result = synthesize_speech("Hello world.", "models/missing.onnx")

    assert result is None


def test_synthesize_speech_returns_none_on_synthesis_failure(monkeypatch):
    monkeypatch.setattr(tts_module, "_get_voice", lambda voice_path: _ExplodingVoice())

    result = synthesize_speech("Hello world.", "models/voice.onnx")

    assert result is None


def test_synthesize_speech_strips_markdown_bold_and_italic(monkeypatch):
    captured = {}

    class CapturingVoice:
        def synthesize_wav(self, text, wav_file, syn_config=None):
            captured["text"] = text
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(b"\x00\x00")

    monkeypatch.setattr(tts_module, "_get_voice", lambda voice_path: CapturingVoice())

    synthesize_speech("This is **bold** and *italic* text.", "models/voice.onnx")

    assert "**" not in captured["text"]
    assert "*" not in captured["text"]
    assert "bold" in captured["text"]
    assert "italic" in captured["text"]


def test_synthesize_speech_strips_citation_brackets(monkeypatch):
    captured = {}

    class CapturingVoice:
        def synthesize_wav(self, text, wav_file, syn_config=None):
            captured["text"] = text
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(b"\x00\x00")

    monkeypatch.setattr(tts_module, "_get_voice", lambda voice_path: CapturingVoice())

    synthesize_speech("Grounded in prior work [1, 2].", "models/voice.onnx")

    assert "[1" not in captured["text"]
    assert "prior work" in captured["text"]


def test_synthesize_speech_strips_leading_bullet_markers(monkeypatch):
    captured = {}

    class CapturingVoice:
        def synthesize_wav(self, text, wav_file, syn_config=None):
            captured["text"] = text
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(22050)
            wav_file.writeframes(b"\x00\x00")

    monkeypatch.setattr(tts_module, "_get_voice", lambda voice_path: CapturingVoice())

    synthesize_speech("- first point\n- second point", "models/voice.onnx")

    assert "- first" not in captured["text"]
    assert "first point" in captured["text"]


def test_synthesize_speech_reloads_voice_when_path_changes(monkeypatch):
    load_calls = []

    def fake_get_voice(voice_path):
        load_calls.append(voice_path)
        return _FakeVoice()

    monkeypatch.setattr(tts_module, "_get_voice", fake_get_voice)

    synthesize_speech("Hello.", "models/voice_a.onnx")
    synthesize_speech("Hello.", "models/voice_b.onnx")

    assert load_calls == ["models/voice_a.onnx", "models/voice_b.onnx"]

"""
Additional tests for paper_scout.qa.answer — conversation-context
passthrough. Append these to tests/test_qa.py (reuses that file's
_StubClient class and imports).
"""


def test_answer_question_passes_conversation_summary_to_prompt():
    client = _StubClient("some answer")

    answer_question(
        "report text",
        "a question",
        client,
        conversation_summary="Earlier the user asked about X.",
    )

    prompt, system = client.calls[0]
    assert "Earlier the user asked about X." in prompt


def test_answer_question_passes_recent_turns_to_prompt():
    client = _StubClient("some answer")

    answer_question(
        "report text",
        "a question",
        client,
        recent_turns=[{"question": "what is X?", "answer": "X is a method."}],
    )

    prompt, system = client.calls[0]
    assert "what is X?" in prompt
    assert "X is a method." in prompt


def test_answer_question_works_without_any_history():
    """Existing single-turn callers (no conversation_summary/recent_turns
    passed) must keep working unchanged."""
    client = _StubClient("some answer")

    result = answer_question("report text", "a question", client)

    assert result == "some answer"
    prompt, system = client.calls[0]
    assert "Earlier in this conversation" not in prompt
    assert "Most recent turns" not in prompt