"""Main Textual application."""

from __future__ import annotations

import contextlib

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import ContentSwitcher, Footer, Header, ListView

from everyharness.plugin.host import PluginHost
from everyharness.tui.panels import (
    DoctorPanel,
    LibraryPanel,
    ModelDetailPanel,
    PluginsPanel,
    RunConsolePanel,
    ServeStatusPanel,
    TrainWizardPanel,
    UpdatePanel,
)
from everyharness.tui.state import AppState
from everyharness.tui.widgets.sidebar import NAV_ITEMS, Sidebar

PANEL_IDS = [panel_id for panel_id, _ in NAV_ITEMS]


class EveryharnessApp(App[None]):
    """everyharness Textual TUI."""

    TITLE = "everyharness"
    SUB_TITLE = "offline-first model harness"

    CSS = """
    Screen {
        background: $background;
    }

    #main-layout {
        height: 1fr;
    }

    #content-switcher {
        width: 1fr;
        height: 1fr;
    }

  Header {
        background: $primary-darken-2;
    }

    Footer {
        background: $surface-darken-1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("l", "show_panel('library')", "Library", show=True),
        Binding("r", "show_panel('run_console')", "Run", show=True),
        Binding("p", "show_panel('plugins')", "Plugins", show=True),
        Binding("d", "show_panel('doctor')", "Doctor", show=True),
        Binding("slash", "focus_search", "Search", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.state = AppState(host=PluginHost.discover())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-layout"):
            yield Sidebar()
            with ContentSwitcher(initial="library", id="content-switcher"):
                yield LibraryPanel(self.state, id="library")
                yield ModelDetailPanel(self.state, id="model_detail")
                yield RunConsolePanel(self.state, id="run_console")
                yield PluginsPanel(self.state, id="plugins")
                yield TrainWizardPanel(self.state, id="train")
                yield ServeStatusPanel(self.state, id="serve")
                yield UpdatePanel(self.state, id="update")
                yield DoctorPanel(self.state, id="doctor")
        yield Footer()

    def on_mount(self) -> None:
        self._sync_nav_index("library")

    def action_show_panel(self, panel_id: str) -> None:
        if panel_id not in PANEL_IDS:
            return
        switcher = self.query_one("#content-switcher", ContentSwitcher)
        switcher.current = panel_id
        self._sync_nav_index(panel_id)
        self._refresh_panel(panel_id)

    def action_focus_search(self) -> None:
        self.action_show_panel("plugins")
        with contextlib.suppress(Exception):
            self.query_one("#catalog-search").focus()

    def _sync_nav_index(self, panel_id: str) -> None:
        index = PANEL_IDS.index(panel_id)
        nav = self.query_one("#nav-list", ListView)
        nav.index = index

    def _refresh_panel(self, panel_id: str) -> None:
        panel = self.query_one(f"#{panel_id}")
        refresh = getattr(panel, "refresh_models", None)
        if callable(refresh):
            refresh()
        refresh_detail = getattr(panel, "refresh_detail", None)
        if callable(refresh_detail):
            refresh_detail()
        refresh_context = getattr(panel, "refresh_context", None)
        if callable(refresh_context):
            refresh_context()
        refresh_status = getattr(panel, "refresh_status", None)
        if callable(refresh_status):
            refresh_status()
        refresh_report = getattr(panel, "refresh_report", None)
        if callable(refresh_report):
            refresh_report()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id and event.item.id.startswith("nav-"):
            panel_id = event.item.id.removeprefix("nav-")
            self.action_show_panel(panel_id)

    def on_library_panel_model_selected(self, event: LibraryPanel.ModelSelected) -> None:
        self.state.selected_model_id = event.model_id
        self.action_show_panel("model_detail")
