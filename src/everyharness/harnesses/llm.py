"""LLM harness: REPL + OpenAI-compatible server."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx

from everyharness.finetune import finetune_model
from everyharness.harnesses._util import missing_extra
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


def _ollama_base(model: ModelRef) -> str:
    return str(model.metadata.get("base_url", "http://127.0.0.1:11434")).rstrip("/")


def _ollama_model_name(model: ModelRef) -> str:
    if model.metadata.get("model"):
        return str(model.metadata["model"])
    uri = model.uri
    for prefix in ("ollama:", "ollama://"):
        if uri.lower().startswith(prefix):
            return uri[len(prefix) :]
    return uri


def _chat_ollama(model: ModelRef, messages: list[dict[str, str]], *, stream: bool = False) -> Any:
    payload = {
        "model": _ollama_model_name(model),
        "messages": messages,
        "stream": stream,
    }
    with httpx.Client(timeout=120.0) as client:
        if stream:
            with client.stream("POST", f"{_ollama_base(model)}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    msg = chunk.get("message", {})
                    content = msg.get("content", "")
                    if content:
                        yield content
                    if chunk.get("done"):
                        break
        else:
            resp = client.post(f"{_ollama_base(model)}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json().get("message", {}).get("content", "")


def _chat_gguf(model: ModelRef, messages: list[dict[str, str]]) -> str:
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise ImportError("llama-cpp-python required for GGUF models") from exc
    path = model.metadata.get("cached_path") or model.uri
    llm = Llama(model_path=str(path), verbose=False)
    prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
    out = llm(prompt, max_tokens=256)
    return str(out["choices"][0]["text"])


def _chat_hf(model: ModelRef, messages: list[dict[str, str]]) -> str:
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise ImportError("transformers required for HF text generation") from exc
    path = model.metadata.get("snapshot_path") or model.metadata.get("repo_id") or model.uri
    gen = pipeline("text-generation", model=str(path))
    prompt = messages[-1]["content"] if messages else ""
    result = gen(prompt, max_new_tokens=128)
    if isinstance(result, list) and result:
        return str(result[0].get("generated_text", ""))
    return ""


def _generate(model: ModelRef, messages: list[dict[str, str]], *, stream: bool = False) -> Any:
    uri = model.uri.lower()
    if uri.startswith(("ollama:", "ollama://")) or model.metadata.get("source") == "ollama":
        return _chat_ollama(model, messages, stream=stream)
    if uri.endswith(".gguf") or model.metadata.get("format") == "gguf":
        if stream:
            yield _chat_gguf(model, messages)
        else:
            return _chat_gguf(model, messages)
    return _chat_hf(model, messages)


class LLMHarness:
    name = "llm"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "llm":
            return 0.95
        uri = model.uri.lower()
        if uri.startswith(("ollama:", "ollama://", "hf:", "huggingface:")):
            return 0.9
        if uri.endswith((".gguf", ".safetensors", ".bin")):
            return 0.85
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: repl | complete <prompt>")
            return 1
        if argv[0] in {"repl", "chat"}:
            print("LLM REPL (Ctrl-D or 'exit' to quit)")
            history: list[dict[str, str]] = []
            while True:
                try:
                    line = input("> ").strip()
                except EOFError:
                    print()
                    break
                if not line or line.lower() in {"exit", "quit"}:
                    break
                history.append({"role": "user", "content": line})
                try:
                    reply = _generate(model, history)
                    text = "".join(reply) if isinstance(reply, Iterator) else str(reply)
                except Exception as exc:
                    print(f"Error: {exc}", file=sys.stderr)
                    continue
                history.append({"role": "assistant", "content": text})
                print(text)
            return 0
        if argv[0] == "complete":
            prompt = " ".join(argv[1:]) or ""
            try:
                text = _generate(model, [{"role": "user", "content": prompt}])
                if isinstance(text, Iterator):
                    text = "".join(text)
                print(text)
            except Exception as exc:
                print(f"Error: {exc}", file=sys.stderr)
                return 1
            return 0
        print("Usage: repl | complete <prompt>")
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        try:
            import uvicorn
            from fastapi import FastAPI
            from fastapi.responses import JSONResponse, StreamingResponse
        except ImportError:
            missing_extra("LLM serve", "llm")
            return
        app = FastAPI(title="everyharness LLM (OpenAI-compatible subset)")

        @app.get("/v1/models")
        def list_models() -> dict[str, Any]:
            return {
                "object": "list",
                "data": [{"id": model.id, "object": "model", "owned_by": "everyharness"}],
            }

        @app.post("/v1/chat/completions")
        def chat_completions(body: dict[str, Any]) -> Any:
            messages = body.get("messages", [])
            stream = bool(body.get("stream"))
            if stream:
                def gen() -> Iterator[str]:
                    for chunk in _generate(model, messages, stream=True):
                        payload = {
                            "choices": [{"delta": {"content": chunk}}],
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                    yield "data: [DONE]\n\n"

                return StreamingResponse(gen(), media_type="text/event-stream")
            text = _generate(model, messages)
            if isinstance(text, Iterator):
                text = "".join(text)
            return JSONResponse(
                {
                    "id": "eh-chat",
                    "object": "chat.completion",
                    "choices": [{"message": {"role": "assistant", "content": text}}],
                }
            )

        @app.post("/v1/completions")
        def completions(body: dict[str, Any]) -> dict[str, Any]:
            prompt = body.get("prompt", "")
            text = _generate(model, [{"role": "user", "content": prompt}])
            if isinstance(text, Iterator):
                text = "".join(text)
            return {
                "id": "eh-completion",
                "object": "text_completion",
                "choices": [{"text": text}],
            }

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
            summary="LLM REPL and OpenAI-compatible /v1 server (Ollama, GGUF, HF).",
            requires_api=">=1,<2",
        )
