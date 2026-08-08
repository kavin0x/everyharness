# Publishing a everyharness plugin

## Naming

- PyPI package: `everyharness-<shortname>`
- Python module: `everyharness_<shortname>` (recommended)

## Scaffold

```bash
everyharness plugin init mymodel --kind harness
cd everyharness-mymodel
pip install -e .
pytest
```

Kinds: `harness`, `loader`, `detector`, `templates`.

## Entry points

Register in `pyproject.toml`:

```toml
[project.entry-points."everyharness.harnesses"]
mymodel = "everyharness_mymodel:MymodelHarness"
```

Match the group to your plugin kind.

## API compatibility

Import from the public SDK:

```python
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    HarnessPlugin,
    ModelRef,
    PluginInfo,
)
```

Set `api_version = PLUGIN_API_VERSION` and `requires_api = ">=1,<2"` in `describe()`.

## Testing

Use contract helpers when available:

```python
from everyharness.testing import assert_harness_plugin
```

Run `everyharness plugin doctor` after install to verify entry points.

## Publishing to PyPI

1. Tag with SemVer (`v0.1.0`).
2. `uv build && uv publish` (or Trusted Publisher in CI).
3. Users install with `everyharness plugin install everyharness-mymodel`.

## Security expectations

- No auto-execute on import beyond plugin registration.
- Document network access, pickle usage, and OS permissions.
- Prefer lazy imports for heavy ML dependencies.

## Catalog listing

Open a PR to [catalog.md](catalog.md) with PyPI name, kind, one-line summary, and maintainer link.
