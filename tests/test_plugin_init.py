"""Plugin init scaffold tests."""

from pathlib import Path

from everyharness.plugin.init_scaffold import scaffold_plugin


def test_scaffold_harness_package(tmp_path: Path) -> None:
    dest = scaffold_plugin("demo", "harness", tmp_path)
    assert dest.is_dir()
    assert (dest / "pyproject.toml").exists()
    assert (dest / "src" / "everyharness_demo" / "plugin.py").exists()
    assert (dest / "tests" / "test_plugin.py").exists()
    content = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert "everyharness-demo" in content
    assert "everyharness.harnesses" in content


def test_scaffold_templates_package(tmp_path: Path) -> None:
    dest = scaffold_plugin("wrap", "templates", tmp_path)
    tmpl = dest / "src" / "everyharness_wrap" / "templates" / "template.toml"
    assert tmpl.exists()
