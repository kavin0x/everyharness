"""Generic harness — fallback for unknown model types."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from everyharness.harnesses._util import print_json, read_json_input
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


class GenericHarness:
    name = "generic"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        return 0.1

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: info | predict [--input FILE] | call [--input FILE]")
            return 1
        cmd = argv[0]
        rest = argv[1:]
        input_path = None
        if "--input" in rest:
            input_path = rest[rest.index("--input") + 1]
        if cmd == "info":
            print_json(
                {
                    "id": model.id,
                    "uri": model.uri,
                    "kind": model.kind,
                    "metadata": model.metadata,
                }
            )
            return 0
        if cmd == "predict":
            data = read_json_input(input_path)
            if model.metadata.get("source") == "callable":
                result = _invoke_callable(model, data)
                print_json({"result": result})
                return 0
            print_json({"message": "generic predict stub", "input": data})
            return 0
        if cmd == "call":
            data = read_json_input(input_path) or {}
            result = _invoke_callable(model, data)
            print_json({"result": result})
            return 0
        print(f"Unknown generic command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError("Use a specialized harness serve() for HTTP endpoints")

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        raise NotImplementedError("Generic harness does not support fine-tuning")

    def templates(self) -> list[TemplateRef]:
        return [TemplateRef(pack="cli-stub", name="main", description="CLI stub template")]

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Fallback harness for unknown model types and Python callables.",
            requires_api=">=1,<2",
        )


def _invoke_callable(model: ModelRef, data: Any) -> Any:
    module_name = model.metadata.get("module")
    attr = model.metadata.get("attr")
    if not module_name or not attr:
        raise ValueError("Model is not a Python callable reference")
    module = importlib.import_module(str(module_name))
    fn = getattr(module, str(attr))
    if callable(fn):
        return fn(data)
    return fn
