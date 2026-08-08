"""Tests for model resolution helpers."""

import pytest

from everyharness.core.errors import RegistryError
from everyharness.core.resolve import pick_harness, require_pickle_trust
from everyharness.harnesses.generic import GenericHarness
from everyharness.harnesses.llm import LLMHarness
from everyharness.plugin.protocols import ModelRef


def test_require_pickle_trust():
    with pytest.raises(RegistryError):
        require_pickle_trust("model.pkl", False)
    require_pickle_trust("model.pkl", True)


def test_pick_harness_respects_explicit_kind():
    model = ModelRef(id="1", uri="./x.bin", kind="generic")
    harness = pick_harness(model, [LLMHarness(), GenericHarness()])
    assert harness.name == "generic"
