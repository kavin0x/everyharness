# everyharness-sample

Documentation-only example of a third-party **harness** plugin. Not published to PyPI.

Demonstrates entry points, `PluginInfo`, and the harness protocol without heavy dependencies.

## Setup

```bash
# From this directory
pip install -e ../..    # everyharness core from repo root
pip install -e .
```

## Verify

```bash
everyharness plugin list
# Should show sample harness from entry point

everyharness add ./any-path --type sample
everyharness list
# Use sample kind to match SampleHarness.matches()
```

## Package layout

```
everyharness_sample/
  __init__.py
  plugin.py      # SampleHarness class
pyproject.toml   # entry-points.everyharness.harnesses
```

## Publish your own

```bash
everyharness plugin init mymodel --kind harness
```

See [docs/plugins/authoring.md](../../docs/plugins/authoring.md).
