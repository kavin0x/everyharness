"""Tests for model loaders."""

from pathlib import Path

from everyharness.loaders.callable_loader import CallableLoader
from everyharness.loaders.hf import HuggingFaceLoader
from everyharness.loaders.local import LocalLoader
from everyharness.loaders.ollama import OllamaLoader


def test_local_loader_can_load_file(tmp_path):
    f = tmp_path / "model.pkl"
    f.write_bytes(b"stub")
    loader = LocalLoader()
    assert loader.can_load(str(f)) > 0
    ref = loader.load(str(f))
    assert ref.uri == str(f.resolve())
    assert ref.kind == "tabular"


def test_hf_loader_parses_uri(monkeypatch, tmp_path):
    loader = HuggingFaceLoader()
    assert loader.can_load("hf:org/model") > 0

    cache = tmp_path / "hf-cache"
    cache.mkdir(parents=True, exist_ok=True)

    def _fake_snapshot_download(*, repo_id: str, local_dir: str, **_kwargs: object) -> str:
        path = Path(local_dir)
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    monkeypatch.setattr(
        "huggingface_hub.snapshot_download",
        _fake_snapshot_download,
        raising=False,
    )
    monkeypatch.setattr(
        "everyharness.loaders.hf.cache_dir_for",
        lambda *_a, **_k: cache,
    )
    ref = loader.load("hf:org/model")
    assert ref.metadata["repo_id"] == "org/model"


def test_ollama_loader_parses_uri():
    loader = OllamaLoader()
    assert loader.can_load("ollama:llama3") > 0
    ref = loader.load("ollama:llama3")
    assert ref.kind == "llm"
    assert ref.metadata["model"] == "llama3"


def test_callable_loader_parses_uri():
    loader = CallableLoader()
    uri = "callable:json:loads"
    assert loader.can_load(uri) > 0
    ref = loader.load(uri)
    assert ref.metadata["module"] == "json"
    assert ref.metadata["attr"] == "loads"
