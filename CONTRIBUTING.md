# Contributing to everyharness

Thank you for helping grow the everyharness ecosystem. We optimize for **small core, large plugin surface**.

## Two contribution tracks

### Track A — Core changes

Use for platform fixes, plugin host, CLI/TUI, built-in harnesses that seed the API, and documentation.

1. Fork and branch from `main`.
2. `uv sync --all-extras --dev`
3. `uv run pytest -q && uv run ruff check src tests`
4. Open a PR with Conventional Commits title (`feat:`, `fix:`, `docs:`, etc.).

### Track B — External plugin (preferred for new model types)

**Preferred** when your feature is a new harness, loader, detector, or template pack that does not require core changes.

1. `everyharness plugin init <name> --kind harness|loader|detector|templates`
2. Implement the protocol in `everyharness.plugin`.
3. Test with `from everyharness.testing import assert_harness_plugin` (when available).
4. Publish to PyPI as `everyharness-<name>`.
5. Open a PR to add your package to [docs/plugins/catalog.md](docs/plugins/catalog.md).

## What belongs in core vs a plugin

| In core | In a plugin |
|---------|-------------|
| Plugin host, registry, config, update | Long-tail model formats |
| Generic harness + template engine | Domain-specific harness UX |
| Seed harnesses (LLM, tabular, …) | Optional heavy ML stacks |
| Public SDK + contract tests | Vendor-specific loaders |

## API compatibility

- Core exposes `PLUGIN_API_VERSION` (currently `1.0.0`).
- Plugins declare `requires_api = ">=1,<2"` in `describe()`.
- Breaking SDK changes only on major core releases with deprecation warnings.

## Security

Installing a plugin runs third-party code. Review packages before `everyharness plugin install`. See [SECURITY.md](SECURITY.md).

## Getting listed in the catalog

Add a row to `docs/plugins/catalog.md` with PyPI name, kind, summary, and maintainer link. We use labels `good first plugin` and `plugin-api` on GitHub for onboarding.

## Commits and releases

- [Conventional Commits](https://www.conventionalcommits.org/)
- [SemVer](https://semver.org/) for `everyharness` and plugins
