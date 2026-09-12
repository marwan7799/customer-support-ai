# AI Customer Support Agent

A small customer-support AI demo built with Python, Ollama, and Gradio. The agent can classify requests, maintain conversation context, summarize long histories, call deterministic Python tools, and return professional support responses.

## Features

- Gradio chat interface with conversation history
- Ollama-based request classification and response generation
- Automatic summarization of older conversation turns
- LLM-selected tool calling with a bounded multi-tool loop
- Deterministic order, product, stock, refund, and ticket tools
- Input validation and graceful model/tool error handling
- Runtime ticket persistence outside the static demo data

## Available tools

1. `get_order_status(order_id)`
2. `get_product_info(product_id)`
3. `check_stock(product_id)`
4. `create_support_ticket(customer_id, issue)`
5. `check_refund_eligibility(order_id)`

Demo IDs:

- Products: `P1001`, `P1002`, `P1003`
- Orders: `10001`, `10002`, `10003`
- Customers: `C1001`, `C1002`, `C1003`

## Project structure

```text
customer-support-ai/
├── app.py                  # Gradio UI and application entry point
├── agent.py                # Agent orchestration and tool-calling loop
├── llm.py                  # Thin Ollama client wrapper
├── prompts_loader.py       # System-prompt loader
├── prompts/
│   └── system_prompt.txt
├── tools/
│   ├── __init__.py
│   ├── _data.py            # Shared JSON storage and ID helpers
│   ├── schemas.py          # Ollama tool schemas and function registry
│   ├── order_tools.py
│   ├── product_tools.py
│   ├── stock_tools.py
│   ├── refund_tools.py
│   └── ticket_tools.py
├── data/                   # Read-only demo company data
│   ├── customers.json
│   ├── products.json
│   └── orders.json
├── runtime/                # Generated at runtime; ignored by Git
│   └── tickets.json
├── tests/
│   ├── test_agent.py
│   └── test_tools.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Install and start Ollama, then make sure the configured model exists. The default is `qwen2.5`:

   ```bash
   ollama pull qwen2.5
   ```

4. Optional: copy `.env.example` to `.env` and change `OLLAMA_MODEL`.
5. Run the tests:

   ```bash
   python -m pytest -q
   ```

6. Start the application:

   ```bash
   python app.py
   ```

The Gradio terminal output will show the local URL.

## Refund policy used by the demo

A delivered order is eligible when its delivery date is within the last 14 days. Non-delivered orders are not eligible for refund review yet. Invalid or future delivery dates are treated as data errors rather than valid refund cases.

## Data and security notes

- `.env` files are ignored by Git; only `.env.example` should be committed.
- No API keys are required by this project because Ollama runs locally.
- Static demo data lives in `data/`.
- Generated support tickets live in `runtime/tickets.json`, which is ignored by Git.
- The UI does not expose raw Python exception messages to customers.

## Scope

This is intentionally a small demo application. It does not include authentication, a production database, RAG, rate limiting, or production observability.
