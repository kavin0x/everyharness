"""Template pack rendering tests."""

from pathlib import Path

from everyharness.plugin.protocols import ModelRef
from everyharness.plugin.templates import render_template_pack
from everyharness.templates.cli_stub import CliStubTemplatePack


def test_render_builtin_cli_stub(tmp_path: Path) -> None:
    model = ModelRef(id="abc123", uri="./models/test.pkl", kind="tabular")
    pack = CliStubTemplatePack()
    dest = tmp_path / "out"
    render_template_pack(pack._root, model=model, dest=dest)
    readme = (dest / "README.md").read_text(encoding="utf-8")
    assert "abc123" in readme
    assert "./models/test.pkl" in readme
    run_sh = dest / "run.sh"
    assert run_sh.exists()
    assert "model.bin" not in readme


def test_template_pack_render_via_class(tmp_path: Path) -> None:
    pack = CliStubTemplatePack()
    model = ModelRef(id="x", uri="/tmp/m", kind="llm")
    out = pack.render(model, tmp_path / "rendered", {})
    assert (out / "README.md").exists()
