"""Hugging Face Hub loader."""

from __future__ import annotations

import uuid

from everyharness.core.config import is_offline
from everyharness.core.detect import kind_from_uri
from everyharness.core.errors import OfflineError
from everyharness.loaders._cache import cache_dir_for, read_metadata, write_metadata
from everyharness.plugin.protocols import PLUGIN_API_VERSION, LoaderPlugin, ModelRef, PluginInfo

_HF_PREFIXES = ("hf:", "huggingface:", "hf://", "huggingface://")


def _parse_hf_uri(uri: str) -> str | None:
    lower = uri.lower()
    for prefix in _HF_PREFIXES:
        if lower.startswith(prefix):
            return uri[len(prefix) :].strip("/")
    return None


class HuggingFaceLoader:
    name = "huggingface"
    api_version = PLUGIN_API_VERSION

    def can_load(self, uri: str) -> float:
        if _parse_hf_uri(uri):
            return 0.95
        return 0.0

    def load(self, uri: str) -> ModelRef:
        repo_id = _parse_hf_uri(uri)
        if repo_id is None:
            raise ValueError(f"Not a Hugging Face URI: {uri}")
        cache_path = cache_dir_for("hf", repo_id)
        metadata: dict[str, object] = {
            "source": "huggingface",
            "repo_id": repo_id,
            "cache_path": str(cache_path),
        }
        existing = read_metadata(cache_path)
        if existing:
            metadata.update(existing)
        elif not is_offline():
            try:
                from huggingface_hub import snapshot_download

                local_dir = snapshot_download(
                    repo_id=repo_id,
                    local_dir=str(cache_path / "snapshot"),
                )
                metadata["snapshot_path"] = local_dir
                write_metadata(cache_path, metadata)
            except ImportError:
                metadata["note"] = "huggingface-hub not installed; metadata only"
                write_metadata(cache_path, metadata)
        else:
            if not (cache_path / "snapshot").exists():
                raise OfflineError(
                    f"Model {repo_id} not cached and EVERYHARNESS_OFFLINE=1"
                )
            metadata["snapshot_path"] = str(cache_path / "snapshot")
        kind = kind_from_uri(str(cache_path / "snapshot")) or "llm"
        return ModelRef(
            id=str(uuid.uuid4())[:8],
            uri=uri,
            kind=kind,
            metadata=metadata,
        )

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="loader",
            summary="Load models from Hugging Face Hub (hf:org/model) with offline cache.",
            requires_api=">=1,<2",
        )


_: LoaderPlugin = HuggingFaceLoader()
