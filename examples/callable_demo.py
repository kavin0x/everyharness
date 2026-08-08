"""Example callable for generic harness demos."""

from __future__ import annotations

from typing import Any


def echo(data: Any) -> Any:
    return {"echo": data}
