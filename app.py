import gradio as gr

from agent import chat_with_agent


def respond(message, history):
    try:
        return chat_with_agent(message, history or [])
    except Exception:
        return "Sorry, something went wrong while processing your request."


demo = gr.ChatInterface(
    fn=respond,
    title="AI Customer Support Agent",
    description="Ask about orders, products, stock, refunds, or support issues.",
)

if __name__ == "__main__":
    demo.launch()
