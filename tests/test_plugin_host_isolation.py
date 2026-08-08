"""Plugin host must isolate broken plugins."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from everyharness.cli import app
from everyharness.plugin.host import PluginHost, PluginLoadResult


def test_broken_entry_point_does_not_raise():
    with patch.object(PluginHost, "_load_group", return_value=[]):
        host = PluginHost.discover()
    assert host.harnesses == []


def test_load_entrypoint_import_error():
    host = PluginHost()
    result = host._load_entrypoint("harness", "broken", "no_such_module:Thing", object)
    assert result.error is not None
    assert result.plugin is None


def test_load_entrypoint_missing_api_version():
    class BadPlugin:
        name = "bad"

        def describe(self):
            pass

    host = PluginHost()

    with patch.object(host, "_resolve_target", return_value=BadPlugin):
        result = host._load_entrypoint("harness", "bad", "fake:BadPlugin", object)
    assert result.error is not None
    assert "api_version" in result.error


def test_incompatible_api_skipped_with_warning():
    from everyharness.plugin.protocols import PluginInfo

    class OldPlugin:
        name = "old"
        api_version = "99.0.0"

        def describe(self) -> PluginInfo:
            return PluginInfo(
                name="old",
                version="0.0.1",
                api_version="99.0.0",
                kind="harness",
                requires_api=">=99,<100",
            )

        def matches(self, model):
            return 0.0

        def run_cli(self, model, argv):
            return 0

        def serve(self, model, host, port):
            pass

        def finetune(self, model, dataset, opts):
            return model

        def templates(self):
            return []

    from everyharness.plugin.protocols import HarnessPlugin

    host = PluginHost()
    with patch.object(host, "_resolve_target", return_value=OldPlugin):
        result = host._load_entrypoint("harness", "old", "fake:OldPlugin", HarnessPlugin)
    assert result.plugin is None
    assert result.warning is not None


def test_cli_survives_broken_plugins():
    """Broken plugins must not prevent everyharness doctor from running."""
    runner = CliRunner()
    with patch.object(PluginHost, "discover") as discover:
        host = PluginHost()
        host.load_results = [
            PluginLoadResult(name="broken", group="harness", error="import failed"),
        ]
        host.harnesses = []
        host.loaders = []
        host.detectors = []
        host.templates = []
        discover.return_value = host
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "broken" in result.stdout.lower() or "error" in result.stdout.lower()


def test_plugin_list_runs():
    runner = CliRunner()
    result = runner.invoke(app, ["plugin", "list"])
    assert result.exit_code == 0
    assert "generic" in result.stdout or "local" in result.stdout
