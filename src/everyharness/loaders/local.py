"""Local file loader."""

from __future__ import annotations

import uuid
from pathlib import Path

from everyharness.core.detect import kind_from_uri
from everyharness.loaders._cache import cache_dir_for, snapshot_local_copy, write_metadata
from everyharness.plugin.protocols import PLUGIN_API_VERSION, LoaderPlugin, ModelRef, PluginInfo


class LocalLoader:
    name = "local"
    api_version = PLUGIN_API_VERSION

    def can_load(self, uri: str) -> float:
        path = Path(uri)
        if path.exists() and path.is_file():
            return 0.9
        if path.exists() and path.is_dir():
            return 0.85
        return 0.0

    def load(self, uri: str) -> ModelRef:
        path = Path(uri).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Local path not found: {uri}")
        cache_path = cache_dir_for("local", str(path))
        metadata: dict[str, object] = {"source": "local", "path": str(path)}
        if path.is_file():
            cached = snapshot_local_copy(path, cache_path)
            metadata["cached_path"] = str(cached)
        elif path.is_dir():
            metadata["cached_path"] = str(cache_path)
            write_metadata(cache_path, {"path": str(path), "kind": "directory"})
        else:
            raise FileNotFoundError(f"Local path is not a file or directory: {uri}")
        kind = kind_from_uri(str(path))
        return ModelRef(
            id=str(uuid.uuid4())[:8],
            uri=str(path),
            kind=kind,
            metadata=metadata,
        )

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="loader",
            summary="Load models from local filesystem paths and directories.",
            requires_api=">=1,<2",
        )


_: LoaderPlugin = LocalLoader()
