# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

## [0.1.3] - 2026-08-08

### Fixed

- Mypy: narrow llama-cpp completion response before indexing (`stream=False` + dict check)

## [0.1.2] - 2026-08-08

### Fixed

- Detector and vision harness no longer treat image/audio files (`.png`, `.wav`, …) as model artifacts
- Vision `detect` command returns a clear unsupported error instead of implying object detection exists
- Generic `predict` on non-callable models errors instead of returning a stub JSON payload
- Speech `speak` exits non-zero (TTS not implemented) instead of a fake success payload

### Changed

- Documented current harness capabilities and limits across README, catalog, architecture, harness `describe()`, and examples
- Computer harness documented as experimental dry-run / echo-only (not real OS control)
- `everyharness ui` docs clarify it writes a prompt pack, not a finished UI
- LLM/vision extras now include the libraries those harnesses actually import (`transformers`, `onnxruntime`)
- New optional extra `llm-gguf` for `llama-cpp-python`
- Package description marks the project as alpha

## [0.1.1] - 2026-08-08

### Fixed

- `everyharness add` no longer silently registers missing local paths as bare refs
- `everyharness run` forwards harness flags like `--input` without requiring `--`
- `--input` accepts inline JSON (`{…}` / `[…]`) as well as file paths
- Tabular `predict` accepts `{"features":…}` / `{"X":…}` to match serve API and docs
- Tabular predict/evaluate/serve return friendly errors instead of raw tracebacks / HTTP 500
- Offline mode blocks update network calls before hitting PyPI/GitHub
- Computer harness accepts `dry-run` as an alias for `plan`

### Changed

- Plugin catalog now indexes built-in harnesses/loaders/templates so `plugin search tabular` works

## [0.1.0] - 2026-08-07

### Added

- PyPI package `everyharness` with `everyharness` CLI entry points
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

[0.1.3]: https://github.com/kavin0x/everyharness/releases/tag/v0.1.3
[0.1.2]: https://github.com/kavin0x/everyharness/releases/tag/v0.1.2
[0.1.1]: https://github.com/kavin0x/everyharness/releases/tag/v0.1.1
[0.1.0]: https://github.com/kavin0x/everyharness/releases/tag/v0.1.0
