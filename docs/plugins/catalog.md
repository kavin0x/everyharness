# Plugin catalog

Curated index of everyharness plugins. Runtime discovery uses PyPI entry points; this catalog is for **marketing and onboarding**.

> Installing a plugin executes third-party code. Review packages before `everyharness plugin install`.

## Built-in (core package)

| PyPI | Kind | Summary |
|------|------|---------|
| `everyharness` | harness | `generic` — fallback harness for unknown models |
| `everyharness` | loader | `local` — local file paths |
| `everyharness` | detector | `builtin` — basic kind sniffing |
| `everyharness` | templates | `cli-stub` — minimal CLI scaffold |

## Community (examples)

| PyPI | Kind | Summary | Maintainer |
|------|------|---------|------------|
| _(your package)_ | harness | Add yours via PR | — |

## Search locally

```bash
everyharness plugin search llm
everyharness plugin list
```

## Publish your plugin

1. `everyharness plugin init myfeat --kind harness`
2. `pip install -e . && pytest`
3. Publish `everyharness-myfeat` to PyPI
4. PR a row to this file + use GitHub topic `everyharness-plugin`

See [authoring.md](authoring.md).
