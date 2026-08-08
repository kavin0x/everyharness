"""Sklearn retrain / partial_fit adapter."""

from __future__ import annotations

import uuid
from pathlib import Path

from everyharness.core.config import data_dir
from everyharness.finetune import load_train_dataset
from everyharness.plugin.protocols import ModelRef, TrainOpts


def finetune_sklearn(model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
    try:
        import joblib
        from sklearn.base import clone
    except ImportError as exc:
        raise ImportError(
            "tabular fine-tune requires scikit-learn and joblib "
            "(pip install 'everyharness[tabular,train]')"
        ) from exc

    data = load_train_dataset(dataset)
    if "X" not in data or "y" not in data:
        raise ValueError('Tabular dataset must be JSON {"X": [...], "y": [...]}')

    path = model.metadata.get("cached_path") or model.uri
    estimator = joblib.load(path)
    method = str(opts.extra.get("method", "retrain"))
    if method == "partial_fit" and hasattr(estimator, "partial_fit"):
        estimator.partial_fit(data["X"], data["y"])
    else:
        fresh = clone(estimator)
        fresh.fit(data["X"], data["y"])
        estimator = fresh

    out_dir = opts.output_dir or (data_dir() / "finetune" / model.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "model.joblib"
    joblib.dump(estimator, out_path)
    return ModelRef(
        id=str(uuid.uuid4())[:8],
        uri=str(out_path),
        kind="tabular",
        metadata={"parent": model.id, "method": method, "epochs": opts.epochs},
    )
