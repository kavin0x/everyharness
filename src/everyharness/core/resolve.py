"""Model resolution: loaders, detection, harness selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from everyharness.core.detect import detect_kind, kind_from_uri
from everyharness.core.errors import PluginError, RegistryError
from everyharness.plugin.host import PluginHost
from everyharness.plugin.protocols import DetectorPlugin, HarnessPlugin, LoaderPlugin, ModelRef


def pick_loader(uri: str, loaders: list[LoaderPlugin]) -> LoaderPlugin | None:
    """Return the loader with the highest can_load score."""
    best: LoaderPlugin | None = None
    best_score = 0.0
    for loader in loaders:
        try:
            score = float(loader.can_load(uri))
        except Exception:
            continue
        if score > best_score:
            best_score = score
            best = loader
    return best if best_score > 0 else None


def _looks_like_local_path(uri: str) -> bool:
    """True when uri is a filesystem path rather than a scheme-based ref."""
    if "://" in uri:
        return False
    if uri.startswith((".", "/", "~")):
        return True
    if ":" in uri:
        scheme = uri.split(":", 1)[0]
        # macOS/Linux only in v1 — treat alpha schemes as non-paths (hf:, embeddings:, …)
        if scheme.isalpha() and len(scheme) > 1:
            return False
    return bool(Path(uri).suffix)


def load_model_ref(
    uri: str,
    loaders: list[LoaderPlugin],
    *,
    kind: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ModelRef:
    """Resolve a URI through loaders; fall back to a bare ModelRef."""
    loader = pick_loader(uri, loaders)
    if loader is None:
        path = Path(uri).expanduser()
        if _looks_like_local_path(uri) and not path.exists():
            raise RegistryError(f"Local path not found: {uri}")
        ref = ModelRef(id="", uri=uri)
    else:
        try:
            ref = loader.load(uri)
        except FileNotFoundError as exc:
            raise RegistryError(str(exc)) from exc
    merged_meta = dict(ref.metadata)
    if metadata:
        merged_meta.update(metadata)
    resolved_kind = kind or ref.kind or kind_from_uri(uri)
    return ModelRef(
        id=ref.id,
        uri=ref.uri,
        kind=resolved_kind,
        metadata=merged_meta,
    )


def refine_kind(model: ModelRef, detectors: list[DetectorPlugin]) -> str | None:
    """Run detectors and merge with existing kind hint."""
    detected = detect_kind(model, detectors)
    if detected:
        return detected
    return model.kind or kind_from_uri(model.uri)


def pick_harness(model: ModelRef, harnesses: list[HarnessPlugin]) -> HarnessPlugin:
    """Select the best-matching harness; generic is the fallback."""
    if model.kind:
        for harness in harnesses:
            if harness.name == model.kind:
                return harness
    best: HarnessPlugin | None = None
    best_score = -1.0
    generic: HarnessPlugin | None = None
    for harness in harnesses:
        if harness.name == "generic":
            generic = harness
        try:
            score = float(harness.matches(model))
        except Exception:
            continue
        if score > best_score:
            best_score = score
            best = harness
    if best is not None and best_score > 0:
        return best
    if generic is not None:
        return generic
    if harnesses:
        return harnesses[0]
    raise PluginError("No harness plugins discovered")


def resolve_for_run(
    model_id: str,
    host: PluginHost,
    *,
    registry: Any | None = None,
) -> tuple[ModelRef, HarnessPlugin]:
    """Load a registered model and pick its harness."""
    from everyharness.core.registry import ModelRegistry

    reg = registry or ModelRegistry()
    record = reg.get(model_id)
    if record is None:
        raise RegistryError(f"Unknown model id: {model_id}")
    model = record.to_model_ref()
    if model.kind is None:
        model = ModelRef(
            id=model.id,
            uri=model.uri,
            kind=refine_kind(model, host.detectors),
            metadata=model.metadata,
        )
    harness = pick_harness(model, host.harnesses)
    return model, harness


def is_pickle_path(uri: str) -> bool:
    lower = uri.lower()
    return lower.endswith((".pkl", ".pickle", ".joblib"))


def require_pickle_trust(uri: str, trust_pickle: bool) -> None:
    if is_pickle_path(uri) and not trust_pickle:
        raise RegistryError(
            "Pickle/joblib models require --trust-pickle (untrusted pickle can execute code)"
        )


def local_path_exists(uri: str) -> bool:
    path = Path(uri)
    return path.exists() and path.is_file()
