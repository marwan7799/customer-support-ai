"""Customer-support agent orchestration and Ollama tool-calling loop."""

from __future__ import annotations

import json
import logging
from typing import Any

from llm import chat
from prompts_loader import load_system_prompt
from tools.schemas import TOOL_FUNCTIONS, TOOL_SCHEMAS

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5
RECENT_HISTORY_TURNS = 8
CLASSIFICATION_LABELS = ("ORDER", "REFUND", "PRODUCT", "COMPLAINT", "TECHNICAL", "OTHER")


def classify_request(message: str) -> str:
    """Classify one customer message, falling back to ``OTHER`` on model failure."""
    prompt = (
        "Classify the customer's message into exactly one of these categories: "
        f"{', '.join(CLASSIFICATION_LABELS)}.\n"
        "Respond with only the category name, nothing else.\n\n"
        f"Customer message: {message}"
    )
    try:
        response = chat(
            [{"role": "user", "content": prompt}],
            think=False,
            options={"num_predict": 16},
        )
        label = str((response.get("message") or {}).get("content") or "").strip().upper()
        return label if label in CLASSIFICATION_LABELS else "OTHER"
    except Exception:
        logger.debug("Request classification failed", exc_info=True)
        return "OTHER"


def summarize_message(message: str) -> str:
    """Summarize a customer message in one or two sentences."""
    prompt = (
        "Summarize the following customer message in 1-2 concise sentences, "
        "capturing the core issue or request:\n\n"
        f"{message}"
    )
    try:
        response = chat([{"role": "user", "content": prompt}])
        summary = str((response.get("message") or {}).get("content") or "").strip()
        return summary or message[:200]
    except Exception:
        logger.debug("Message summarization failed", exc_info=True)
        return message[:200]


def summarize_conversation(history: list[dict[str, Any]]) -> str:
    """Summarize older conversation turns to keep model context bounded."""
    if not history:
        return ""

    transcript = "\n".join(
        f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history
    )
    prompt = (
        "Summarize the following customer support conversation in 2-3 sentences, "
        "focusing on the customer's issue and facts already established "
        "(order IDs, product IDs, customer IDs, etc.):\n\n"
        f"{transcript}"
    )
    try:
        response = chat([{"role": "user", "content": prompt}])
        return str((response.get("message") or {}).get("content") or "").strip()
    except Exception:
        logger.debug("Conversation summarization failed", exc_info=True)
        return ""


def _normalize_history(history: list[Any] | None) -> list[dict[str, str]]:
    """Convert Gradio history values into Ollama-compatible role/content messages."""
    if not history:
        return []

    normalized: list[dict[str, str]] = []
    for turn in history:
        if isinstance(turn, dict):
            role = turn.get("role", "user")
            content = turn.get("content", "")
        else:
            role = getattr(turn, "role", "user")
            content = getattr(turn, "content", "")

        if isinstance(content, list):
            content = "".join(
                str(part.get("text") or part.get("content") or "")
                if isinstance(part, dict)
                else str(part)
                for part in content
            )

        if role in {"user", "assistant", "system"} and content is not None:
            text = str(content).strip()
            if text:
                normalized.append({"role": role, "content": text})
    return normalized


def _build_messages(message: str, history: list[Any] | None) -> list[dict[str, Any]]:
    """Build model input and summarize old history when conversations grow long."""
    normalized_history = _normalize_history(history)

    if len(normalized_history) > RECENT_HISTORY_TURNS:
        older = normalized_history[:-RECENT_HISTORY_TURNS]
        recent = normalized_history[-RECENT_HISTORY_TURNS:]
        summary = summarize_conversation(older)
        if summary:
            recent = [
                {"role": "system", "content": f"Earlier conversation summary: {summary}"},
                *recent,
            ]
        base_history = recent
    else:
        base_history = normalized_history

    return [
        {"role": "system", "content": load_system_prompt()},
        *base_history,
        {"role": "user", "content": message},
    ]


def _parse_tool_call(call: Any) -> tuple[str | None, dict[str, Any] | None, str | None]:
    """Validate and normalize one model tool call."""
    if not isinstance(call, dict):
        return None, None, "Malformed tool call."

    function = call.get("function")
    if not isinstance(function, dict):
        return None, None, "Malformed tool call."

    function_name = function.get("name")
    if not isinstance(function_name, str) or not function_name.strip():
        return None, None, "Tool call is missing a function name."
    function_name = function_name.strip()

    arguments = function.get("arguments") or {}
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            return function_name, None, "Malformed tool arguments."

    if not isinstance(arguments, dict):
        return function_name, None, "Tool arguments must be an object."

    return function_name, arguments, None


def _run_tool_call(call: Any) -> tuple[str, dict[str, Any]]:
    """Execute one validated tool call and convert failures into tool-safe results."""
    function_name, arguments, validation_error = _parse_tool_call(call)
    safe_name = function_name or "unknown_tool"
    if validation_error:
        return safe_name, {"success": False, "error": validation_error}

    function = TOOL_FUNCTIONS.get(safe_name)
    if function is None:
        return safe_name, {"success": False, "error": f"Unknown tool: {safe_name}"}

    try:
        result = function(**arguments)
    except TypeError:
        logger.warning("Invalid arguments supplied for tool %s", safe_name, exc_info=True)
        return safe_name, {"success": False, "error": f"Invalid arguments for {safe_name}."}
    except Exception:
        logger.exception("Unexpected failure in tool %s", safe_name)
        return safe_name, {"success": False, "error": f"Tool '{safe_name}' failed."}

    if not isinstance(result, dict):
        logger.error("Tool %s returned non-dict result", safe_name)
        return safe_name, {"success": False, "error": f"Tool '{safe_name}' returned invalid data."}
    return safe_name, result


def chat_with_agent(message: str, history: list[Any] | None = None) -> str:
    """Classify a request, run model-selected tools, and return the final reply."""
    if not isinstance(message, str) or not message.strip():
        return "Please enter a message before sending."
    message = message.strip()

    classification = classify_request(message)
    logger.info("Customer request classified as %s", classification)

    messages = _build_messages(message, history)
    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            response = chat(messages, tools=TOOL_SCHEMAS)
        except Exception:
            logger.exception("Ollama chat failed")
            return "Sorry, I'm having trouble reaching the support system right now. Please try again shortly."

        model_message = response.get("message")
        if not isinstance(model_message, dict):
            logger.error("Ollama response did not contain a valid message")
            return "Sorry, I received an invalid response from the support system. Please try again."

        tool_calls = model_message.get("tool_calls")
        if not tool_calls:
            content = str(model_message.get("content") or "").strip()
            return content or "Sorry, I couldn't generate a response. Please try rephrasing."

        if not isinstance(tool_calls, list):
            logger.error("Ollama returned malformed tool_calls")
            return "Sorry, I received an invalid tool request from the support system. Please try again."

        messages.append(
            {
                "role": "assistant",
                "content": str(model_message.get("content") or ""),
                "tool_calls": tool_calls,
            }
        )

        for tool_call in tool_calls:
            function_name, result = _run_tool_call(tool_call)
            logger.info("Tool called: %s | success=%s", function_name, result.get("success"))
            messages.append(
                {
                    "role": "tool",
                    "tool_name": function_name,
                    "content": json.dumps(result, default=str),
                }
            )

    logger.warning("Agent reached maximum tool iterations")
    return (
        "Sorry, I couldn't complete that request after several attempts. "
        "Please try rephrasing or contact support directly."
    )
