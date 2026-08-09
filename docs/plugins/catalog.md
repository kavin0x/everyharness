# Plugin catalog

Curated index of everyharness plugins. Runtime discovery uses PyPI entry points; this catalog is for **discovery and onboarding**.

> Installing a plugin executes third-party code. Review packages before `everyharness plugin install`.

## Built-in (core package)

| Name | Kind | Summary |
| ------ | ------ | --------- |
| `generic` | harness | Python callables (`call`/`info`); not a general runner |
| `tabular` | harness | sklearn/joblib predict, evaluate, explain, serve |
| `embeddings` | harness | embed, similarity, local index search |
| `llm` | harness | Thin Ollama/GGUF/HF wrapper + OpenAI-compatible `/v1` |
| `vision` | harness | Image classification (ONNX + HF); no object detect |
| `speech` | harness | Whisper transcribe only (manual whisper install) |
| `diffusion` | harness | text-to-image generate (CLI only) |
| `computer` | harness | Experimental dry-run planner; echo-only control |
| `local` | loader | local filesystem paths |
| `huggingface` | loader | `hf:org/model` with offline cache |
| `ollama` | loader | `ollama:model` via local daemon |
| `callable` | loader | `callable:module:attr` / `python:…` |
| `cli-stub` | templates | minimal CLI scaffold |

All of the above ship in PyPI package `everyharness`.

## Community

No third-party plugins are curated yet. The sample below is docs-only.

| PyPI | Kind | Summary | Maintainer |
|------|------|---------|------------|
| `everyharness-sample` | harness | Docs-only example plugin | everyharness |
| _(your package)_ | harness | Add yours via PR | — |

## Search locally

```bash
everyharness plugin search tabular
everyharness plugin search llm
everyharness plugin list
```

## Publish your plugin

1. `everyharness plugin init myfeat --kind harness`
2. `pip install -e . && pytest`
3. Publish `everyharness-myfeat` to PyPI
4. PR a row to this file + use GitHub topic `everyharness-plugin`

See [authoring.md](authoring.md).
