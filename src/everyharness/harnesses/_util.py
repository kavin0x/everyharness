"""Shared harness utilities."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str))


def read_json_input(path: str | None) -> Any:
    """Read JSON from a file path, inline JSON string, or stdin."""
    if path:
        stripped = path.strip()
        if stripped.startswith(("{", "[")):
            return json.loads(stripped)
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if sys.stdin.isatty():
        return None
    return json.loads(sys.stdin.read())


def missing_extra(name: str, extra: str) -> int:
    print(
        f"Missing optional dependency for {name}. "
        f"Install with: pip install 'everyharness[{extra}]'",
        file=sys.stderr,
    )
    return 1


def unsupported(message: str) -> int:
    """Print a clear unsupported-feature message and return exit code 1."""
    print(f"Unsupported: {message}", file=sys.stderr)
    return 1


def try_import(module: str, extra: str) -> Any | None:
    try:
        return __import__(module)
    except ImportError:
        return None
