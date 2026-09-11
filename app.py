import gradio as gr

from agent import chat_with_agent as handle_message

def respond(user_input, history):
    """
    Called by Gradio on each message. Wraps the agent call so a crash
    shows a friendly error in the chat instead of breaking the app.
    """
    if not user_input or not user_input.strip():
        history = history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": "Please enter a message before sending."},
        ]
        return history, ""

    try:
        reply = handle_message(user_input, history)
    except Exception as e:
        reply = f"Sorry, something went wrong while processing your request. ({e})"

    history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply},
    ]
    return history, ""


with gr.Blocks(title="AI Customer Support Agent") as demo:
    gr.Markdown("## AI Customer Support Agent\nAsk about your order, a product, or report an issue.")

    chatbot = gr.Chatbot(height=450)
    status = gr.Markdown("")  

    with gr.Row():
        msg_box = gr.Textbox(
            placeholder="e.g. My headphones arrived broken, can I get a refund? (Order ORD1001, Customer CUST001)",
            scale=8,
            show_label=False,
        )
        send_btn = gr.Button("Send", scale=1)

    clear_btn = gr.Button("Clear conversation")

    send_btn.click(respond, inputs=[msg_box, chatbot], outputs=[chatbot, msg_box])
    msg_box.submit(respond, inputs=[msg_box, chatbot], outputs=[chatbot, msg_box])
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg_box])


if __name__ == "__main__":
    demo.launch()
