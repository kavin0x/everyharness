"""Offline cache helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from everyharness.core.config import cache_dir


def get_cache_root() -> Path:
    return cache_dir()


def prune_cache(*, dry_run: bool = False) -> list[Path]:
    """Remove empty cache subdirectories. Returns removed paths."""
    root = get_cache_root()
    removed: list[Path] = []
    if not root.exists():
        return removed
    for child in sorted(root.iterdir()):
        if child.is_dir() and not any(child.iterdir()):
            removed.append(child)
            if not dry_run:
                shutil.rmtree(child)
    return removed


def cache_size_bytes() -> int:
    root = get_cache_root()
    if not root.exists():
        return 0
    total = 0
    for path in root.rglob("*"):
        if path.is_file():
            total += path.stat().st_size
    return total
