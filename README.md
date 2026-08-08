# everyharness

**Drop in any model. Get a harness.**

Offline-first CLI + TUI that detects model type, runs the right harness, serves HTTP, and scaffolds plugins — for tabular, embeddings, LLMs, vision, diffusion, computer use, and more.

[![CI](https://github.com/kavin0x/everyharness/actions/workflows/ci.yml/badge.svg)](https://github.com/kavin0x/everyharness/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/everyharness.svg)](https://pypi.org/project/everyharness/)
[![Python](https://img.shields.io/pypi/pyversions/everyharness.svg)](https://pypi.org/project/everyharness/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

![everyharness demo](docs/demo/demo.gif)

> macOS and Linux only in v1. Windows is not supported.

## Features

- **Drop-in models** — local files, Hugging Face, Ollama, or Python callables
- **Auto harness selection** — tabular, embeddings, LLM, vision, speech, diffusion, computer, generic
- **One CLI** — `everyharness add` → `everyharness run` → `everyharness serve` → `everyharness train`
- **Offline-first** — works without the network; `EVERYHARNESS_OFFLINE=1` hard-blocks outbound calls
- **Plugin system** — publish `everyharness-*` packages; scaffold with `everyharness plugin init`
- **Agent UI bridge** — `everyharness ui` writes a prompt pack for Cursor, Claude Code, Copilot, Pi, or Codex
- **Textual TUI** — launch with bare `everyharness`

## Install

```bash
pip install everyharness

# optional extras
pip install 'everyharness[tabular]'
pip install 'everyharness[llm]'
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

| Kind | Examples | Typical commands |
| ------ | ---------- | ------------------ |
| `tabular` | `.pkl` / `.joblib` sklearn | `predict`, `evaluate`, `explain` |
| `embeddings` | sentence-transformers, `embeddings:` | `embed`, `similarity` |
| `llm` | GGUF, Ollama, HF | `complete`, `repl`, `serve` |
| `vision` | image classifiers | harness-specific |
| `diffusion` | Diffusers pipelines | harness-specific |
| `generic` | Python callables | `call`, `predict`, `info` |

## Coding-agent UI bridge

Generate a prompt pack so your coding agent can scaffold a local web/GUI wrapper:

```bash
everyharness ui <model-id> --agent cursor
# → ./harness-ui/<id>/{AGENT_PROMPT.md,model-card.json,manifest.json,README.md}
```

## Plugins

Community packages publish as `everyharness-*` on PyPI:

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
