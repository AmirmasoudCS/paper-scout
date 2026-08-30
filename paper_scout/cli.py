"""
paper_scout.cli

Single command entry point:

    python -m paper_scout "diffusion models for audio"

True end-to-end: nothing is shown until the final report is ready,
per the project's UX goal. No intermediate prompts by default — every
tunable knob lives in config.yaml. The one opt-in exception is
--refine-query, which pauses once, before the pipeline starts, to let
the small model suggest a cleaned-up query and let you confirm, edit,
or cancel it — mirroring the web UI's refine/confirm flow.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from paper_scout.llm.ollama_client import OllamaClient
from paper_scout.llm.query_refine import refine_search_query
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


def _prompt_query_refinement(client: OllamaClient, raw_query: str) -> tuple[str, Optional[str]]:
    """
    Interactively refine raw_query using the small model. Returns
    (final_query, original_query), where original_query is None unless
    the query actually changed and refinement was accepted in some
    form — mirrors the web UI's "always show what changed, let the
    user confirm/edit/cancel" behavior, adapted to a terminal prompt.

    Raises KeyboardInterrupt if the user cancels via Ctrl+C during the
    prompt, so the caller can abort the whole run rather than silently
    continuing with an unintended query.
    """
    refinement = refine_search_query(raw_query, client)

    if refinement.refined is None:
        print(f"Could not refine the query ({refinement.error}) — using your original query.\n")
        return raw_query, None

    if not refinement.changed:
        print("Your query already looked good — nothing to change.\n")
        return raw_query, None

    print(f"Original query:  {raw_query}")
    print(f"Suggested query: {refinement.refined}\n")

    try:
        choice = input(
            "Press Enter to use the suggested query, type your own version, "
            "or type 'cancel' to keep the original: "
        ).strip()
    except EOFError:
        # No interactive input available (e.g. piped/non-interactive run) —
        # fall back to the suggestion rather than hang or fail.
        print("\nNo input available — using the suggested query.\n")
        return refinement.refined, raw_query

    if choice == "":
        return refinement.refined, raw_query
    if choice.lower() == "cancel":
        return raw_query, None
    return choice, raw_query


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
    parser.add_argument(
        "--refine-query",
        action="store_true",
        help="Use the small model to fix spelling and tighten your query's phrasing before "
        "searching, with a chance to review, edit, or cancel the suggestion.",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    _configure_logging(config)
    logger = logging.getLogger(__name__)

    query = args.query
    original_query: Optional[str] = None
    client: Optional[OllamaClient] = None

    if args.refine_query:
        client = OllamaClient.from_config(config)
        if not client.is_available():
            print("Warning: Ollama is not reachable — skipping query refinement.\n", file=sys.stderr)
        else:
            try:
                query, original_query = _prompt_query_refinement(client, args.query)
            except KeyboardInterrupt:
                print("\nAborted.", file=sys.stderr)
                return 130

    print(f"Researching: {query}")
    if original_query and original_query != query:
        print(f"(originally typed as: {original_query})")
    print("This may take several minutes — no output until the report is ready...\n")

    try:
        pipeline_run = run_pipeline(query, config, client=client, original_query=original_query)
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