"""Vision transfer-head fine-tune adapter."""

from __future__ import annotations

import uuid
from pathlib import Path

from everyharness.core.config import data_dir
from everyharness.finetune import load_train_dataset
from everyharness.plugin.protocols import ModelRef, TrainOpts


def finetune_vision_head(model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
    data = load_train_dataset(dataset)
    if "images" not in data or "labels" not in data:
        raise ValueError('Vision dataset must be JSON {"images": [...], "labels": [...]}')
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForImageClassification  # noqa: F401
    except ImportError as exc:
        raise NotImplementedError(
            "Vision head fine-tune requires torch and transformers. "
            "Install with: pip install 'everyharness[vision,train]'"
        ) from exc

    out_dir = opts.output_dir or (data_dir() / "finetune" / model.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    return ModelRef(
        id=str(uuid.uuid4())[:8],
        uri=str(out_dir),
        kind="vision",
        metadata={
            "parent": model.id,
            "method": "head",
            "status": "scaffold-only",
            "samples": len(data["images"]),
        },
    )
