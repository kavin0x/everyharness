"""Curated plugin catalog (local index for discovery)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogEntry:
    name: str
    pypi_name: str
    kind: str
    summary: str
    tags: tuple[str, ...] = ()


# Curated seed catalog; online index is a later-phase extension point.
# Built-ins ship in the everyharness package; community plugins use everyharness-*.
CATALOG: tuple[CatalogEntry, ...] = (
    CatalogEntry(
        name="generic",
        pypi_name="everyharness",
        kind="harness",
        summary="Fallback harness for unknown model types and Python callables.",
        tags=("builtin", "generic", "callable"),
    ),
    CatalogEntry(
        name="tabular",
        pypi_name="everyharness",
        kind="harness",
        summary="Tabular predict/evaluate/explain for sklearn/joblib models.",
        tags=("builtin", "tabular", "sklearn"),
    ),
    CatalogEntry(
        name="embeddings",
        pypi_name="everyharness",
        kind="harness",
        summary="Text embeddings: embed, similarity, and local index search.",
        tags=("builtin", "embeddings", "similarity"),
    ),
    CatalogEntry(
        name="llm",
        pypi_name="everyharness",
        kind="harness",
        summary="LLM REPL and OpenAI-compatible /v1 server (Ollama, GGUF, HF).",
        tags=("builtin", "llm", "ollama", "gguf"),
    ),
    CatalogEntry(
        name="vision",
        pypi_name="everyharness",
        kind="harness",
        summary="Vision classify/detect harness (ONNX + HF pipelines).",
        tags=("builtin", "vision", "onnx"),
    ),
    CatalogEntry(
        name="speech",
        pypi_name="everyharness",
        kind="harness",
        summary="Speech transcribe via whisper; speak is stubbed in v1.",
        tags=("builtin", "speech", "whisper"),
    ),
    CatalogEntry(
        name="diffusion",
        pypi_name="everyharness",
        kind="harness",
        summary="Text-to-image diffusion generate (diffusers extra).",
        tags=("builtin", "diffusion", "image"),
    ),
    CatalogEntry(
        name="computer",
        pypi_name="everyharness",
        kind="harness",
        summary="Computer-use harness with dry-run default and --allow-control opt-in.",
        tags=("builtin", "computer", "agent"),
    ),
    CatalogEntry(
        name="local",
        pypi_name="everyharness",
        kind="loader",
        summary="Load models from local filesystem paths and directories.",
        tags=("builtin", "loader", "local"),
    ),
    CatalogEntry(
        name="huggingface",
        pypi_name="everyharness",
        kind="loader",
        summary="Load models from Hugging Face Hub (hf:org/model) with offline cache.",
        tags=("builtin", "loader", "huggingface", "hf"),
    ),
    CatalogEntry(
        name="ollama",
        pypi_name="everyharness",
        kind="loader",
        summary="Reference Ollama models (ollama:model) via local daemon.",
        tags=("builtin", "loader", "ollama"),
    ),
    CatalogEntry(
        name="callable",
        pypi_name="everyharness",
        kind="loader",
        summary="Load Python callables via callable:module.path:attr.",
        tags=("builtin", "loader", "callable", "python"),
    ),
    CatalogEntry(
        name="cli-stub",
        pypi_name="everyharness",
        kind="templates",
        summary="Minimal CLI stub scaffold around a model.",
        tags=("builtin", "templates", "cli"),
    ),
    CatalogEntry(
        name="sample-harness",
        pypi_name="everyharness-sample",
        kind="harness",
        summary="Example harness plugin for documentation.",
        tags=("example", "docs", "community"),
    ),
)


def search_catalog(query: str) -> list[CatalogEntry]:
    q = query.strip().lower()
    if not q:
        return list(CATALOG)
    results: list[CatalogEntry] = []
    for entry in CATALOG:
        haystack = " ".join([entry.name, entry.pypi_name, entry.summary, *entry.tags]).lower()
        if q in haystack:
            results.append(entry)
    return results


def get_catalog_entry(name: str) -> CatalogEntry | None:
    key = name.strip().lower()
    for entry in CATALOG:
        if entry.name.lower() == key or entry.pypi_name.lower() == key:
            return entry
    return None
