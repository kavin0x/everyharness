# Plugin API reference

Stable import surface: `everyharness.plugin` and `everyharness.plugin.protocols`.

## Constants

- `PLUGIN_API_VERSION` — current SDK version (e.g. `1.0.0`).

## Types

### `ModelRef`

```python
@dataclass(frozen=True)
class ModelRef:
    id: str
    uri: str
    kind: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### `PluginInfo`

Metadata for discovery and `everyharness doctor`.

### `TrainOpts`

Fine-tune options stub (`epochs`, `learning_rate`, `output_dir`, `extra`).

### `TemplateRef`

Template name within a pack (`pack`, `name`, `description`).

## Protocols

### `HarnessPlugin`

| Member | Description |
|--------|-------------|
| `name`, `api_version` | Identity |
| `matches(model)` | Score 0.0–1.0 fit |
| `run_cli(model, argv)` | Subprocess-style CLI |
| `serve(model, host, port)` | Optional HTTP server |
| `finetune(model, dataset, opts)` | Optional training |
| `templates()` | Linked template refs |
| `describe()` | `PluginInfo` |

### `LoaderPlugin`

`can_load(uri)`, `load(uri)`, `describe()`.

### `DetectorPlugin`

`score(model)`, `describe()`.

### `TemplatePack`

`list_templates()`, `render(model, dest, vars)`, `describe()`.

## Compatibility

`is_api_compatible(plugin_api_version, requires_api)` checks major version alignment.

Incompatible plugins are skipped at load time; errors surface in `everyharness plugin doctor`.

## CLI integration

| Command | Purpose |
|---------|---------|
| `everyharness plugin list` | Discovered plugins |
| `everyharness plugin install <pypi>` | `pip install` wrapper |
| `everyharness plugin init` | Scaffold new package |
| `everyharness template apply` | Render template pack |

## Coding-agent bridge

`everyharness ui <id> --agent cursor|claude|copilot|pi|codex` writes prompt packs to `./harness-ui/<id>/` without invoking the public SDK directly, but uses `ModelRef` from the registry.
