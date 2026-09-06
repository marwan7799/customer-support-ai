import os
from typing import Any

import ollama
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")


def chat(messages: list[dict[str, Any]], tools=None):
    """Low-level wrapper around Ollama.

    The tool orchestration belongs in agent.py.
    """
    kwargs = {"model": MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    return ollama.chat(**kwargs)
