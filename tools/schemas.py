"""
Tool schemas for Ollama function calling.

Hand this file to whoever builds agent.py — pass TOOL_SCHEMAS to the Ollama
chat call's `tools` parameter, and use TOOL_FUNCTIONS to map a tool_call's
name back to the actual Python function to execute.

Example usage in agent.py:

    from tools.schemas import TOOL_SCHEMAS, TOOL_FUNCTIONS

    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOL_SCHEMAS,
    )

    # when the model returns a tool_call:
    func = TOOL_FUNCTIONS[tool_call["function"]["name"]]
    result = func(**tool_call["function"]["arguments"])
"""
from tools import (
    get_order_status,
    get_product_info,
    check_stock,
    create_support_ticket,
    check_refund_eligibility,
)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Check the delivery/order status for a given order ID. Use this whenever a customer asks about where their order is or whether it has been delivered.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order identifier, e.g. 'ORD1001'",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Retrieve product details (name, price, category, warranty) for a given product ID. Use this when a customer asks about a product's specs, price, or warranty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product identifier, e.g. 'P100'",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check current stock quantity and availability for a given product ID. Use this when a customer asks if an item is in stock or available to buy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product identifier, e.g. 'P100'",
                    }
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Open a support ticket for a customer issue. Use this after confirming the customer's problem (e.g. broken item, complaint) and once you have enough detail to file it — do not create a ticket speculatively.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier, e.g. 'CUST001'",
                    },
                    "issue": {
                        "type": "string",
                        "description": "A clear description of the customer's issue.",
                    },
                },
                "required": ["customer_id", "issue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Determine whether an order is eligible for a refund, based on order status and delivery date. Use this before promising a customer a refund.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order identifier, e.g. 'ORD1001'",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "get_order_status": get_order_status,
    "get_product_info": get_product_info,
    "check_stock": check_stock,
    "create_support_ticket": create_support_ticket,
    "check_refund_eligibility": check_refund_eligibility,
}