# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

## [0.1.0] - 2026-08-07

### Added

- PyPI package `everyharness` with `everyharness` / `everyharness` CLI entry points
- Plugin SDK (`everyharness.plugin`) with harness, loader, detector, and template protocols
- Plugin host with entry-point discovery and broken-plugin isolation
- `everyharness plugin` commands: list, search, info, install, init, doctor
- `everyharness template` list/apply with built-in `cli-stub` pack
- Model registry (`everyharness add`, `list`)
- Textual TUI launcher (`everyharness` with no subcommand)
- Coding-agent bridge: `everyharness ui` for cursor, claude, copilot, pi, codex
- Autoupdate: `everyharness update` with PyPI check and GitHub Releases fallback
- Offline mode via `EVERYHARNESS_OFFLINE=1`
- Generic harness and local loader built-ins
- Example third-party plugin in `examples/sample-plugin/`
- CI (ruff, mypy, pytest) and PyPI release workflow on version tags

[0.1.0]: https://github.com/kavin0x/everyharness/releases/tag/v0.1.0
