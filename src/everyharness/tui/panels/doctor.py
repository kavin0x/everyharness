"""Doctor diagnostics panel."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Button, Static

from everyharness.doctor import run_doctor
from everyharness.plugin.host import PluginHost
from everyharness.tui.panels.base import PanelBody, PanelHeader
from everyharness.tui.state import AppState


class DoctorPanel(Vertical):
    """Install health and plugin diagnostics."""

    DEFAULT_CSS = """
    DoctorPanel {
        height: 1fr;
    }

    DoctorPanel #doctor-body {
        padding: 1 2;
        height: 1fr;
    }

    DoctorPanel #doctor-output {
        height: 1fr;
        border: solid $primary-darken-2;
        padding: 1;
        background: $surface;
    }

    DoctorPanel #doctor-actions {
        height: auto;
        padding: 0 2 1 2;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state

    def compose(self) -> ComposeResult:
        yield PanelHeader("Doctor")
        with PanelBody(id="doctor-body"):
            yield Static("", id="doctor-output")
            yield Button("Re-run doctor", variant="primary", id="doctor-rerun-btn")

    def on_mount(self) -> None:
        self.refresh_report()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "doctor-rerun-btn":
            self.state.host = PluginHost.discover()
            self.refresh_report()

    def refresh_report(self) -> None:
        report = run_doctor()
        lines = [
            f"[bold]everyharness[/bold] {report.version} (plugin API {report.plugin_api_version})",
            f"Offline: {'yes' if report.offline else 'no'}",
            f"Config:  {report.config_dir}",
            f"Cache:   {report.cache_dir} ({report.cache_bytes} bytes)",
            f"Data:    {report.data_dir}",
            f"Plugins: {report.plugins_ok} loaded, {report.plugins_broken} broken",
            "",
        ]
        for warning in report.warnings:
            lines.append(f"[yellow]warning[/yellow]: {warning}")
        for error in report.errors:
            lines.append(f"[red]error[/red]: {error}")
        if not report.warnings and not report.errors:
            lines.append("[green]No issues detected.[/green]")
        self.query_one("#doctor-output", Static).update("\n".join(lines))
