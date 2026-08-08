"""Streaming-friendly run console."""

from __future__ import annotations

import shlex
import threading
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, RichLog, Static

from everyharness.tui.panels.base import EmptyState, PanelBody, PanelHeader
from everyharness.tui.state import AppState

if TYPE_CHECKING:
    from everyharness.plugin.protocols import HarnessPlugin, ModelRef


class _StreamWriter:
    """Redirect stdout/stderr into a RichLog widget."""

    def __init__(self, log: RichLog) -> None:
        self._log = log

    def write(self, text: str) -> None:
        if text:
            self._log.write(text)

    def flush(self) -> None:
        pass


class RunConsolePanel(Vertical):
    """Run harness CLI with live output."""

    DEFAULT_CSS = """
    RunConsolePanel {
        height: 1fr;
    }

    RunConsolePanel #run-controls {
        height: auto;
        padding: 0 2 1 2;
    }

    RunConsolePanel #run-controls Input {
        width: 1fr;
    }

    RunConsolePanel RichLog {
        height: 1fr;
        margin: 0 2;
        border: solid $primary-darken-2;
        background: $surface;
    }

    RunConsolePanel #run-status {
        height: auto;
        padding: 0 2;
        color: $text-muted;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state
        self._running = False

    def compose(self) -> ComposeResult:
        yield PanelHeader("Run Console")
        with PanelBody():
            yield EmptyState(
                "Select a model in Library, then enter CLI arguments below.",
                id="run-empty",
            )
            with Horizontal(id="run-controls"):
                yield Input(placeholder="Arguments (e.g. predict --input data.csv)", id="run-args")
                yield Button("Run", variant="primary", id="run-btn")
                yield Button("Clear", id="clear-btn")
            yield RichLog(id="run-log", highlight=True, markup=True, wrap=True)
            yield Static("Ready.", id="run-status")

    def on_mount(self) -> None:
        self._sync_empty_state()

    def _sync_empty_state(self) -> None:
        empty = self.query_one("#run-empty", EmptyState)
        empty.display = self.state.selected_record() is None

    def refresh_context(self) -> None:
        self._sync_empty_state()
        record = self.state.selected_record()
        status = self.query_one("#run-status", Static)
        if record is None:
            status.update("No model selected.")
            return
        harness = self.state.harness_for_selected()
        harness_name = harness.name if harness else "none"
        status.update(f"Model {record.id} → harness [cyan]{harness_name}[/cyan]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear-btn":
            self.query_one("#run-log", RichLog).clear()
            return
        if event.button.id != "run-btn":
            return
        if self._running:
            self.app.notify("Run already in progress.", severity="warning")
            return
        model = self.state.selected_model_ref()
        if model is None:
            self.app.notify("Select a model in Library first.", severity="warning")
            return
        harness = self.state.harness_for_selected()
        if harness is None:
            self.app.notify("No harness available for this model.", severity="error")
            return
        raw_args = self.query_one("#run-args", Input).value.strip()
        argv = shlex.split(raw_args) if raw_args else []
        self.state.last_run_argv = argv
        self._start_run(model, harness, argv)

    def _start_run(self, model: ModelRef, harness: HarnessPlugin, argv: list[str]) -> None:
        log = self.query_one("#run-log", RichLog)
        status = self.query_one("#run-status", Static)
        self._running = True
        self.query_one("#run-btn", Button).disabled = True
        log.write(f"[bold]everyharness run {model.id}[/bold] {' '.join(argv)}\n")
        log.write(f"[dim]harness={harness.name}[/dim]\n")
        status.update("Running…")

        def worker() -> None:
            writer = _StreamWriter(log)
            rc = 1
            try:
                import sys

                old_out, old_err = sys.stdout, sys.stderr
                sys.stdout = writer
                sys.stderr = writer
                try:
                    rc = harness.run_cli(model, argv)
                finally:
                    sys.stdout = old_out
                    sys.stderr = old_err
            except Exception as exc:
                log.write(f"[red]Error: {exc}[/red]\n")
                rc = 1
            self.app.call_from_thread(self._finish_run, rc)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_run(self, rc: int) -> None:
        self._running = False
        self.query_one("#run-btn", Button).disabled = False
        log = self.query_one("#run-log", RichLog)
        color = "green" if rc == 0 else "red"
        log.write(f"\n[bold {color}]exit {rc}[/bold {color}]\n")
        status = self.query_one("#run-status", Static)
        status.update(f"Finished with exit code {rc}.")
