"""Tests for model resolution helpers."""

from pathlib import Path

import pytest

from everyharness.core.errors import RegistryError
from everyharness.core.resolve import load_model_ref, pick_harness, require_pickle_trust
from everyharness.harnesses.generic import GenericHarness
from everyharness.harnesses.llm import LLMHarness
from everyharness.loaders.local import LocalLoader
from everyharness.plugin.protocols import ModelRef


def test_require_pickle_trust():
    with pytest.raises(RegistryError):
        require_pickle_trust("model.pkl", False)
    require_pickle_trust("model.pkl", True)


def test_pick_harness_respects_explicit_kind():
    model = ModelRef(id="1", uri="./x.bin", kind="generic")
    harness = pick_harness(model, [LLMHarness(), GenericHarness()])
    assert harness.name == "generic"


def test_load_model_ref_rejects_missing_local_path():
    with pytest.raises(RegistryError, match="not found"):
        load_model_ref("./does-not-exist.pkl", [LocalLoader()])


def test_load_model_ref_allows_scheme_uris_without_loader():
    ref = load_model_ref("embeddings:demo", [], kind="embeddings")
    assert ref.kind == "embeddings"
    assert ref.uri == "embeddings:demo"


def test_load_model_ref_resolves_existing_file(tmp_path: Path):
    model = tmp_path / "model.pkl"
    model.write_bytes(b"stub")
    ref = load_model_ref(str(model), [LocalLoader()])
    assert ref.uri == str(model.resolve())
    assert "cached_path" in ref.metadata
