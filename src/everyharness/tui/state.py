"""Shared TUI state."""

from __future__ import annotations

from dataclasses import dataclass, field

from everyharness.core.registry import ModelRecord, ModelRegistry
from everyharness.plugin.host import PluginHost
from everyharness.plugin.protocols import HarnessPlugin, ModelRef


@dataclass
class AppState:
    """Mutable state shared across TUI panels."""

    host: PluginHost
    selected_model_id: str | None = None
    serve_running: bool = False
    serve_host: str = "127.0.0.1"
    serve_port: int = 8000
    serve_model_id: str | None = None
    last_run_argv: list[str] = field(default_factory=list)

    def registry(self) -> ModelRegistry:
        from everyharness.core.registry import ModelRegistry

        return ModelRegistry()

    def selected_record(self) -> ModelRecord | None:
        if not self.selected_model_id:
            return None
        return self.registry().get(self.selected_model_id)

    def selected_model_ref(self) -> ModelRef | None:
        record = self.selected_record()
        return record.to_model_ref() if record else None

    def find_harness(self, model: ModelRef) -> HarnessPlugin | None:
        from everyharness.core.resolve import pick_harness

        try:
            return pick_harness(model, self.host.harnesses)
        except Exception:
            return None

    def harness_for_selected(self) -> HarnessPlugin | None:
        model = self.selected_model_ref()
        if model is None:
            return None
        return self.find_harness(model)
