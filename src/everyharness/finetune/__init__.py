"""Fine-tune adapters for supported harnesses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from everyharness.plugin.protocols import ModelRef, TrainOpts

__all__ = ["finetune_model", "supported_for", "unsupported_message"]


_SUPPORTED: dict[str, set[str]] = {
    "tabular": {"retrain", "partial_fit"},
    "llm": {"lora", "qlora"},
    "vision": {"head"},
    "embeddings": {"contrastive"},
    "diffusion": {"dreambooth", "lora"},
}


def supported_for(harness: str) -> set[str]:
    return _SUPPORTED.get(harness, set())


def unsupported_message(harness: str, method: str | None = None) -> str:
    methods = supported_for(harness)
    if not methods:
        return f"Harness '{harness}' does not support fine-tuning in v1."
    if method and method not in methods:
        return (
            f"Method '{method}' is not supported for '{harness}'. "
            f"Supported: {', '.join(sorted(methods))}"
        )
    return ""


def finetune_model(
    model: ModelRef,
    dataset: Path,
    opts: TrainOpts,
    *,
    harness: str,
) -> ModelRef:
    """Dispatch to the appropriate fine-tune adapter."""
    method = str(opts.extra.get("method", "default"))
    if harness == "tabular":
        from everyharness.finetune.sklearn_adapter import finetune_sklearn

        return finetune_sklearn(model, dataset, opts)
    if harness == "llm":
        from everyharness.finetune.lora import finetune_lora

        return finetune_lora(model, dataset, opts)
    if harness == "vision":
        from everyharness.finetune.vision_head import finetune_vision_head

        return finetune_vision_head(model, dataset, opts)
    if harness == "embeddings":
        from everyharness.finetune.embeddings import finetune_embeddings

        return finetune_embeddings(model, dataset, opts)
    if harness == "diffusion":
        from everyharness.finetune.lora import finetune_lora

        return finetune_lora(model, dataset, opts, kind="diffusion")
    msg = unsupported_message(harness, method if method != "default" else None)
    raise NotImplementedError(msg or f"Fine-tune not supported for harness: {harness}")


def load_train_dataset(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    if path.suffix == ".json":
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    if path.suffix == ".jsonl":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return {"rows": rows}
    raise ValueError(f"Unsupported dataset format: {path.suffix} (use .json or .jsonl)")
