"""Ollama model loader."""

from __future__ import annotations

import uuid

import httpx

from everyharness.core.config import is_offline
from everyharness.loaders._cache import cache_dir_for, write_metadata
from everyharness.plugin.protocols import PLUGIN_API_VERSION, LoaderPlugin, ModelRef, PluginInfo

_OLLAMA_PREFIXES = ("ollama:", "ollama://")


def _parse_ollama_uri(uri: str) -> str | None:
    lower = uri.lower()
    for prefix in _OLLAMA_PREFIXES:
        if lower.startswith(prefix):
            return uri[len(prefix) :].strip("/")
    return None


def _ollama_base() -> str:
    import os

    return os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")


class OllamaLoader:
    name = "ollama"
    api_version = PLUGIN_API_VERSION

    def can_load(self, uri: str) -> float:
        if _parse_ollama_uri(uri):
            return 0.95
        return 0.0

    def load(self, uri: str) -> ModelRef:
        model_name = _parse_ollama_uri(uri)
        if model_name is None:
            raise ValueError(f"Not an Ollama URI: {uri}")
        cache_path = cache_dir_for("ollama", model_name)
        metadata: dict[str, object] = {
            "source": "ollama",
            "model": model_name,
            "base_url": _ollama_base(),
            "cache_path": str(cache_path),
        }
        if not is_offline():
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.get(f"{_ollama_base()}/api/tags")
                    resp.raise_for_status()
                    tags = resp.json().get("models", [])
                    names = {m.get("name", "").split(":")[0] for m in tags}
                    metadata["available"] = model_name.split(":")[0] in names
            except Exception as exc:
                metadata["probe_error"] = str(exc)
        else:
            metadata["offline"] = True
        write_metadata(cache_path, metadata)
        return ModelRef(
            id=str(uuid.uuid4())[:8],
            uri=uri,
            kind="llm",
            metadata=metadata,
        )

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="loader",
            summary="Reference Ollama models (ollama:model) via local daemon.",
            requires_api=">=1,<2",
        )


_: LoaderPlugin = OllamaLoader()
