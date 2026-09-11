# AI Customer Support Agent

Team 2 project for AI & Automation Engineering.

## Goal

Build a customer-support AI application using Python, Ollama, and Gradio.

Required functionality:
- conversation history
- customer-request understanding/classification
- message summarization
- professional support responses
- five Python tools
- LLM-selected tool calling
- multi-tool workflows
- reliability/error handling

## Required tools

1. `get_order_status(order_id)`
2. `get_product_info(product_id)`
3. `check_stock(product_id)`
4. `create_support_ticket(customer_id, issue)`
5. `check_refund_eligibility(order_id)`

## Team split

### me — AI / Agent
- Ollama integration
- system prompt
- conversation history
- tool-calling loop
- request classification
- summarization
- final response generation
- agent-level error handling

### Kareem — Tools / Data / UI
- demo company data
- five Python tools
- validation and tool-level error handling
- Gradio interface
- status messages

### Shared
- integration
- testing
- README
- presentation/demo

## Project structure

```text
customer-support-ai/
├── app.py
├── agent.py
├── llm.py
├── prompts_loader.py
├── prompts/
│   └── system_prompt.txt
├── tools/
│   ├── __init__.py
│   ├── order_tools.py
│   ├── product_tools.py
│   ├── ticket_tools.py
│   └── refund_tools.py
├── data/
│   ├── customers.json
│   ├── products.json
│   └── orders.json
├── tests/
│   └── test_tools.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Bonus scope

RAG is not included in this starter version.
