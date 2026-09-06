from typing import Any

from llm import chat
from prompts_loader import load_system_prompt


# TODO:
# 1. Define the five Ollama tool schemas.
# 2. Register the five Python tool functions.
# 3. Send system prompt + conversation history + current user message.
# 4. Inspect Ollama tool calls.
# 5. Execute the selected Python tool(s).
# 6. Add tool results using the correct tool message structure.
# 7. Continue until Ollama returns a final response.
# 8. Add classification and summarization flows where needed.


def chat_with_agent(message: str, history: list[dict[str, Any]]) -> str:
    messages = [
        {"role": "system", "content": load_system_prompt()},
        *history,
        {"role": "user", "content": message},
    ]

    # Temporary starter behavior.
    response = chat(messages)
    return response["message"]["content"]
