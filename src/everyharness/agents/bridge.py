"""Materialize coding-agent prompt packs under ./harness-ui/<model-id>/."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from everyharness.agents.detect import AgentId, AgentStatus, detect_agent
from everyharness.agents.prompts import build_agent_prompt, build_readme
from everyharness.plugin.protocols import ModelRef


def default_ui_root() -> Path:
    return Path.cwd() / "harness-ui"


def ui_dest_for_model(model_id: str, root: Path | None = None) -> Path:
    base = root or default_ui_root()
    return base / model_id


def materialize_ui_pack(
    model: ModelRef,
    agent: AgentId,
    *,
    dest: Path | None = None,
    root: Path | None = None,
) -> Path:
    """Write prompt pack and metadata to harness-ui/<model-id>/."""
    out = dest or ui_dest_for_model(model.id, root=root)
    out.mkdir(parents=True, exist_ok=True)

    model_card: dict[str, Any] = {
        "id": model.id,
        "uri": model.uri,
        "kind": model.kind,
        "metadata": dict(model.metadata),
    }
    (out / "model-card.json").write_text(
        json.dumps(model_card, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    prompt = build_agent_prompt(model, agent)
    (out / "AGENT_PROMPT.md").write_text(prompt + "\n", encoding="utf-8")

    readme = build_readme(model, agent, str(out))
    (out / "README.md").write_text(readme, encoding="utf-8")

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "agent": agent,
        "model_id": model.id,
        "everyharness_ui_pack": "1.0",
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out


def prepare_ui_bridge(
    model: ModelRef,
    agent: AgentId,
    *,
    dest: Path | None = None,
    root: Path | None = None,
) -> tuple[Path, AgentStatus]:
    """Materialize files and return destination plus agent CLI status."""
    status = detect_agent(agent)
    path = materialize_ui_pack(model, agent, dest=dest, root=root)
    return path, status
