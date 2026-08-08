"""Tests for model registry."""

from everyharness.core.registry import ModelRegistry


def test_registry_add_list_remove(tmp_path):
    path = tmp_path / "registry.json"
    reg = ModelRegistry(path)
    rec = reg.add("./model.pkl", kind="tabular")
    assert reg.get(rec.id) is not None
    listed = reg.list()
    assert len(listed) == 1
    assert reg.remove(rec.id) is True
    assert reg.get(rec.id) is None


def test_registry_update(tmp_path):
    path = tmp_path / "registry.json"
    reg = ModelRegistry(path)
    rec = reg.add("./model.bin")
    updated = reg.update(rec.id, kind="generic")
    assert updated.kind == "generic"
