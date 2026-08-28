"""
paper_scout.utils.config

Loads config.yaml (the project's single source of truth for tunables)
and .env (for secrets like SEMANTIC_SCHOLAR_API_KEY) into a plain dict
used throughout the pipeline.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from dotenv import load_dotenv


def load_config(path: str | Path = "config.yaml") -> dict:
    """
    Load config.yaml into a dict. Also loads a sibling .env file (if
    present) so os.environ has any API keys available before sources
    are constructed. Raises FileNotFoundError with a clear message if
    the config file is missing — this should fail loudly at startup,
    not degrade gracefully like the rest of the pipeline, since without
    it nothing downstream has sane defaults.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"config.yaml not found at {config_path.resolve()} — "
            "paper-scout cannot run without it."
        )

    env_path = config_path.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)