"""Thin Ollama client wrapper used by the agent layer."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "qwen2.5"
MODEL = os.getenv("OLLAMA_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    think: bool | None = None,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send a chat request to Ollama and return a plain dictionary response."""
    try:
        import ollama
    except ImportError as exc:
        raise RuntimeError(
            "The 'ollama' package is not installed. Install project dependencies first."
        ) from exc

    kwargs: dict[str, Any] = {"model": MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    if think is not None:
        kwargs["think"] = think
    if options:
        kwargs["options"] = options

    result = ollama.chat(**kwargs)
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    if not isinstance(result, dict):
        raise RuntimeError("Ollama returned an unexpected response type.")
    return result
