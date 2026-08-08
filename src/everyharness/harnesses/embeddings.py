"""Embeddings harness."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, cast

from everyharness.finetune import finetune_model
from everyharness.harnesses._util import missing_extra, print_json, read_json_input
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


def _hash_embed(text: str, dim: int = 32) -> list[float]:
    """Deterministic fallback embedding when sentence-transformers is unavailable."""
    vec = [0.0] * dim
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % dim] += ch / 255.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _load_embedder(model: ModelRef) -> Any:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    path = model.metadata.get("snapshot_path") or model.metadata.get("repo_id") or model.uri
    if str(path).startswith("embeddings:"):
        path = str(path).split(":", 1)[1]
    try:
        return SentenceTransformer(str(path))
    except Exception:
        return None


def _embed_texts(model: ModelRef, texts: list[str]) -> list[list[float]]:
    embedder = _load_embedder(model)
    if embedder is not None:
        vectors = embedder.encode(texts)
        return vectors.tolist() if hasattr(vectors, "tolist") else [list(v) for v in vectors]
    return [_hash_embed(t) for t in texts]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


class EmbeddingsHarness:
    name = "embeddings"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "embeddings":
            return 0.95
        if model.uri.lower().startswith("embeddings:"):
            return 0.9
        repo = str(model.metadata.get("repo_id", "")).lower()
        if "sentence" in repo or "embedding" in repo or "e5" in repo:
            return 0.85
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: embed | similarity | index [--input FILE]")
            return 1
        cmd = argv[0]
        rest = argv[1:]
        input_path = None
        if "--input" in rest:
            idx = rest.index("--input")
            if idx + 1 < len(rest):
                input_path = rest[idx + 1]
        if cmd == "embed":
            data = read_json_input(input_path)
            if isinstance(data, str):
                texts = [data]
            elif isinstance(data, list):
                texts = [str(t) for t in data]
            elif isinstance(data, dict) and "texts" in data:
                texts = [str(t) for t in data["texts"]]
            else:
                print('Provide text, ["a","b"], or {"texts":[...]}', file=sys.stderr)
                return 1
            vectors = _embed_texts(model, texts)
            print_json({"embeddings": vectors, "dim": len(vectors[0]) if vectors else 0})
            return 0
        if cmd == "similarity":
            data = read_json_input(input_path)
            if not isinstance(data, dict) or "a" not in data or "b" not in data:
                print('Similarity expects {"a":"...", "b":"..."}', file=sys.stderr)
                return 1
            va, vb = _embed_texts(model, [str(data["a"]), str(data["b"])])
            print_json({"similarity": _cosine(va, vb)})
            return 0
        if cmd == "index":
            data = read_json_input(input_path)
            if not isinstance(data, dict) or "documents" not in data or "query" not in data:
                print('Index expects {"documents":[...], "query":"..."}', file=sys.stderr)
                return 1
            docs = [str(d) for d in data["documents"]]
            query = str(data["query"])
            doc_vecs = _embed_texts(model, docs)
            q_vec = _embed_texts(model, [query])[0]
            scores = [
                {"document": d, "score": _cosine(q_vec, v)}
                for d, v in zip(docs, doc_vecs, strict=True)
            ]
            scores.sort(key=lambda x: cast(float, x["score"]), reverse=True)
            print_json({"results": scores})
            return 0
        print(f"Unknown embeddings command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        try:
            import uvicorn
            from fastapi import FastAPI
        except ImportError:
            missing_extra("embeddings serve", "embeddings")
            return
        app = FastAPI(title="everyharness embeddings")

        @app.post("/embed")
        def embed(payload: dict[str, Any]) -> dict[str, Any]:
            texts = payload.get("texts") or [payload.get("text", "")]
            vectors = _embed_texts(model, [str(t) for t in texts])
            return {"embeddings": vectors}

        uvicorn.run(app, host=host, port=port, log_level="warning")

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        return finetune_model(model, dataset, opts, harness=self.name)

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Text embeddings: embed, similarity, and local index search.",
            requires_api=">=1,<2",
        )
