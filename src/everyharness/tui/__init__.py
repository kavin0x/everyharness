"""Textual TUI for everyharness."""

from __future__ import annotations

from everyharness.tui.app import EveryharnessApp


def launch_tui() -> None:
    """Launch the everyharness Textual TUI."""
    EveryharnessApp().run()
