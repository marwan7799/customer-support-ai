"""
Shared helpers for loading and saving the demo JSON data files.
Keeping this in one place means every tool resolves paths the same way,
regardless of what directory the app is launched from.
"""
import json
import os

# Project root = one level up from this file's folder (tools/ -> project root)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_ROOT, "data")


def load_json(filename: str):
    """Load a JSON file from the data/ folder. Raises FileNotFoundError/JSONDecodeError on bad input."""
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data):
    """Write a JSON file back to the data/ folder (used by create_support_ticket)."""
    path = os.path.join(_DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)