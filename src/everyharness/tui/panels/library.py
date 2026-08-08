"""Model library panel."""

from __future__ import annotations

import contextlib
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Input

from everyharness.tui.panels.base import EmptyState, PanelBody, PanelHeader
from everyharness.tui.state import AppState


class LibraryPanel(Vertical):
    """Browse and add registered models."""

    DEFAULT_CSS = """
    LibraryPanel {
        height: 1fr;
    }

    LibraryPanel #add-row {
        height: auto;
        padding: 0 2 1 2;
    }

    LibraryPanel #add-row Input {
        width: 1fr;
    }

    LibraryPanel DataTable {
        height: 1fr;
        margin: 0 2;
    }

    LibraryPanel #library-actions {
        height: auto;
        padding: 1 2;
    }
    """

    class ModelSelected(Message):
        """Emitted when a model row is activated."""

        def __init__(self, model_id: str) -> None:
            self.model_id = model_id
            super().__init__()

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state

    def compose(self) -> ComposeResult:
        yield PanelHeader("Library — registered models")
        with PanelBody():
            with Horizontal(id="add-row"):
                yield Input(placeholder="Path or model ref (e.g. ./model.pkl)", id="add-ref")
                yield Button("Add", variant="primary", id="add-btn")
            yield DataTable(id="model-table", zebra_stripes=True, cursor_type="row")
            with Horizontal(id="library-actions"):
                yield Button("Open detail", id="open-detail-btn")
                yield Button("Remove", variant="error", id="remove-btn")
            yield EmptyState(
                "No models yet. Add a path or URI above, or run: everyharness add <ref>",
                id="empty-hint",
            )

    def on_mount(self) -> None:
        table = self.query_one("#model-table", DataTable)
        table.add_columns("ID", "Ref", "Kind", "Created")
        self.refresh_models()

    def refresh_models(self) -> None:
        table = self.query_one("#model-table", DataTable)
        table.clear()
        models = self.state.registry().list()
        empty = self.query_one("#empty-hint", EmptyState)
        empty.display = len(models) == 0
        for rec in models:
            table.add_row(
                rec.id,
                rec.ref,
                rec.kind or "—",
                rec.created_at[:19].replace("T", " "),
                key=rec.id,
            )
        if self.state.selected_model_id:
            with contextlib.suppress(StopIteration):
                table.move_cursor(row=next(
                    i for i, rec in enumerate(models) if rec.id == self.state.selected_model_id
                ))

    def _selected_row_id(self) -> str | None:
        table = self.query_one("#model-table", DataTable)
        if table.row_count == 0:
            return None
        row_key = table.get_row_at(table.cursor_row)
        return str(row_key[0])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-btn":
            ref = self.query_one("#add-ref", Input).value.strip()
            if not ref:
                self.app.notify("Enter a model reference.", severity="warning")
                return
            record = self.state.registry().add(ref)
            self.state.selected_model_id = record.id
            self.query_one("#add-ref", Input).value = ""
            self.refresh_models()
            self.app.notify(f"Added model {record.id}", severity="information")
        elif event.button.id == "open-detail-btn":
            model_id = self._selected_row_id()
            if model_id:
                self.post_message(self.ModelSelected(model_id))
            else:
                self.app.notify("Select a model first.", severity="warning")
        elif event.button.id == "remove-btn":
            model_id = self._selected_row_id()
            if not model_id:
                self.app.notify("Select a model to remove.", severity="warning")
                return
            if self.state.registry().remove(model_id):
                if self.state.selected_model_id == model_id:
                    self.state.selected_model_id = None
                self.refresh_models()
                self.app.notify(f"Removed {model_id}", severity="information")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key is not None:
            model_id = str(event.row_key.value)
            self.state.selected_model_id = model_id
            self.post_message(self.ModelSelected(model_id))
