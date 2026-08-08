"""Harness plugin contract tests."""

from everyharness.harnesses.computer import ComputerHarness
from everyharness.harnesses.embeddings import EmbeddingsHarness
from everyharness.harnesses.generic import GenericHarness
from everyharness.harnesses.llm import LLMHarness
from everyharness.harnesses.tabular import TabularHarness
from everyharness.plugin.protocols import ModelRef
from everyharness.testing import assert_harness_plugin


def test_builtin_harness_contracts():
    for harness in (
        GenericHarness(),
        TabularHarness(),
        EmbeddingsHarness(),
        LLMHarness(),
        ComputerHarness(),
    ):
        assert_harness_plugin(harness)


def test_embeddings_hash_fallback():
    model = ModelRef(id="e1", uri="embeddings:demo", kind="embeddings")
    from everyharness.harnesses.embeddings import _embed_texts

    vecs = _embed_texts(model, ["hello", "world"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 32


def test_computer_dry_run_default():
    harness = ComputerHarness()
    model = ModelRef(id="c1", uri="computer:agent", kind="computer")
    code = harness.run_cli(model, ["plan", '{"type":"click","x":1,"y":2}'])
    assert code == 0


def test_computer_dry_run_alias(capsys):
    harness = ComputerHarness()
    model = ModelRef(id="c1", uri="computer:agent", kind="computer")
    code = harness.run_cli(model, ["dry-run", '{"type":"echo","message":"hi"}'])
    assert code == 0
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert "not executed" in out
