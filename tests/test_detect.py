"""Tests for kind detection."""

from everyharness.core.detect import BuiltinDetector, detect_kind, kind_from_uri
from everyharness.harnesses.speech import SpeechHarness
from everyharness.harnesses.vision import VisionHarness
from everyharness.plugin.protocols import ModelRef


def test_kind_from_uri_extensions():
    assert kind_from_uri("./model.pkl") == "tabular"
    assert kind_from_uri("weights.gguf") == "llm"
    assert kind_from_uri("ollama:mistral") == "llm"
    assert kind_from_uri("hf:org/model") == "llm"
    assert kind_from_uri("callable:pkg.mod:fn") == "generic"
    assert kind_from_uri("model.onnx") == "vision"


def test_kind_from_uri_ignores_input_media():
    assert kind_from_uri("./photo.png") is None
    assert kind_from_uri("./clip.wav") is None
    assert kind_from_uri("./song.mp3") is None


def test_builtin_detector_scores_kind():
    det = BuiltinDetector()
    model = ModelRef(id="1", uri="./a.pkl", kind="tabular")
    assert det.score(model) >= 0.9


def test_detect_kind_prefers_explicit_kind():
    model = ModelRef(id="1", uri="./x.bin", kind="llm")
    assert detect_kind(model, [BuiltinDetector()]) == "llm"


def test_vision_matches_weights_not_images():
    harness = VisionHarness()
    assert harness.matches(ModelRef(id="1", uri="./model.onnx", kind=None)) >= 0.7
    assert harness.matches(ModelRef(id="2", uri="./photo.png", kind=None)) == 0.0
    assert harness.matches(ModelRef(id="3", uri="./photo.png", kind="vision")) >= 0.9


def test_speech_matches_whisper_not_audio_files():
    harness = SpeechHarness()
    assert harness.matches(ModelRef(id="1", uri="./clip.wav", kind=None)) == 0.0
    assert harness.matches(ModelRef(id="2", uri="hf:openai/whisper-tiny", kind=None)) >= 0.9
    assert harness.matches(ModelRef(id="3", uri="speech:base", kind="speech")) >= 0.9
