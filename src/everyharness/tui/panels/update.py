"""Update check panel."""

from __future__ import annotations

import threading
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from everyharness.core.config import is_offline
from everyharness.core.errors import OfflineError
from everyharness.core.update import check_for_update, current_version
from everyharness.tui.panels.base import PanelBody, PanelHeader
from everyharness.tui.state import AppState


class UpdatePanel(Vertical):
    """Check for PyPI updates."""

    DEFAULT_CSS = """
    UpdatePanel {
        height: 1fr;
    }

    UpdatePanel #update-body {
        padding: 1 2;
        height: 1fr;
    }

    UpdatePanel #update-result {
        padding-top: 1;
    }

    UpdatePanel #update-actions {
        height: auto;
        padding: 1 2;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state

    def compose(self) -> ComposeResult:
        yield PanelHeader("Update")
        with PanelBody(id="update-body"):
            yield Static("", id="update-info")
            yield Static("", id="update-result")
            with Horizontal(id="update-actions"):
                yield Button("Check for updates", variant="primary", id="update-check-btn")

    def on_mount(self) -> None:
        self._show_baseline()

    def _show_baseline(self) -> None:
        info = self.query_one("#update-info", Static)
        offline = is_offline()
        info.update(
            f"Installed: [bold cyan]everyharness {current_version()}[/bold cyan]\n"
            f"Offline mode: {'yes' if offline else 'no'}\n"
            f"Upgrade path: [dim]pip install -U everyharness[/dim]"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "update-check-btn":
            return
        result = self.query_one("#update-result", Static)
        result.update("[dim]Checking PyPI…[/dim]")
        self.query_one("#update-check-btn", Button).disabled = True

        def worker() -> None:
            try:
                latest = check_for_update()
            except OfflineError as exc:
                self.app.call_from_thread(self._show_result, f"[yellow]{exc}[/yellow]")
                return
            except Exception as exc:
                self.app.call_from_thread(self._show_result, f"[red]Check failed: {exc}[/red]")
                return
            if latest is None:
                msg = (
                    "[green]You are up to date[/green] (or PyPI check not available yet).\n"
                    f"Current: {current_version()}"
                )
            else:
                msg = (
                    f"[yellow]Update available:[/yellow] {latest}\n"
                    f"Current: {current_version()}\n"
                    "Run: pip install -U everyharness"
                )
            self.app.call_from_thread(self._show_result, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _show_result(self, message: str) -> None:
        self.query_one("#update-result", Static).update(message)
        self.query_one("#update-check-btn", Button).disabled = False
