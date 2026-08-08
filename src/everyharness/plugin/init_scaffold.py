"""Scaffold third-party everyharness-* plugin packages."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

PluginKind = Literal["harness", "loader", "detector", "templates"]

_SCAFFOLD: dict[PluginKind, dict[str, str]] = {
    "harness": {
        "pyproject.toml": """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "everyharness-{name}"
version = "0.1.0"
description = "An everyharness harness plugin"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["everyharness>=0.1.0"]

[project.entry-points."everyharness.harnesses"]
{name} = "everyharness_{module}:MyHarness"

[tool.hatch.build.targets.wheel]
packages = ["src/everyharness_{module}"]
""",
        "README.md": """\
# everyharness-{name}

Harness plugin for [everyharness](https://pypi.org/project/everyharness/).

```bash
pip install -e .
everyharness plugin doctor
pytest
```
""",
        "src/everyharness_{module}/__init__.py": """\
from everyharness_{module}.plugin import MyHarness

__all__ = ["MyHarness"]
""",
        "src/everyharness_{module}/plugin.py": """\
from __future__ import annotations

from pathlib import Path

from everyharness.plugin import (
    HarnessPlugin,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)
from everyharness.plugin.protocols import PLUGIN_API_VERSION


class MyHarness:
    name = "{name}"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        print(f"Running harness for {{model.uri}} with args {{argv}}")
        return 0

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError("serve() not implemented yet")

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        raise NotImplementedError("finetune() not implemented yet")

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Example harness plugin scaffold.",
            requires_api=">=1,<2",
        )
""",
        "tests/test_plugin.py": """\
from everyharness.testing import assert_harness_plugin
from everyharness_{module}.plugin import MyHarness


def test_harness_contract() -> None:
    assert_harness_plugin(MyHarness())
""",
    },
    "loader": {
        "pyproject.toml": """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "everyharness-{name}"
version = "0.1.0"
description = "An everyharness loader plugin"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["everyharness>=0.1.0"]

[project.entry-points."everyharness.loaders"]
{name} = "everyharness_{module}:MyLoader"

[tool.hatch.build.targets.wheel]
packages = ["src/everyharness_{module}"]
""",
        "README.md": """\
# everyharness-{name}

Loader plugin for everyharness.
""",
        "src/everyharness_{module}/__init__.py": "",
        "src/everyharness_{module}/plugin.py": """\
from __future__ import annotations

from everyharness.plugin import LoaderPlugin, ModelRef, PluginInfo
from everyharness.plugin.protocols import PLUGIN_API_VERSION


class MyLoader:
    name = "{name}"
    api_version = PLUGIN_API_VERSION

    def can_load(self, uri: str) -> float:
        return 0.0

    def load(self, uri: str) -> ModelRef:
        return ModelRef(id="local", uri=uri)

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="loader",
            summary="Example loader plugin scaffold.",
            requires_api=">=1,<2",
        )
""",
        "tests/test_plugin.py": """\
from everyharness.testing import assert_loader_plugin
from everyharness_{module}.plugin import MyLoader


def test_loader_contract() -> None:
    assert_loader_plugin(MyLoader())
""",
    },
    "detector": {
        "pyproject.toml": """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "everyharness-{name}"
version = "0.1.0"
description = "An everyharness detector plugin"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["everyharness>=0.1.0"]

[project.entry-points."everyharness.detectors"]
{name} = "everyharness_{module}:MyDetector"

[tool.hatch.build.targets.wheel]
packages = ["src/everyharness_{module}"]
""",
        "README.md": """\
# everyharness-{name}

Detector plugin for everyharness.
""",
        "src/everyharness_{module}/__init__.py": "",
        "src/everyharness_{module}/plugin.py": """\
from __future__ import annotations

from everyharness.plugin import DetectorPlugin, ModelRef, PluginInfo
from everyharness.plugin.protocols import PLUGIN_API_VERSION


class MyDetector:
    name = "{name}"
    api_version = PLUGIN_API_VERSION

    def score(self, model: ModelRef) -> float:
        return 0.0

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="detector",
            summary="Example detector plugin scaffold.",
            requires_api=">=1,<2",
        )
""",
        "tests/test_plugin.py": """\
from everyharness.testing import assert_detector_plugin
from everyharness_{module}.plugin import MyDetector


def test_detector_contract() -> None:
    assert_detector_plugin(MyDetector())
""",
    },
    "templates": {
        "pyproject.toml": """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "everyharness-{name}"
version = "0.1.0"
description = "An everyharness template pack"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["everyharness>=0.1.0"]

[project.entry-points."everyharness.templates"]
{name} = "everyharness_{module}:MyTemplatePack"

[tool.hatch.build.targets.wheel]
packages = ["src/everyharness_{module}"]
""",
        "README.md": """\
# everyharness-{name}

Template pack for everyharness.
""",
        "src/everyharness_{module}/__init__.py": "",
        "src/everyharness_{module}/plugin.py": """\
from __future__ import annotations

from pathlib import Path
from typing import Any

from everyharness.plugin import ModelRef, PluginInfo, TemplateRef, TemplatePack
from everyharness.plugin.protocols import PLUGIN_API_VERSION
from everyharness.plugin.templates import load_template_manifest, render_template_pack


class MyTemplatePack:
    name = "{name}"
    api_version = PLUGIN_API_VERSION

    def __init__(self) -> None:
        self._root = Path(__file__).resolve().parent / "templates"

    def list_templates(self) -> list[TemplateRef]:
        manifest = load_template_manifest(self._root)
        from everyharness.plugin.templates import template_ref_from_manifest

        return template_ref_from_manifest(self.name, manifest)

    def render(self, model: ModelRef, dest: Path, vars: dict[str, Any]) -> Path:
        return render_template_pack(self._root, model=model, dest=dest, vars=vars)

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="templates",
            summary="Example template pack scaffold.",
            requires_api=">=1,<2",
        )
""",
        "src/everyharness_{module}/templates/template.toml": """\
name = "{name}"
default_template = "main"

[templates.main]
"README.md" = "README.md.j2"
""",
        "src/everyharness_{module}/templates/README.md.j2": """\
# Generated for {{ model_uri }}

Model id: {{ model_id }}
Kind: {{ model_kind }}
""",
        "tests/test_plugin.py": """\
from pathlib import Path

from everyharness.plugin import ModelRef
from everyharness.testing import assert_template_pack
from everyharness_{module}.plugin import MyTemplatePack


def test_template_pack_contract(tmp_path: Path) -> None:
    pack = MyTemplatePack()
    assert_template_pack(pack)
    model = ModelRef(id="abc", uri="./model.bin")
    pack.render(model, tmp_path / "out", {{}})
""",
    },
}


def _sanitize_module(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def scaffold_plugin(
    name: str,
    kind: PluginKind,
    dest: Path,
    *,
    force: bool = False,
) -> Path:
    """Write a publishable plugin package under dest/everyharness-{name}/."""
    module = _sanitize_module(name)
    package_dir = dest / f"everyharness-{name}"
    if package_dir.exists() and not force:
        raise FileExistsError(f"{package_dir} already exists (use --force to overwrite)")

    files = _SCAFFOLD[kind]
    for rel_path, content in files.items():
        path = package_dir / rel_path.format(name=name, module=module)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.format(name=name, module=module), encoding="utf-8")

    return package_dir
