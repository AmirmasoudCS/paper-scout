"""Tests for paper_scout.web.runs — pure filesystem reads, no network/LLM."""

from __future__ import annotations

import json

from paper_scout.web.runs import get_run, get_run_report_markdown, list_runs


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