"""OpenAI-compatible chat client (default: local Ollama).

Talks to the /chat/completions endpoint of any OpenAI-compatible server.
No API keys are required by default; Ollama runs entirely locally.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class LLMError(RuntimeError):
    """Raised when the language model endpoint cannot be reached or fails."""


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    raw: dict


class ChatClient:
    """Minimal OpenAI-compatible chat completions client over urllib."""

    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 800,
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/chat/completions"

    def chat(self, messages: list[ChatMessage]) -> ChatResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LLMError(
                f"Could not reach LLM endpoint at {self.endpoint}. "
                "Is Ollama (or another OpenAI-compatible server) running locally?"
            ) from exc
        except json.JSONDecodeError as exc:
            raise LLMError(f"Invalid JSON response from LLM endpoint at {self.endpoint}") from exc

        choices = raw.get("choices") or []
        if not choices:
            raise LLMError(f"LLM endpoint returned no choices: {raw}")
        content = choices[0].get("message", {}).get("content", "") or ""
        return ChatResponse(content=content, model=raw.get("model", self.model), raw=raw)
