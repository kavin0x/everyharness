"""Model detail panel."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from everyharness.tui.panels.base import EmptyState, PanelBody, PanelHeader
from everyharness.tui.state import AppState


class ModelDetailPanel(Vertical):
    """Show metadata and harness match for a selected model."""

    DEFAULT_CSS = """
    ModelDetailPanel {
        height: 1fr;
    }

    ModelDetailPanel #detail-body {
        padding: 1 2;
        height: 1fr;
    }

    ModelDetailPanel .detail-label {
        color: $text-muted;
        padding-top: 1;
    }

    ModelDetailPanel .detail-value {
        padding-left: 1;
    }
    """

    def __init__(self, state: AppState, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.state = state

    def compose(self) -> ComposeResult:
        yield PanelHeader("Model Detail")
        with PanelBody(id="detail-body"):
            yield EmptyState("Select a model from Library to view details.", id="detail-empty")
            yield Static("", id="detail-content")

    def refresh_detail(self) -> None:
        empty = self.query_one("#detail-empty", EmptyState)
        content = self.query_one("#detail-content", Static)
        record = self.state.selected_record()
        if record is None:
            empty.display = True
            content.update("")
            return
        empty.display = False
        model = record.to_model_ref()
        harness = self.state.find_harness(model)
        harness_name = harness.name if harness else "none"
        try:
            harness_score = harness.matches(model) if harness else 0.0
        except Exception:
            harness_score = 0.0
            harness_name = f"{harness_name} (error)"

        meta_lines = []
        if record.metadata:
            for key, value in sorted(record.metadata.items()):
                meta_lines.append(f"  {key}: {value}")

        lines = [
            f"[bold]ID[/bold]       {record.id}",
            f"[bold]Ref[/bold]      {record.ref}",
            f"[bold]Kind[/bold]     {record.kind or '—'}",
            f"[bold]Created[/bold]  {record.created_at}",
            f"[bold]Updated[/bold]  {record.updated_at}",
            "",
            f"[bold]Harness[/bold]  {harness_name} (score {harness_score:.2f})",
        ]
        if meta_lines:
            lines.append("")
            lines.append("[bold]Metadata[/bold]")
            lines.extend(meta_lines)

        if harness is None:
            lines.append("")
            lines.append(
                "[yellow]No harness matched. Install a plugin or use generic harness.[/yellow]"
            )
        elif harness_name == "generic":
            lines.append("")
            lines.append("[dim]Generic harness is a stub — run output may be limited.[/dim]")

        content.update("\n".join(lines))
