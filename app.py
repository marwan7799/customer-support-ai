"""Gradio user interface for the AI customer-support agent."""

from __future__ import annotations

import logging
from typing import Any, Iterator

import gradio as gr

from agent import chat_with_agent

logger = logging.getLogger(__name__)


def respond(user_input: str, history: list[dict[str, Any]] | None) -> Iterator[tuple]:
    """Handle one Gradio message while keeping failures out of the UI internals."""
    history = history or []
    user_input = user_input if isinstance(user_input, str) else ""

    if not user_input.strip():
        yield history, user_input, "Please enter a message before sending."
        return

    cleaned_input = user_input.strip()
    pending = [
        *history,
        {"role": "user", "content": cleaned_input},
        {"role": "assistant", "content": "Working..."},
    ]
    yield pending, "", "Contacting the support model..."

    try:
        reply = chat_with_agent(cleaned_input, history)
    except Exception:
        logger.exception("Unhandled error while processing a chat message")
        reply = "Sorry, something went wrong while processing your request. Please try again."

    pending[-1] = {"role": "assistant", "content": reply}
    yield pending, "", ""


def build_app() -> gr.Blocks:
    """Construct the Gradio application without launching it on import."""
    with gr.Blocks(title="AI Customer Support Agent") as demo:
        gr.Markdown(
            "## AI Customer Support Agent\n"
            "Ask about your order, a product, a refund, or report an issue."
        )

        chatbot = gr.Chatbot(height=450)
        status = gr.Markdown("")

        with gr.Row():
            message_box = gr.Textbox(
                placeholder="e.g. What's the price of P1001? Is P1003 in stock?",
                scale=8,
                show_label=False,
            )
            send_button = gr.Button("Send", scale=1)

        clear_button = gr.Button("Clear conversation")

        send_button.click(
            respond,
            inputs=[message_box, chatbot],
            outputs=[chatbot, message_box, status],
        )
        message_box.submit(
            respond,
            inputs=[message_box, chatbot],
            outputs=[chatbot, message_box, status],
        )
        clear_button.click(lambda: ([], "", ""), outputs=[chatbot, message_box, status])

    return demo


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    build_app().queue().launch()


if __name__ == "__main__":
    main()
