"""Embeddings contrastive fine-tune adapter."""

from __future__ import annotations

import uuid
from pathlib import Path

from everyharness.core.config import data_dir
from everyharness.finetune import load_train_dataset
from everyharness.plugin.protocols import ModelRef, TrainOpts


def finetune_embeddings(model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
    data = load_train_dataset(dataset)
    pairs = data.get("pairs") or data.get("rows")
    if not pairs:
        raise ValueError('Embeddings dataset must include "pairs" or "rows" with anchor/positive')
    import importlib.util

    if importlib.util.find_spec("sentence_transformers") is None:
        raise NotImplementedError(
            "Embeddings contrastive fine-tune requires sentence-transformers. "
            "Install with: pip install 'everyharness[embeddings,train]'"
        )
    from sentence_transformers import SentenceTransformer  # noqa: F401

    out_dir = opts.output_dir or (data_dir() / "finetune" / model.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    return ModelRef(
        id=str(uuid.uuid4())[:8],
        uri=str(out_dir),
        kind="embeddings",
        metadata={
            "parent": model.id,
            "method": "contrastive",
            "status": "scaffold-only",
            "pairs": len(pairs),
        },
    )
