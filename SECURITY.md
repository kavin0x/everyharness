# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories or email the maintainers. Do not open public issues for undisclosed vulnerabilities.

## Known risk areas

### Pickle and untrusted model files

Loading pickled models can execute arbitrary code. Use `--trust-pickle` only for models from trusted sources.

### Third-party plugins

`everyharness plugin install` runs `pip install` and loads entry-point code at startup. Treat plugin installs like installing arbitrary Python packages.

### Computer-use harness

Computer-control features must stay opt-in (`--allow-control`). Never enable real OS control in CI or shared environments.

### Coding-agent bridge

`everyharness ui` writes prompt packs locally. Review generated code before running agents against production systems.

## Dependency updates

Core dependencies are scanned in CI. Report supply-chain concerns with reproduction steps.
