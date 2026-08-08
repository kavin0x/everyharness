"""Base panel helpers."""

from __future__ import annotations

from textual.containers import Vertical
from textual.widgets import Static


class PanelHeader(Static):
    """Section title with optional subtitle."""

    DEFAULT_CSS = """
    PanelHeader {
        height: auto;
        padding: 1 2 0 2;
        text-style: bold;
        color: $text;
    }
    """


class EmptyState(Static):
    """Friendly empty-state message."""

    DEFAULT_CSS = """
    EmptyState {
        padding: 2 2;
        color: $text-muted;
    }
    """


class PanelBody(Vertical):
    """Standard panel content area."""

    DEFAULT_CSS = """
    PanelBody {
        height: 1fr;
        padding: 0 1 1 1;
    }
    """
