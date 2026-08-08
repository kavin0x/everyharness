"""CLI integration for run/serve/train."""


import pytest
from typer.testing import CliRunner

from everyharness.cli import app
from everyharness.core.registry import ModelRegistry


@pytest.fixture
def runner():
    return CliRunner()


def test_run_generic_info(runner, tmp_path, monkeypatch):
    reg_path = tmp_path / "registry.json"
    monkeypatch.setattr("everyharness.core.registry.registry_path", lambda: reg_path)
    reg = ModelRegistry(reg_path)
    rec = reg.add("callable:json:loads", kind="generic")
    result = runner.invoke(app, ["run", rec.id, "info"])
    assert result.exit_code == 0
    assert rec.id in result.stdout or "callable" in result.stdout


def test_add_detects_kind(runner, tmp_path, monkeypatch):
    reg_path = tmp_path / "registry.json"
    monkeypatch.setattr("everyharness.core.registry.registry_path", lambda: reg_path)
    model = tmp_path / "model.pkl"
    model.write_bytes(b"")
    result = runner.invoke(app, ["add", str(model), "--trust-pickle"])
    assert result.exit_code == 0
    assert "tabular" in result.stdout
