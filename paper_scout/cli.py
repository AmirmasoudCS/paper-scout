"""
paper_scout.cli

Single command entry point:

    python -m paper_scout "diffusion models for audio"

True end-to-end: nothing is shown until the final report is ready,
per the project's UX goal. No intermediate prompts — every tunable
knob lives in config.yaml.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from paper_scout.pipeline import run_pipeline
from paper_scout.utils.config import load_config


def _configure_logging(config: dict) -> None:
    log_cfg = config.get("logging", {})
    log_dir = Path(log_cfg.get("log_dir", "log"))
    log_dir.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, str(log_cfg.get("level", "INFO")).upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "paper_scout.log"),
            logging.StreamHandler(sys.stderr),
        ],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="paper-scout",
        description="Search recent papers on a topic and produce a markdown report "
        "with grounded future-work ideas.",
    )
    parser.add_argument("query", help="Research field or query, e.g. 'diffusion models for audio'")
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: ./config.yaml)",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _configure_logging(config)
    logger = logging.getLogger(__name__)

    print(f"Researching: {args.query}")
    print("This may take several minutes — no output until the report is ready...\n")

    try:
        pipeline_run = run_pipeline(args.query, config)
    except RuntimeError as exc:
        # Startup-time failures we deliberately raise loudly (Ollama down,
        # configured model not pulled) rather than let degrade silently.
        logger.error("Pipeline aborted: %s", exc)
        print(f"\nError: {exc}", file=sys.stderr)
        return 1
    except Exception:
        logger.exception("Pipeline failed with an unexpected error")
        print(
            "\nSomething went wrong — see the log file for details.",
            file=sys.stderr,
        )
        return 1

    print(f"Done. Found {len(pipeline_run.papers)} papers.")
    print(f"Report written to: {pipeline_run.report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())