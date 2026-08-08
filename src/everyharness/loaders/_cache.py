"""Shared offline cache helpers for loaders."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, cast

from everyharness.core.cache import get_cache_root
from everyharness.core.config import is_offline
from everyharness.core.errors import OfflineError


def cache_key(namespace: str, uri: str) -> str:
    digest = hashlib.sha256(f"{namespace}:{uri}".encode()).hexdigest()[:16]
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in uri)[-48:]
    return f"{namespace}-{safe}-{digest}"


def cache_dir_for(namespace: str, uri: str) -> Path:
    path = get_cache_root() / namespace / cache_key(namespace, uri)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_metadata(cache_path: Path, data: dict[str, Any]) -> None:
    meta = cache_path / "metadata.json"
    meta.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_metadata(cache_path: Path) -> dict[str, Any] | None:
    meta = cache_path / "metadata.json"
    if not meta.exists():
        return None
    return cast(dict[str, Any], json.loads(meta.read_text(encoding="utf-8")))


def ensure_not_offline_for_download() -> None:
    if is_offline():
        raise OfflineError(
            "Network download blocked: EVERYHARNESS_OFFLINE=1 (use a cached model or local path)"
        )


def snapshot_local_copy(src: Path, dest: Path) -> Path:
    """Copy a local file into cache if not already present."""
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / src.name
    if not target.exists():
        shutil.copy2(src, target)
    return target
