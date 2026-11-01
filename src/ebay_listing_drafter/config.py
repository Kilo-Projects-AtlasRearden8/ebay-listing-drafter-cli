"""Configuration for the eBay listing drafter.

Configuration sources (in priority order):
1. command-line arguments
2. environment variables
3. user config file (~/.config/ebay-listing-drafter/config.json)
4. built-in defaults

All settings are optional. The default endpoint is a local Ollama instance,
so no API keys or network accounts are required.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOKENS = 800

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "ebay-listing-drafter"
CONFIG_FILE = CONFIG_DIR / "config.json"

ENV_BASE_URL = "EBAY_DRAFTER_BASE_URL"
ENV_MODEL = "EBAY_DRAFTER_MODEL"
ENV_TEMPERATURE = "EBAY_DRAFTER_TEMPERATURE"
ENV_TIMEOUT = "EBAY_DRAFTER_TIMEOUT_SECONDS"
ENV_MAX_TOKENS = "EBAY_DRAFTER_MAX_TOKENS"


@dataclass
class Config:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    max_tokens: int = DEFAULT_MAX_TOKENS
    source: str = "defaults"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file, environment, then defaults."""
        config = cls()
        config.source = "defaults"

        file_values: dict[str, Any] = {}
        if CONFIG_FILE.exists():
            try:
                with CONFIG_FILE.open("r", encoding="utf-8") as handle:
                    file_values = json.load(handle) or {}
            except (OSError, json.JSONDecodeError):
                file_values = {}

        if file_values:
            config = cls(**{k: v for k, v in file_values.items() if k in cls.__dataclass_fields__})
            config.source = f"config file ({CONFIG_FILE})"

        env_overrides = {
            "base_url": os.environ.get(ENV_BASE_URL),
            "model": os.environ.get(ENV_MODEL),
            "temperature": _parse_float(os.environ.get(ENV_TEMPERATURE)),
            "timeout_seconds": _parse_int(os.environ.get(ENV_TIMEOUT)),
            "max_tokens": _parse_int(os.environ.get(ENV_MAX_TOKENS)),
        }
        applied = {k: v for k, v in env_overrides.items() if v is not None}
        if applied:
            for key, value in applied.items():
                setattr(config, key, value)
            config.source = "environment variables"

        return config

    def save_to_file(self, path: Path | None = None) -> Path:
        """Persist the current config to the user config file."""
        target = path or CONFIG_FILE
        target.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
        }
        with target.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        return target


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
