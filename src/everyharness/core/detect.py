"""Type detection (built-in + plugin hook point)."""

from __future__ import annotations

from pathlib import Path

from everyharness.plugin.protocols import DetectorPlugin, ModelRef, PluginInfo

PLUGIN_API_VERSION = "1.0.0"

_EXTENSION_KINDS: dict[str, str] = {
    ".pkl": "tabular",
    ".pickle": "tabular",
    ".joblib": "tabular",
    ".onnx": "vision",
    ".gguf": "llm",
    ".safetensors": "llm",
    ".pt": "vision",
    ".pth": "vision",
    ".bin": "llm",
    ".wav": "speech",
    ".mp3": "speech",
    ".flac": "speech",
    ".png": "vision",
    ".jpg": "vision",
    ".jpeg": "vision",
    ".webp": "vision",
}

_URI_PREFIX_KINDS: list[tuple[str, str]] = [
    ("ollama:", "llm"),
    ("ollama://", "llm"),
    ("hf:", "llm"),
    ("huggingface:", "llm"),
    ("callable:", "generic"),
    ("python:", "generic"),
    ("embeddings:", "embeddings"),
    ("diffusion:", "diffusion"),
    ("computer:", "computer"),
]


def kind_from_uri(uri: str) -> str | None:
    """Infer model kind from URI patterns and file extensions."""
    lower = uri.lower().strip()
    for prefix, kind in _URI_PREFIX_KINDS:
        if lower.startswith(prefix):
            return kind
    path = Path(uri)
    suffix = path.suffix.lower()
    if suffix in _EXTENSION_KINDS:
        return _EXTENSION_KINDS[suffix]
    if path.is_dir():
        config = path / "config.json"
        if config.exists():
            try:
                import json

                data = json.loads(config.read_text(encoding="utf-8"))
                arch = str(data.get("architectures", data.get("model_type", ""))).lower()
                if "whisper" in arch or "wav2vec" in arch:
                    return "speech"
                if "clip" in arch or "vit" in arch or "detr" in arch:
                    return "vision"
                if "diffusion" in arch or "unet" in arch:
                    return "diffusion"
                if "bert" in arch or "sentence" in arch or "embedding" in arch:
                    return "embeddings"
                return "llm"
            except Exception:
                return "llm"
    return None


class BuiltinDetector:
    """Built-in detector using URI patterns, extensions, and metadata hints."""

    name = "builtin"
    api_version = PLUGIN_API_VERSION

    def score(self, model: ModelRef) -> float:
        if model.kind:
            return 0.95
        uri_kind = kind_from_uri(model.uri)
        if uri_kind:
            return 0.85
        meta_kind = model.metadata.get("kind")
        if isinstance(meta_kind, str):
            return 0.8
        lower = model.uri.lower()
        if lower.endswith((".pkl", ".joblib", ".onnx", ".gguf", ".safetensors")):
            return 0.3
        return 0.0

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="detector",
            summary="Built-in URI/extension/metadata kind detector.",
            requires_api=">=1,<2",
        )


def detect_kind(model: ModelRef, detectors: list[DetectorPlugin]) -> str | None:
    """Pick the best kind hint from model metadata, URI, and detector plugins."""
    if model.kind:
        return model.kind
    uri_kind = kind_from_uri(model.uri)
    meta_kind = model.metadata.get("kind")
    if isinstance(meta_kind, str):
        return meta_kind
    if uri_kind:
        return uri_kind

    best_score = 0.0
    best_kind: str | None = None
    for detector in detectors:
        try:
            score = float(detector.score(model))
        except Exception:
            continue
        if score > best_score:
            best_score = score
            if detector.name == "builtin":
                best_kind = kind_from_uri(model.uri) or model.kind
            else:
                best_kind = model.metadata.get("kind") or kind_from_uri(model.uri)
    return best_kind
