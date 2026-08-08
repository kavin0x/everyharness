"""Smoke tests for the Textual TUI."""

from __future__ import annotations

import pytest

from everyharness.tui.app import PANEL_IDS, EveryharnessApp
from everyharness.tui.state import AppState


def test_app_state_find_harness(tmp_path, monkeypatch):
    from everyharness.plugin.host import PluginHost

    reg_path = tmp_path / "registry.json"
    monkeypatch.setattr("everyharness.core.registry.registry_path", lambda: reg_path)

    host = PluginHost.discover()
    state = AppState(host=host)
    rec = state.registry().add("./test-model.bin", kind="generic")
    state.selected_model_id = rec.id
    harness = state.harness_for_selected()
    assert harness is not None
    assert harness.name == "generic"


@pytest.mark.anyio(backend="asyncio")
async def test_tui_app_mounts():
    app = EveryharnessApp()
    async with app.run_test() as pilot:
        assert pilot.app is not None
        switcher = app.query_one("#content-switcher")
        assert switcher.current == "library"


@pytest.mark.anyio(backend="asyncio")
async def test_tui_navigate_panels():
    app = EveryharnessApp()
    async with app.run_test() as pilot:
        for panel_id in PANEL_IDS:
            app.action_show_panel(panel_id)
            await pilot.pause()
            switcher = app.query_one("#content-switcher")
            assert switcher.current == panel_id


@pytest.mark.anyio(backend="asyncio")
async def test_tui_doctor_panel():
    app = EveryharnessApp()
    async with app.run_test() as pilot:
        app.action_show_panel("doctor")
        await pilot.pause()
        output = app.query_one("#doctor-output")
        assert "everyharness" in str(output.render())
