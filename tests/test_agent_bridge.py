"""Tests for coding-agent bridge."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from everyharness.agents.bridge import materialize_ui_pack, prepare_ui_bridge, ui_dest_for_model
from everyharness.agents.detect import AGENT_IDS, detect_agent, detect_all
from everyharness.plugin.protocols import ModelRef


def _model() -> ModelRef:
    return ModelRef(id="abc12345", uri="./model.pkl", kind="tabular", metadata={"source": "test"})


def test_materialize_ui_pack_writes_expected_files(tmp_path: Path):
    model = _model()
    dest = materialize_ui_pack(model, "cursor", root=tmp_path)

    assert dest == tmp_path / model.id
    assert (dest / "AGENT_PROMPT.md").is_file()
    assert (dest / "model-card.json").is_file()
    assert (dest / "manifest.json").is_file()
    assert (dest / "README.md").is_file()

    card = json.loads((dest / "model-card.json").read_text(encoding="utf-8"))
    assert card["id"] == model.id
    assert card["uri"] == model.uri

    prompt = (dest / "AGENT_PROMPT.md").read_text(encoding="utf-8")
    assert model.id in prompt
    assert model.uri in prompt
    assert "only wrote these prompt/metadata files" in prompt

    readme = (dest / "README.md").read_text(encoding="utf-8")
    assert "prompt pack" in readme.lower()


def test_ui_dest_for_model_default_name():
    path = ui_dest_for_model("xyz", root=Path("/tmp/root"))
    assert path == Path("/tmp/root/xyz")


def test_detect_all_covers_agents():
    statuses = detect_all()
    assert len(statuses) == len(AGENT_IDS)
    assert {s.agent for s in statuses} == set(AGENT_IDS)


def test_detect_agent_unknown_raises():
    with pytest.raises(ValueError, match="Unknown agent"):
        detect_agent("unknown-agent")


def test_prepare_ui_bridge_returns_status(tmp_path: Path):
    model = _model()
    dest, status = prepare_ui_bridge(model, "claude", root=tmp_path)
    assert dest.is_dir()
    assert status.agent == "claude"
    assert isinstance(status.available, bool)
