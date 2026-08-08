"""Tests for kind detection."""

from everyharness.core.detect import BuiltinDetector, detect_kind, kind_from_uri
from everyharness.plugin.protocols import ModelRef


def test_kind_from_uri_extensions():
    assert kind_from_uri("./model.pkl") == "tabular"
    assert kind_from_uri("weights.gguf") == "llm"
    assert kind_from_uri("ollama:mistral") == "llm"
    assert kind_from_uri("hf:org/model") == "llm"
    assert kind_from_uri("callable:pkg.mod:fn") == "generic"


def test_builtin_detector_scores_kind():
    det = BuiltinDetector()
    model = ModelRef(id="1", uri="./a.pkl", kind="tabular")
    assert det.score(model) >= 0.9


def test_detect_kind_prefers_explicit_kind():
    model = ModelRef(id="1", uri="./x.bin", kind="llm")
    assert detect_kind(model, [BuiltinDetector()]) == "llm"
