"""Basic train wizard panel."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, RichLog, Static

from everyharness.plugin.protocols import TrainOpts
from everyharness.tui.panels.base import EmptyState, PanelBody, PanelHeader
from everyharness.tui.state import AppState

if TYPE_CHECKING:
    from everyharness.plugin.protocols import HarnessPlugin, ModelRef


class TrainWizardPanel(Vertical):
    """Fine-tune wizard (basic — calls harness.finetune when supported)."""

    DEFAULT_CSS = """
    TrainWizardPanel {
        height: 1fr;
    }

    TrainWizardPanel .train-field {
        height: auto;
        padding: 0 2;
    }

    TrainWizardPanel .train-label {
        width: 14;
        color: $text-muted;
    }

    TrainWizardPanel RichLog {
        height: 1fr;
        margin: 1 2;
        border: solid $primary-darken-2;
    }

    TrainWizardPanel #train-actions {
        height: auto;
        padding: 0 2 1 2;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state
        self._running = False

    def compose(self) -> ComposeResult:
        yield PanelHeader("Train Wizard")
        with PanelBody():
            yield EmptyState("Select a model in Library to configure training.", id="train-empty")
            yield Static("", id="train-model-line", classes="train-field")
            with Horizontal(classes="train-field"):
                yield Static("Dataset path", classes="train-label")
                yield Input(placeholder="./data/train.csv", id="train-dataset")
            with Horizontal(classes="train-field"):
                yield Static("Epochs", classes="train-label")
                yield Input(value="1", id="train-epochs")
            with Horizontal(classes="train-field"):
                yield Static("Learning rate", classes="train-label")
                yield Input(value="0.0001", id="train-lr")
            with Horizontal(classes="train-field"):
                yield Static("Output dir", classes="train-label")
                yield Input(placeholder="optional", id="train-out")
            with Horizontal(id="train-actions"):
                yield Button("Start training", variant="primary", id="train-btn")
                yield Button("Clear log", id="train-clear-btn")
            yield RichLog(id="train-log", highlight=True, markup=True)
            yield Static("", id="train-status")

    def on_mount(self) -> None:
        self.refresh_context()

    def refresh_context(self) -> None:
        empty = self.query_one("#train-empty", EmptyState)
        line = self.query_one("#train-model-line", Static)
        record = self.state.selected_record()
        empty.display = record is None
        if record is None:
            line.update("")
            return
        harness = self.state.harness_for_selected()
        harness_name = harness.name if harness else "none"
        line.update(f"Model [cyan]{record.id}[/cyan] → harness [cyan]{harness_name}[/cyan]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "train-clear-btn":
            self.query_one("#train-log", RichLog).clear()
            return
        if event.button.id != "train-btn":
            return
        if self._running:
            self.app.notify("Training already in progress.", severity="warning")
            return
        model = self.state.selected_model_ref()
        if model is None:
            self.app.notify("Select a model first.", severity="warning")
            return
        harness = self.state.harness_for_selected()
        if harness is None:
            self.app.notify("No harness for this model.", severity="error")
            return
        dataset_raw = self.query_one("#train-dataset", Input).value.strip()
        if not dataset_raw:
            self.app.notify("Dataset path is required.", severity="warning")
            return
        dataset = Path(dataset_raw)
        if not dataset.exists():
            self.app.notify(f"Dataset not found: {dataset}", severity="error")
            return
        try:
            epochs = int(self.query_one("#train-epochs", Input).value.strip() or "1")
            lr = float(self.query_one("#train-lr", Input).value.strip() or "1e-4")
        except ValueError:
            self.app.notify("Invalid epochs or learning rate.", severity="error")
            return
        out_raw = self.query_one("#train-out", Input).value.strip()
        out_dir = Path(out_raw) if out_raw else None
        opts = TrainOpts(epochs=epochs, learning_rate=lr, output_dir=out_dir)
        self._start_train(model, harness, dataset, opts)

    def _start_train(
        self,
        model: ModelRef,
        harness: HarnessPlugin,
        dataset: Path,
        opts: TrainOpts,
    ) -> None:
        log = self.query_one("#train-log", RichLog)
        status = self.query_one("#train-status", Static)
        self._running = True
        self.query_one("#train-btn", Button).disabled = True
        log.write(
            f"[bold]everyharness train {model.id}[/bold] dataset={dataset} "
            f"epochs={opts.epochs} lr={opts.learning_rate}\n"
        )
        status.update("Training…")

        def worker() -> None:
            try:
                result = harness.finetune(model, dataset, opts)
                self.app.call_from_thread(self._finish_train, True, f"New model: {result.id}")
            except NotImplementedError:
                self.app.call_from_thread(
                    self._finish_train,
                    False,
                    "This harness does not support training yet. "
                    "Install a harness with train support or wait for a future release.",
                )
            except Exception as exc:
                self.app.call_from_thread(self._finish_train, False, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_train(self, ok: bool, message: str) -> None:
        self._running = False
        self.query_one("#train-btn", Button).disabled = False
        log = self.query_one("#train-log", RichLog)
        color = "green" if ok else "red"
        log.write(f"[bold {color}]{message}[/bold {color}]\n")
        self.query_one("#train-status", Static).update(message)
