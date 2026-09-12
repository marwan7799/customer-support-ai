"""Shared JSON data access helpers for support tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RUNTIME_DIR = PROJECT_ROOT / "runtime"


class DataStoreError(Exception):
    """Raised when a JSON-backed data store cannot be read or written safely."""


def load_json(path: Path) -> Any:
    """Load JSON from *path* and convert storage failures to a stable exception."""
    try:
        with path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as exc:
        raise DataStoreError(f"Data file '{path.name}' is unavailable.") from exc
    except json.JSONDecodeError as exc:
        raise DataStoreError(f"Data file '{path.name}' is corrupted.") from exc
    except OSError as exc:
        raise DataStoreError(f"Data file '{path.name}' could not be read.") from exc


def load_records(filename: str) -> list[dict[str, Any]]:
    """Load a list of object records from the project's static data directory."""
    data = load_json(DATA_DIR / filename)
    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise DataStoreError(f"Data file '{filename}' has an invalid structure.")
    return data


def save_json(path: Path, data: Any) -> None:
    """Atomically write JSON so an interrupted write does not corrupt the store."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")
        temporary_path.replace(path)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise DataStoreError(f"Data file '{path.name}' could not be saved.") from exc


def normalize_identifier(value: Any) -> str | None:
    """Return a stripped identifier, or ``None`` for invalid/empty input."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def find_by_id(records: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    """Match an identifier ignoring surrounding whitespace and letter case."""
    needle = value.casefold()
    return next(
        (
            row
            for row in records
            if str(row.get(key, "")).strip().casefold() == needle
        ),
        None,
    )
