# everyharness

**Register a local model. Run it through a harness.**

Alpha offline-first CLI + TUI for wrapping local models (sklearn, embeddings, Ollama/GGUF/HF LLMs, and more) behind one plugin interface. Not a replacement for Ollama, Gradio, or BentoML — a thin registry + harness layer.

[![CI](https://github.com/kavin0x/everyharness/actions/workflows/ci.yml/badge.svg)](https://github.com/kavin0x/everyharness/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/everyharness.svg)](https://pypi.org/project/everyharness/)
[![Python](https://img.shields.io/pypi/pyversions/everyharness.svg)](https://pypi.org/project/everyharness/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Socket Badge](https://badge.socket.dev/pypi/package/everyharness/0.1.3?artifact_id=tar-gz)](https://badge.socket.dev/pypi/package/everyharness/0.1.3?artifact_id=tar-gz)

![everyharness demo](docs/demo/demo.gif)

> macOS and Linux only in v1. Windows is not supported.

## What works today

| Area | Status |
| ------ | -------- |
| Tabular (sklearn/joblib) | **Solid** — `predict`, `evaluate`, `explain`, HTTP serve |
| Embeddings | **Usable** — embed/similarity; hash fallback without extras |
| LLM | **Thin wrapper** — Ollama HTTP; optional GGUF (`[llm-gguf]`) / HF (`[llm]`) |
| Vision | **Classify only** — ONNX/HF; no object detection |
| Diffusion | **CLI generate only** — no HTTP serve |
| Speech | **Transcribe only** — install `openai-whisper` yourself; no TTS/serve |
| Computer | **Experimental** — dry-run JSON log; `--allow-control` only supports `echo` |
| `everyharness ui` | **Prompt pack** — writes files for a coding agent; does not build a UI |
| Community plugins | **None yet** — scaffold with `plugin init`; catalog is built-ins + docs sample |

Pickles need `--trust-pickle` (loads arbitrary code). Prefer joblib from trusted sources.

## Features

- **Model registry** — local files, Hugging Face, Ollama, or Python callables
- **Harness selection** — by kind / URI; override with `--type`
- **One CLI** — `everyharness add` → `run` → `serve` → `train` (train depth varies by harness)
- **Offline-first** — `EVERYHARNESS_OFFLINE=1` hard-blocks outbound calls
- **Plugin system** — publish `everyharness-*` packages; scaffold with `everyharness plugin init`
- **Agent prompt pack** — `everyharness ui` writes prompts for Cursor, Claude Code, Copilot, Pi, or Codex
- **Textual TUI** — launch with bare `everyharness`

## Install

```bash
pip install everyharness

# optional extras
pip install 'everyharness[tabular]'
pip install 'everyharness[llm]'          # HF + OpenAI-compatible serve deps
pip install 'everyharness[llm,llm-gguf]' # + llama-cpp-python for local GGUF
pip install 'everyharness[vision]'
pip install 'everyharness[all]'
```

## Quick start

```bash
# register models (kind auto-detected when possible)
everyharness add ./model.pkl --trust-pickle
everyharness add embeddings:demo --type embeddings
everyharness add python:callable_demo:echo

everyharness list

# same interface, different harnesses
everyharness run --trust-pickle <id> predict --input '[[1.5, 0.5]]'
everyharness run <id> similarity --input '{"a":"cat","b":"kitten"}'
everyharness run <id> call --input '{"hello":"world"}'

# scaffold a publishable harness plugin
everyharness plugin init weather --kind harness
```

Launch the TUI:

```bash
everyharness
```

## Model types

| Kind | Examples | Typical commands | Notes |
| ------ | ---------- | ------------------ | ------- |
| `tabular` | `.pkl` / `.joblib` sklearn | `predict`, `evaluate`, `explain`, `serve` | Best-supported path |
| `embeddings` | sentence-transformers, `embeddings:` | `embed`, `similarity` | |
| `llm` | Ollama, GGUF, HF | `complete`, `repl`, `serve` | Thin wrapper over backends |
| `vision` | `.onnx`, HF classifiers | `classify` | No `detect` in v1 |
| `diffusion` | Diffusers pipelines | `generate` | No HTTP serve |
| `speech` | Whisper | `transcribe` | Separate whisper install |
| `computer` | `computer:` refs | `plan` / `dry-run` | Echo-only when control enabled |
| `generic` | Python callables | `call`, `info` | |

## Coding-agent prompt pack

Write metadata + `AGENT_PROMPT.md` so your coding agent can scaffold a local web/GUI wrapper (everyharness does not generate the UI itself):

```bash
everyharness ui <model-id> --agent cursor
# → ./harness-ui/<id>/{AGENT_PROMPT.md,model-card.json,manifest.json,README.md}
```

## Plugins

Built-in harnesses/loaders ship in the core package. Third-party packages can publish as `everyharness-*` on PyPI (none curated yet beyond the docs sample):

```bash
everyharness plugin search tabular
everyharness plugin install everyharness-foo
everyharness plugin init mymodel --kind harness   # harness | loader | detector | templates
```

- [Plugin catalog](docs/plugins/catalog.md)
- [Authoring guide](docs/plugins/authoring.md)
- [Plugin API](docs/plugins/api.md)

## Architecture

CLI/TUI → plugin host → harnesses / loaders / detectors / templates. See [docs/architecture.md](docs/architecture.md).

## Updates & offline

```bash
everyharness update --check
everyharness update --yes
```

Set `EVERYHARNESS_OFFLINE=1` to block update checks, HF downloads, and `everyharness plugin install`.

## Development

```bash
uv sync --all-extras --dev
uv run pytest -q
uv run ruff check src tests
```

## License

Apache-2.0 — see [LICENSE](LICENSE).

## Community

- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
