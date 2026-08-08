"""Navigation sidebar."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ListItem, ListView, Static

NAV_ITEMS: tuple[tuple[str, str], ...] = (
    ("library", "Library"),
    ("model_detail", "Model Detail"),
    ("run_console", "Run Console"),
    ("plugins", "Plugins / Templates"),
    ("train", "Train Wizard"),
    ("serve", "Serve Status"),
    ("update", "Update"),
    ("doctor", "Doctor"),
)


class Sidebar(Vertical):
    """Left navigation rail."""

    DEFAULT_CSS = """
    Sidebar {
        width: 22;
        min-width: 22;
        background: $surface-darken-1;
        border-right: solid $primary-darken-2;
    }

    Sidebar #nav-title {
        padding: 1 1 0 1;
        text-style: bold;
        color: $accent;
    }

    Sidebar ListView {
        height: 1fr;
        background: transparent;
    }

    Sidebar ListItem {
        padding: 0 1;
    }

    Sidebar ListItem.-highlight {
        background: $primary 30%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("everyharness", id="nav-title")
        with ListView(id="nav-list"):
            for panel_id, label in NAV_ITEMS:
                yield ListItem(Static(label), id=f"nav-{panel_id}")

    def on_mount(self) -> None:
        self.query_one("#nav-list", ListView).index = 0
