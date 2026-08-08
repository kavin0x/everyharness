"""Python callable loader (module:attribute references)."""

from __future__ import annotations

import importlib
import uuid

from everyharness.loaders._cache import cache_dir_for, write_metadata
from everyharness.plugin.protocols import PLUGIN_API_VERSION, LoaderPlugin, ModelRef, PluginInfo

_CALLABLE_PREFIXES = ("callable:", "python:", "py:")


def _parse_callable_uri(uri: str) -> tuple[str, str] | None:
    lower = uri.lower()
    for prefix in _CALLABLE_PREFIXES:
        if lower.startswith(prefix):
            rest = uri[len(prefix) :]
            if ":" not in rest:
                return None
            module_name, attr = rest.rsplit(":", 1)
            return module_name, attr
    return None


class CallableLoader:
    name = "callable"
    api_version = PLUGIN_API_VERSION

    def can_load(self, uri: str) -> float:
        if _parse_callable_uri(uri):
            return 0.9
        return 0.0

    def load(self, uri: str) -> ModelRef:
        parsed = _parse_callable_uri(uri)
        if parsed is None:
            raise ValueError(f"Not a callable URI: {uri} (use callable:module:attr)")
        module_name, attr = parsed
        cache_path = cache_dir_for("callable", uri)
        metadata: dict[str, object] = {
            "source": "callable",
            "module": module_name,
            "attr": attr,
            "cache_path": str(cache_path),
        }
        try:
            module = importlib.import_module(module_name)
            obj = getattr(module, attr)
            metadata["callable_type"] = type(obj).__name__
        except Exception as exc:
            metadata["import_error"] = str(exc)
        write_metadata(cache_path, metadata)
        return ModelRef(
            id=str(uuid.uuid4())[:8],
            uri=uri,
            kind="generic",
            metadata=metadata,
        )

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="loader",
            summary="Load Python callables via callable:module.path:attr.",
            requires_api=">=1,<2",
        )


_: LoaderPlugin = CallableLoader()
