# Architecture

everyharness is a **plugin platform** for running local models through harnesses—not a full ML serving stack (use Ollama / Gradio / BentoML when you need those jobs done deeply).

## Flow

1. User installs `pip install everyharness` and runs `everyharness add <ref>`.
2. **Plugin host** loads built-in entry points plus installed `everyharness-*` packages.
3. **Detectors** score model kind from URI/extensions/metadata; user can override with `--type`.
   Image/audio *inputs* are not treated as model artifacts.
4. Matching **harness** runs CLI, serve, or train paths (capability varies by harness).
5. Optional **templates** scaffold extra CLI or project files.
6. Optional `everyharness ui --agent …` writes a **prompt pack** (not a finished UI) under `./harness-ui/<id>/`.

## Components

| Layer | Responsibility |
|-------|----------------|
| CLI (`everyharness`) | Typer commands, Rich output |
| TUI | Textual fullscreen UI |
| Core | Registry, config, cache, autoupdate |
| Plugin host | Entry-point discovery, API compat, isolation |
| Built-ins | Harnesses, loaders, builtin detector, cli-stub templates |
| Community | Optional PyPI packages via entry points (none curated yet) |

## Entry points

Third-party packages register via `pyproject.toml`:

```toml
[project.entry-points."everyharness.harnesses"]
myharness = "everyharness_my:MyHarness"
```

Discovery uses `importlib.metadata`—no central registry required at runtime.

## Offline contract

- Core works offline once models and plugins are local.
- `EVERYHARNESS_OFFLINE=1` blocks PyPI update checks, `everyharness plugin install`, and online search.
- Hugging Face downloads are user-initiated and respect offline mode.

## Versioning

- Core SemVer + `PLUGIN_API_VERSION` (currently `1.0.0`).
- Plugins declare `requires_api`; incompatible plugins are skipped with `everyharness doctor` warnings.

See also [Plugin API](plugins/api.md) and [Authoring](plugins/authoring.md).
