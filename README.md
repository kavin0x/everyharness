# everyharness

Register a local model. Run it through one harness. Offline-first CLI + TUI for people who keep models on disk (sklearn, embeddings, Ollama/GGUF/HF, vision, more) and want one interface instead of five tools.

**[PyPI](https://pypi.org/project/everyharness/)** · macOS / Linux (v1) · Apache 2.0

![everyharness demo](docs/demo/demo.gif)

## Why I built this

I kept wiring the same “detect model → run the right commands → maybe serve HTTP” glue for different local stacks. Ollama, Gradio, and BentoML each solve a slice. I wanted a thin registry + harness layer that stays offline-first and plugin-shaped. So I shipped everyharness as a CLI/TUI on PyPI.

## Typical stack vs this

| | Piecing Ollama / Gradio / notebooks | everyharness |
|---|---|---|
| Interface | Different per model type | One CLI / TUI |
| Offline | Easy to accidentally hit the network | `EVERYHARNESS_OFFLINE=1` hard-blocks outbound |
| Plugins | Ad hoc scripts | `everyharness-*` packages + `plugin init` |
| Honesty | Often “works for everything” marketing | Alpha table — what’s solid vs thin |

## Features

**Core**
- Model registry (local files, Hugging Face, Ollama, Python callables)
- Harness selection by kind / URI (override with `--type`)
- Same flow: `add` → `run` → `serve` → `train` (train depth varies)
- Textual TUI: bare `everyharness`
- Agent prompt pack: `everyharness ui` writes files for a coding agent (doesn’t build the UI itself)

**Maturity (alpha — be honest)**

| Area | Status |
| --- | --- |
| Tabular (sklearn/joblib) | Solid — predict, evaluate, explain, HTTP serve |
| Embeddings | Usable |
| LLM | Thin wrapper (Ollama; optional GGUF / HF) |
| Vision | Classify only |
| Diffusion | CLI generate only |
| Speech | Transcribe only (install whisper yourself) |
| Computer | Experimental |
| Community plugins | None curated yet |

Pickles need `--trust-pickle`. Prefer joblib from sources you trust.

## Try it

```bash
pip install everyharness
# optional: pip install 'everyharness[tabular]' / '[llm]' / '[all]'

everyharness add ./model.pkl --trust-pickle
everyharness add embeddings:demo --type embeddings
everyharness list

everyharness run --trust-pickle <id> predict --input '[[1.5, 0.5]]'
everyharness
```

Dev: `uv sync --all-extras --dev && uv run pytest -q`

## Stack

Python · Textual TUI · plugin host · optional extras for tabular / LLM / vision · Apache 2.0

## License

[Apache License 2.0](LICENSE) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)
