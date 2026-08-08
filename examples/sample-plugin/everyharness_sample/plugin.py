"""Example third-party harness plugin (documentation only)."""

from __future__ import annotations

from pathlib import Path

from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


class SampleHarness:
    name = "sample"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        return 1.0 if model.kind == "sample" else 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        print(f"sample harness: {model.uri}")
        return 0

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        raise NotImplementedError

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Documentation sample harness plugin.",
            requires_api=">=1,<2",
        )
