"""
paper_scout.llm.ollama_client

Thin wrapper around the local Ollama REST API (http://localhost:11434),
supporting the project's two-tier setup:
  - "small"  -> qwen3.5:9b            (per-paper summarization, Phase 5)
  - "large"  -> gemma4:e4b            (cross-paper synthesis / future-work
                                        ideation, Phase 6)

Consistent with the rest of the pipeline's degrade-gracefully philosophy:
network/model failures are retried with backoff and then return None
rather than raising, so one bad LLM call doesn't kill a full pipeline run.
Callers decide how to handle a None (skip the paper, fall back to a
simpler summary, etc.).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Literal, Optional

import requests

logger = logging.getLogger(__name__)

ModelTier = Literal["small", "large"]

_MAX_RETRIES = 3
_BACKOFF_BASE_SECONDS = 2


@dataclass
class ModelConfig:
    name: str
    temperature: float = 0.3
    max_tokens: int = 512


class OllamaClient:
    """
    Usage:
        client = OllamaClient.from_config(config)  # config is the parsed config.yaml dict
        text = client.generate_small("Summarize this abstract: ...")
        text = client.generate_large("Synthesize themes across these papers: ...", json_mode=False)
    """

    def __init__(
        self,
        small_model: ModelConfig,
        large_model: ModelConfig,
        base_url: str = "http://localhost:11434",
        timeout_seconds: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._models: dict[ModelTier, ModelConfig] = {
            "small": small_model,
            "large": large_model,
        }

    @classmethod
    def from_config(cls, config: dict, base_url: str = "http://localhost:11434") -> "OllamaClient":
        llm_cfg = config["llm"]
        return cls(
            small_model=ModelConfig(
                name=llm_cfg["small_model"]["name"],
                temperature=llm_cfg["small_model"].get("temperature", 0.3),
                max_tokens=llm_cfg["small_model"].get("max_tokens", 512),
            ),
            large_model=ModelConfig(
                name=llm_cfg["large_model"]["name"],
                temperature=llm_cfg["large_model"].get("temperature", 0.5),
                max_tokens=llm_cfg["large_model"].get("max_tokens", 1500),
            ),
            base_url=base_url,
            timeout_seconds=llm_cfg.get("timeout_seconds", 120),
        )

    # ── Health checks ────────────────────────────────────────────────

    def is_available(self) -> bool:
        """True if the local Ollama server is reachable at all."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.warning("Ollama server not reachable at %s: %s", self.base_url, exc)
            return False

    def list_models(self) -> list[str]:
        """Local model tags currently pulled. Empty list on failure."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
        except (requests.RequestException, KeyError, ValueError) as exc:
            logger.warning("Failed to list Ollama models: %s", exc)
            return []

    def verify_configured_models(self) -> dict[ModelTier, bool]:
        """
        Check that the small/large models named in config are actually
        pulled locally. Use this at pipeline startup to fail fast with a
        clear message instead of a confusing error mid-run.
        """
        available = set(self.list_models())
        result: dict[ModelTier, bool] = {}
        for tier, model_cfg in self._models.items():
            # Ollama tags list may or may not include the ":latest" suffix depending
            # on how the model was pulled — compare both forms to be safe.
            name = model_cfg.name
            found = name in available or f"{name}:latest" in available or any(
                m.startswith(name.split(":")[0]) for m in available
            )
            result[tier] = found
            if not found:
                logger.warning(
                    "Configured %s model %r not found in local Ollama models: %s",
                    tier,
                    name,
                    sorted(available),
                )
        return result

    # ── Generation ───────────────────────────────────────────────────

    def generate_small(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> Optional[str]:
        return self._chat("small", prompt, system, json_mode)

    def generate_large(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> Optional[str]:
        return self._chat("large", prompt, system, json_mode)

    def _chat(
        self,
        tier: ModelTier,
        prompt: str,
        system: Optional[str],
        json_mode: bool,
        max_retries: int = _MAX_RETRIES,
    ) -> Optional[str]:
        model_cfg = self._models[tier]

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_cfg.name,
            "messages": messages,
            "stream": False,
            # Disable "thinking" mode for reasoning models (e.g. qwen3.5). Must be a
            # TOP-LEVEL field, not inside `options` — Ollama silently ignores
            # options.think for the /api/chat endpoint on these models and the
            # model burns its entire num_predict budget on invisible reasoning,
            # leaving message.content empty. See ollama/ollama#14793.
            "think": False,
            "options": {
                "temperature": model_cfg.temperature,
                "num_predict": model_cfg.max_tokens,
            },
        }
        if json_mode:
            # NOTE: format="json" is known to be silently ignored on some
            # thinking-capable models (e.g. qwen3.5) once think=False is set
            # (ollama/ollama#14645). We still request it — it's honored on
            # non-thinking models and is harmless when ignored — but callers
            # doing json_mode should parse leniently rather than assume
            # strict JSON-only output (see summarize.summarizer._parse_summary_json).
            payload["format"] = "json"

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("message", {}).get("content")
                if not content:
                    # Rare fallback: some Ollama versions/models still route output
                    # to the "thinking" field even with think=False (ollama/ollama#14716).
                    # Recover it rather than silently failing, but flag it loudly since
                    # it means the client's think:False request wasn't fully honored.
                    thinking = data.get("message", {}).get("thinking")
                    if thinking:
                        logger.warning(
                            "Ollama %s model %r returned content in 'thinking' field "
                            "instead of 'content' despite think=False — using it anyway "
                            "(see ollama/ollama#14716)",
                            tier,
                            model_cfg.name,
                        )
                        content = thinking
                if not content:
                    logger.warning(
                        "Ollama %s model %r returned an empty response", tier, model_cfg.name
                    )
                    return None
                return content

            except requests.RequestException as exc:
                wait = _BACKOFF_BASE_SECONDS**attempt
                logger.warning(
                    "Attempt %d/%d failed for %s model %r (%s)%s",
                    attempt,
                    max_retries,
                    tier,
                    model_cfg.name,
                    exc,
                    f" — retrying in {wait}s" if attempt < max_retries else "",
                )
                if attempt < max_retries:
                    time.sleep(wait)
            except (KeyError, ValueError) as exc:
                # Malformed response body — retrying won't help.
                logger.error("Malformed response from Ollama for %s model: %s", tier, exc)
                return None

        logger.error(
            "Giving up on %s model %r after %d attempts", tier, model_cfg.name, max_retries
        )
        return None