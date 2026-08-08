"""Tabular harness tests."""

import json

import pytest

from everyharness.harnesses.tabular import TabularHarness
from everyharness.plugin.protocols import ModelRef


@pytest.fixture
def sklearn_model(tmp_path):
    joblib = pytest.importorskip("joblib")
    pytest.importorskip("sklearn")
    from sklearn.linear_model import LogisticRegression

    X = [[0.0], [1.0], [2.0], [3.0]]
    y = [0, 0, 1, 1]
    est = LogisticRegression()
    est.fit(X, y)
    path = tmp_path / "model.joblib"
    joblib.dump(est, path)
    return path


def test_tabular_predict(sklearn_model, tmp_path, capsys):
    harness = TabularHarness()
    model = ModelRef(
        id="t1",
        uri=str(sklearn_model),
        kind="tabular",
        metadata={"cached_path": str(sklearn_model)},
    )
    payload = tmp_path / "features.json"
    payload.write_text(json.dumps([[1.5]]), encoding="utf-8")
    code = harness.run_cli(
        model,
        ["predict", "--input", str(payload), "--trust-pickle"],
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "predictions" in out
