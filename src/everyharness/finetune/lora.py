"""LoRA / QLoRA fine-tune adapter (optional heavy deps)."""

from __future__ import annotations

from pathlib import Path

from everyharness.core.config import data_dir
from everyharness.finetune import load_train_dataset
from everyharness.plugin.protocols import ModelRef, TrainOpts


def finetune_lora(
    model: ModelRef,
    dataset: Path,
    opts: TrainOpts,
    *,
    kind: str = "llm",
) -> ModelRef:
    _ = load_train_dataset(dataset)
    method = str(opts.extra.get("method", "lora"))
    try:
        import torch  # noqa: F401
        from peft import LoraConfig  # noqa: F401
        from transformers import AutoModelForCausalLM  # noqa: F401
    except ImportError as exc:
        raise NotImplementedError(
            f"{kind} {method} fine-tune requires torch, transformers, and peft. "
            "Install with: pip install 'everyharness[train]' and the ML stack for your platform."
        ) from exc

    out_dir = opts.output_dir or (data_dir() / "finetune" / model.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = out_dir / "training_manifest.json"
    manifest.write_text(
        '{"status": "not-run", "reason": "LoRA training scaffold only in v1"}\n',
        encoding="utf-8",
    )
    raise NotImplementedError(
        f"{kind} {method} training requires a full ML stack; manifest written to {manifest}"
    )
