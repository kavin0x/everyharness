"""Fine-tune adapter tests."""

import json
from pathlib import Path

import pytest

from everyharness.finetune import finetune_model, supported_for, unsupported_message
from everyharness.plugin.protocols import ModelRef, TrainOpts


def test_supported_methods():
    assert "retrain" in supported_for("tabular")
    assert "lora" in supported_for("llm")
    assert unsupported_message("computer")


def test_sklearn_retrain(tmp_path):
    joblib = pytest.importorskip("joblib")
    pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    est = LogisticRegression()
    est.fit([[0], [1], [2], [3]], [0, 0, 1, 1])
    model_path = tmp_path / "base.joblib"
    joblib.dump(est, model_path)
    dataset = tmp_path / "train.json"
    dataset.write_text(
        json.dumps({"X": [[0], [1], [2], [3]], "y": [0, 0, 1, 1]}),
        encoding="utf-8",
    )
    model = ModelRef(
        id="m1",
        uri=str(model_path),
        kind="tabular",
        metadata={"cached_path": str(model_path)},
    )
    result = finetune_model(
        model,
        dataset,
        TrainOpts(output_dir=tmp_path / "out"),
        harness="tabular",
    )
    assert result.kind == "tabular"
    assert Path(result.uri).exists()
