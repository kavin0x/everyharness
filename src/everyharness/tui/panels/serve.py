"""Serve status panel."""

from __future__ import annotations

import threading
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, RichLog, Static

from everyharness.tui.panels.base import EmptyState, PanelBody, PanelHeader
from everyharness.tui.state import AppState


class ServeStatusPanel(Vertical):
    """Start/stop model server and show status."""

    DEFAULT_CSS = """
    ServeStatusPanel {
        height: 1fr;
    }

    ServeStatusPanel .serve-field {
        height: auto;
        padding: 0 2;
    }

    ServeStatusPanel .serve-label {
        width: 10;
        color: $text-muted;
    }

    ServeStatusPanel RichLog {
        height: 1fr;
        margin: 1 2;
        border: solid $primary-darken-2;
    }

    ServeStatusPanel #serve-actions {
        height: auto;
        padding: 0 2 1 2;
    }

    ServeStatusPanel #serve-badge {
        height: auto;
        padding: 0 2;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state
        self._serve_thread: threading.Thread | None = None

    def compose(self) -> ComposeResult:
        yield PanelHeader("Serve Status")
        with PanelBody():
            yield EmptyState("Select a model in Library to serve.", id="serve-empty")
            yield Static("", id="serve-badge")
            with Horizontal(classes="serve-field"):
                yield Static("Host", classes="serve-label")
                yield Input(value="127.0.0.1", id="serve-host")
            with Horizontal(classes="serve-field"):
                yield Static("Port", classes="serve-label")
                yield Input(value="8000", id="serve-port")
            with Horizontal(id="serve-actions"):
                yield Button("Start serve", variant="primary", id="serve-start-btn")
                yield Button("Stop", variant="error", id="serve-stop-btn", disabled=True)
            yield RichLog(id="serve-log", highlight=True, markup=True)
            yield Static("", id="serve-status")

    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        empty = self.query_one("#serve-empty", EmptyState)
        badge = self.query_one("#serve-badge", Static)
        record = self.state.selected_record()
        empty.display = record is None
        if self.state.serve_running:
            badge.update(
                f"[bold green]● RUNNING[/bold green] "
                f"{self.state.serve_host}:{self.state.serve_port} "
                f"model={self.state.serve_model_id or '—'}"
            )
        else:
            badge.update("[dim]○ Not serving[/dim]")
        status = self.query_one("#serve-status", Static)
        if record is None:
            status.update("No model selected.")
        elif self.state.serve_running:
            status.update(
                f"OpenAI-compatible endpoint (when harness supports it): "
                f"http://{self.state.serve_host}:{self.state.serve_port}"
            )
        else:
            harness = self.state.harness_for_selected()
            name = harness.name if harness else "none"
            status.update(f"Model {record.id} → harness {name}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "serve-start-btn":
            self._start_serve()
        elif event.button.id == "serve-stop-btn":
            self._stop_serve()

    def _start_serve(self) -> None:
        if self.state.serve_running:
            self.app.notify("Server already running.", severity="warning")
            return
        model = self.state.selected_model_ref()
        if model is None:
            self.app.notify("Select a model first.", severity="warning")
            return
        harness = self.state.harness_for_selected()
        if harness is None:
            self.app.notify("No harness for this model.", severity="error")
            return
        host = self.query_one("#serve-host", Input).value.strip() or "127.0.0.1"
        try:
            port = int(self.query_one("#serve-port", Input).value.strip() or "8000")
        except ValueError:
            self.app.notify("Invalid port.", severity="error")
            return

        log = self.query_one("#serve-log", RichLog)
        log.write(f"[bold]everyharness serve {model.id}[/bold] --host {host} --port {port}\n")

        self.state.serve_host = host
        self.state.serve_port = port
        self.state.serve_model_id = model.id

        def worker() -> None:
            try:
                harness.serve(model, host, port)
            except NotImplementedError as exc:
                self.app.call_from_thread(self._serve_failed, str(exc))
            except Exception as exc:
                self.app.call_from_thread(self._serve_failed, str(exc))
            finally:
                self.app.call_from_thread(self._serve_stopped)

        self.state.serve_running = True
        self.query_one("#serve-start-btn", Button).disabled = True
        self.query_one("#serve-stop-btn", Button).disabled = False
        self._serve_thread = threading.Thread(target=worker, daemon=True)
        self._serve_thread.start()
        self.refresh_status()
        self.app.notify(f"Serving on {host}:{port}", severity="information")

    def _serve_failed(self, message: str) -> None:
        log = self.query_one("#serve-log", RichLog)
        log.write(f"[red]Serve failed: {message}[/red]\n")
        self.app.notify(message, severity="error")

    def _serve_stopped(self) -> None:
        self.state.serve_running = False
        self.state.serve_model_id = None
        self.query_one("#serve-start-btn", Button).disabled = False
        self.query_one("#serve-stop-btn", Button).disabled = True
        self.refresh_status()

    def _stop_serve(self) -> None:
        if not self.state.serve_running:
            return
        log = self.query_one("#serve-log", RichLog)
        log.write(
            "[yellow]Stop requested — harness serve() may block until process ends.[/yellow]\n"
        )
        self.state.serve_running = False
        self.state.serve_model_id = None
        self.query_one("#serve-start-btn", Button).disabled = False
        self.query_one("#serve-stop-btn", Button).disabled = True
        self.refresh_status()
        self.app.notify("Serve marked stopped (thread may still be running).", severity="warning")
