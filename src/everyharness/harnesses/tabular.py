"""Tabular model harness (sklearn/joblib)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from everyharness.finetune import finetune_model
from everyharness.harnesses._util import missing_extra, print_json, read_json_input
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


def _load_sklearn_model(model: ModelRef, *, trust_pickle: bool = False) -> Any:
    from everyharness.core.resolve import require_pickle_trust

    path = model.metadata.get("cached_path") or model.uri
    require_pickle_trust(str(path), trust_pickle)
    try:
        import joblib
    except ImportError as exc:
        raise ImportError("joblib required for tabular models") from exc
    return joblib.load(path)


class TabularHarness:
    name = "tabular"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "tabular":
            return 0.95
        uri = model.uri.lower()
        if uri.endswith((".pkl", ".pickle", ".joblib")):
            return 0.9
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: predict | evaluate | explain [--input FILE] [--trust-pickle]")
            return 1
        cmd = argv[0]
        rest = argv[1:]
        trust_pickle = "--trust-pickle" in rest
        input_path = None
        if "--input" in rest:
            idx = rest.index("--input")
            if idx + 1 < len(rest):
                input_path = rest[idx + 1]
        try:
            estimator = _load_sklearn_model(model, trust_pickle=trust_pickle)
        except Exception as exc:
            if "joblib" in str(exc).lower() or isinstance(exc, ImportError):
                return missing_extra("tabular harness", "tabular")
            print(f"Load error: {exc}", file=sys.stderr)
            return 1
        if cmd == "predict":
            data = read_json_input(input_path)
            if data is None:
                print("Provide JSON features via --input or stdin", file=sys.stderr)
                return 1
            features = data if isinstance(data, list) else [data]
            preds = estimator.predict(features)
            print_json({"predictions": preds.tolist() if hasattr(preds, "tolist") else list(preds)})
            return 0
        if cmd == "evaluate":
            data = read_json_input(input_path)
            if not isinstance(data, dict) or "X" not in data or "y" not in data:
                print('Evaluate expects JSON {"X": [...], "y": [...]}', file=sys.stderr)
                return 1
            preds = estimator.predict(data["X"])
            y_true = data["y"]
            if hasattr(estimator, "score"):
                score = float(estimator.score(data["X"], y_true))
            else:
                score = float((preds == y_true).mean()) if len(y_true) else 0.0
            print_json({"score": score, "predictions": list(preds)})
            return 0
        if cmd == "explain":
            result: dict[str, Any] = {"model": type(estimator).__name__}
            if hasattr(estimator, "feature_importances_"):
                result["feature_importances"] = list(estimator.feature_importances_)
            elif hasattr(estimator, "coef_"):
                coef = estimator.coef_
                result["coef"] = coef.tolist() if hasattr(coef, "tolist") else coef
            else:
                result["message"] = "No explainable attributes on this estimator"
            print_json(result)
            return 0
        print(f"Unknown tabular command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        try:
            import uvicorn
            from fastapi import FastAPI
        except ImportError:
            missing_extra("tabular serve", "tabular")
            return
        app = FastAPI(title="everyharness tabular")
        estimator = _load_sklearn_model(model, trust_pickle=True)

        @app.post("/predict")
        def predict(payload: dict[str, Any]) -> dict[str, Any]:
            features = payload.get("features") or payload.get("X")
            preds = estimator.predict(features)
            return {"predictions": preds.tolist() if hasattr(preds, "tolist") else list(preds)}

        uvicorn.run(app, host=host, port=port, log_level="warning")

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        return finetune_model(model, dataset, opts, harness=self.name)

    def templates(self) -> list[TemplateRef]:
        return [TemplateRef(pack="cli-stub", name="main", description="CLI stub template")]

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Tabular predict/evaluate/explain for sklearn/joblib models.",
            requires_api=">=1,<2",
        )
