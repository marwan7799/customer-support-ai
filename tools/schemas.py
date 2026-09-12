"""Ollama function schemas and the corresponding Python callables."""

from tools.order_tools import get_order_status
from tools.product_tools import get_product_info
from tools.refund_tools import check_refund_eligibility
from tools.stock_tools import check_stock
from tools.ticket_tools import create_support_ticket

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Check delivery/order status for an order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID, e.g. '10001'."}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_info",
            "description": "Get product name, price, category, and warranty details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID, e.g. 'P1001'."}
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check current stock quantity and availability for a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID, e.g. 'P1001'."}
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": (
                "Create a support ticket after the customer's issue is clear and a valid "
                "customer ID is available. Do not create tickets speculatively."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID, e.g. 'C1001'."},
                    "issue": {"type": "string", "description": "Concise description of the issue."},
                },
                "required": ["customer_id", "issue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Check refund eligibility from order status and delivery date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID, e.g. '10001'."}
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
