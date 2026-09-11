import json
import logging
from typing import Any

from llm import chat
from prompts_loader import load_system_prompt
from tools.schemas import TOOL_SCHEMAS, TOOL_FUNCTIONS

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5

CLASSIFICATION_LABELS = ["ORDER", "REFUND", "PRODUCT", "COMPLAINT", "TECHNICAL", "OTHER"]


def classify_request(message: str) -> str:
    """Classify the customer's message into one of the brief's required categories.

    Runs as a lightweight, single-turn LLM call (no tools, no history) so it
    stays fast and cheap. Falls back to 'OTHER' on any failure so a
    classification error never blocks the main conversation.
    """
    prompt = (
        "Classify the customer's message into exactly one of these categories: "
        f"{', '.join(CLASSIFICATION_LABELS)}.\n"
        "Respond with only the category name, nothing else.\n\n"
        f"Customer message: {message}"
    )
    try:
        response = chat([{"role": "user", "content": prompt}])
        label = response["message"]["content"].strip().upper()
        return label if label in CLASSIFICATION_LABELS else "OTHER"
    except Exception:
        return "OTHER"


def summarize_message(message: str) -> str:
    """Summarize a single customer message/email in one or two sentences.

    Used for logging and for producing a concise issue description when
    filing a support ticket, per the brief's 'summarize a customer
    email/message' requirement.
    """
    prompt = (
        "Summarize the following customer message in 1-2 concise sentences, "
        "capturing the core issue or request:\n\n"
        f"{message}"
    )
    try:
        response = chat([{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception:
        return message[:200]  # graceful fallback: truncate rather than fail


def summarize_conversation(history: list[dict[str, Any]]) -> str:
    """Summarize prior conversation turns into a short paragraph.

    Used to keep long histories compact before sending them to the model,
    so the context sent to Ollama stays bounded as conversations grow.
    """
    if not history:
        return ""

    transcript = "\n".join(
        f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history
    )
    prompt = (
        "Summarize the following customer support conversation in 2-3 "
        "sentences, focusing on the customer's issue and any facts "
        "already established (order IDs, product IDs, etc.):\n\n"
        f"{transcript}"
    )
    try:
        response = chat([{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception:
        return ""


def _build_messages(message: str, history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assemble the message list, condensing history if it grows too long."""
    system_prompt = load_system_prompt()

    # Keep the last few turns verbatim; summarize anything older so the
    # context sent to the model stays bounded as conversations get long.
    RECENT_TURNS = 8
    if len(history) > RECENT_TURNS:
        older, recent = history[:-RECENT_TURNS], history[-RECENT_TURNS:]
        summary = summarize_conversation(older)
        summary_note = (
            {"role": "system", "content": f"Earlier conversation summary: {summary}"}
            if summary
            else None
        )
        base_history = ([summary_note] if summary_note else []) + recent
    else:
        base_history = history

    return [
        {"role": "system", "content": system_prompt},
        *base_history,
        {"role": "user", "content": message},
    ]


def _run_tool_call(call: dict[str, Any]) -> tuple[str, Any]:
    """Execute a single tool call requested by the model and return its result."""
    fn_name = call["function"]["name"]
    fn_args = call["function"].get("arguments") or {}

    if isinstance(fn_args, str):
        try:
            fn_args = json.loads(fn_args)
        except json.JSONDecodeError:
            return fn_name, {"error": "Malformed tool arguments."}

    fn = TOOL_FUNCTIONS.get(fn_name)
    if fn is None:
        return fn_name, {"error": f"Unknown tool: {fn_name}"}

    try:
        return fn_name, fn(**fn_args)
    except TypeError as e:
        return fn_name, {"error": f"Invalid arguments for {fn_name}: {e}"}
    except Exception as e:
        return fn_name, {"error": f"Tool '{fn_name}' failed: {e}"}


def chat_with_agent(message: str, history: list[dict[str, Any]]) -> str:
    """Main entry point: classify, run the tool-calling loop, return a reply."""
    category = classify_request(message)
    logger.info("Request classified as: %s | message: %s", category, summarize_message(message))

    messages = _build_messages(message, history)

    for _ in range(MAX_TOOL_ITERATIONS):
        try:
            response = chat(messages, tools=TOOL_SCHEMAS)
        except Exception:
            return "Sorry, I'm having trouble reaching the support system right now. Please try again shortly."

        msg = response.get("message", {})
        tool_calls = msg.get("tool_calls")

        if not tool_calls:
            content = msg.get("content")
            return content if content else "Sorry, I couldn't generate a response. Please try rephrasing."

        messages.append(msg)

        for call in tool_calls:
            fn_name, result = _run_tool_call(call)
            logger.info("Tool called: %s | result: %s", fn_name, result)
            messages.append(
                {
                    "role": "tool",
                    "name": fn_name,
                    "content": json.dumps(result, default=str),
                }
            )

    return "Sorry, I couldn't complete that request after several attempts. Please try rephrasing or contact support directly."
