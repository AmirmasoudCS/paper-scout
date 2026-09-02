"""Tests for paper_scout.web.runs — pure filesystem reads, no network/LLM."""

from __future__ import annotations

import json

from paper_scout.web.runs import get_run, get_run_report_markdown, list_runs
from paper_scout.web.runs import get_qa_history, save_qa_history, append_qa_turn


def _make_run_dir(tmp_path, name, metadata=None, report_text=None):
    run_dir = tmp_path / name
    run_dir.mkdir()
    if metadata is not None:
        (run_dir / "run_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    if report_text is not None:
        (run_dir / "report.md").write_text(report_text, encoding="utf-8")
        (run_dir / "report.pdf").write_bytes(b"%PDF-1.4 fake")
    return run_dir


def test_list_runs_returns_empty_list_when_output_dir_missing(tmp_path):
    missing = tmp_path / "does_not_exist"
    assert list_runs(missing) == []


def test_list_runs_reads_metadata_for_each_run(tmp_path):
    _make_run_dir(
        tmp_path,
        "diffusion-models_2026-08-28",
        metadata={"query": "diffusion models", "paper_count": 12, "sources": {}},
        report_text="# Report",
    )

    runs = list_runs(tmp_path)

    assert len(runs) == 1
    assert runs[0].query == "diffusion models"
    assert runs[0].paper_count == 12
    assert runs[0].has_report is True
    assert runs[0].has_pdf is True


def test_list_runs_falls_back_to_folder_name_when_metadata_missing(tmp_path):
    _make_run_dir(tmp_path, "sensory-design-in-campuses_2026-08-20")

    runs = list_runs(tmp_path)

    assert len(runs) == 1
    assert runs[0].query == "sensory design in campuses"
    assert runs[0].paper_count == 0
    assert runs[0].has_report is False


def test_list_runs_survives_corrupted_metadata_json(tmp_path):
    run_dir = tmp_path / "broken_2026-08-20"
    run_dir.mkdir()
    (run_dir / "run_metadata.json").write_text("{not valid json", encoding="utf-8")

    runs = list_runs(tmp_path)

    assert len(runs) == 1
    assert runs[0].run_id == "broken_2026-08-20"


def test_list_runs_orders_most_recent_first(tmp_path):
    import os
    import time

    _make_run_dir(tmp_path, "first_2026-08-01")
    time.sleep(0.01)
    _make_run_dir(tmp_path, "second_2026-08-02")

    runs = list_runs(tmp_path)

    assert runs[0].run_id == "second_2026-08-02"
    assert runs[1].run_id == "first_2026-08-01"


def test_get_run_returns_none_for_unknown_run_id(tmp_path):
    assert get_run(tmp_path, "does-not-exist") is None


def test_get_run_returns_summary_for_existing_run(tmp_path):
    _make_run_dir(
        tmp_path,
        "topic_2026-08-29",
        metadata={"query": "topic", "paper_count": 5},
    )

    run = get_run(tmp_path, "topic_2026-08-29")

    assert run is not None
    assert run.query == "topic"


def test_get_run_report_markdown_returns_none_when_missing(tmp_path):
    _make_run_dir(tmp_path, "no-report_2026-08-29")
    assert get_run_report_markdown(tmp_path, "no-report_2026-08-29") is None


def test_get_run_report_markdown_returns_content(tmp_path):
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Hello\n\nWorld")

    content = get_run_report_markdown(tmp_path, "topic_2026-08-29")

    assert content == "# Hello\n\nWorld"


def test_extraction_summary_and_future_work_ideation_default_to_empty_dict(tmp_path):
    _make_run_dir(tmp_path, "minimal_2026-08-29", metadata={"query": "x"})

    run = get_run(tmp_path, "minimal_2026-08-29")

    assert run.extraction_summary == {}
    assert run.future_work_ideation == {}

"""
Additional tests for paper_scout.web.runs — Q&A history persistence.
Append these to tests/test_web_runs.py (reuses that file's
_make_run_dir helper). Also add this import at the top:

    from paper_scout.web.runs import (
        append_qa_turn,
        get_qa_history,
        save_qa_history,
    )
"""


def test_get_qa_history_returns_empty_structure_when_no_file(tmp_path):
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")

    history = get_qa_history(tmp_path, "topic_2026-08-29")

    assert history == {"turns": [], "summary": None, "summarized_through": 0}


def test_get_qa_history_returns_empty_structure_when_run_dir_missing(tmp_path):
    history = get_qa_history(tmp_path, "does-not-exist")

    assert history == {"turns": [], "summary": None, "summarized_through": 0}


def test_get_qa_history_survives_corrupted_json(tmp_path):
    run_dir = _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    (run_dir / "qa_history.json").write_text("{not valid json", encoding="utf-8")

    history = get_qa_history(tmp_path, "topic_2026-08-29")

    assert history == {"turns": [], "summary": None, "summarized_through": 0}


def test_get_qa_history_merges_over_defaults_for_partial_files(tmp_path):
    """An older/partial qa_history.json (e.g. written before the
    summary/summarized_through fields existed) should still load with
    those fields defaulted, not raise a KeyError downstream."""
    run_dir = _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    (run_dir / "qa_history.json").write_text(
        '{"turns": [{"question": "q", "answer": "a"}]}', encoding="utf-8"
    )

    history = get_qa_history(tmp_path, "topic_2026-08-29")

    assert history["turns"] == [{"question": "q", "answer": "a"}]
    assert history["summary"] is None
    assert history["summarized_through"] == 0


def test_save_qa_history_writes_full_structure(tmp_path):
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    history = {
        "turns": [{"question": "q1", "answer": "a1"}],
        "summary": "a summary",
        "summarized_through": 1,
    }

    save_qa_history(tmp_path, "topic_2026-08-29", history)

    reloaded = get_qa_history(tmp_path, "topic_2026-08-29")
    assert reloaded == history


def test_append_qa_turn_adds_to_existing_turns(tmp_path):
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    existing = {"turns": [{"question": "q1", "answer": "a1"}], "summary": None, "summarized_through": 0}

    append_qa_turn(tmp_path, "topic_2026-08-29", existing, "q2", "a2")

    history = get_qa_history(tmp_path, "topic_2026-08-29")
    assert history["turns"] == [
        {"question": "q1", "answer": "a1"},
        {"question": "q2", "answer": "a2"},
    ]


def test_append_qa_turn_preserves_summary_fields(tmp_path):
    """The history dict passed in (e.g. from build_conversation_context,
    which may have just advanced summarized_through) must have its
    summary/summarized_through preserved, not reset, when a new turn
    is appended."""
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    updated = {"turns": [{"question": "q1", "answer": "a1"}], "summary": "prior summary", "summarized_through": 1}

    append_qa_turn(tmp_path, "topic_2026-08-29", updated, "q2", "a2")

    history = get_qa_history(tmp_path, "topic_2026-08-29")
    assert history["summary"] == "prior summary"
    assert history["summarized_through"] == 1
    assert len(history["turns"]) == 2


def test_append_qa_turn_on_empty_history(tmp_path):
    _make_run_dir(tmp_path, "topic_2026-08-29", report_text="# Report")
    empty = get_qa_history(tmp_path, "topic_2026-08-29")

    append_qa_turn(tmp_path, "topic_2026-08-29", empty, "first question", "first answer")

    history = get_qa_history(tmp_path, "topic_2026-08-29")
    assert history["turns"] == [{"question": "first question", "answer": "first answer"}]