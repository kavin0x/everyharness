# Architecture

everyharness is a **platform** for running local models through pluggable harnesses—not a closed toolbox.

## Flow

1. User installs `pip install everyharness` and runs `everyharness add <ref>`.
2. **Plugin host** loads built-in entry points plus installed `everyharness-*` packages.
3. **Detectors** score model kind; user can override with `--type`.
4. Matching **harness** runs CLI, serve, or train paths.
5. Optional **templates** scaffold extra CLI or project files.
6. Optional `everyharness ui --agent …` writes coding-agent prompt packs under `./harness-ui/<id>/`.

## Components

| Layer | Responsibility |
|-------|----------------|
| CLI (`everyharness`) | Typer commands, Rich output |
| TUI | Textual fullscreen UI |
| Core | Registry, config, cache, autoupdate |
| Plugin host | Entry-point discovery, API compat, isolation |
| Built-ins | Generic harness, local loader, builtin detector, cli-stub templates |
| Community | PyPI packages via `everyharness.harnesses` / `loaders` / `detectors` / `templates` |

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
