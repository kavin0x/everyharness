"""Detect installed coding-agent CLIs."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal

AgentId = Literal["cursor", "claude", "copilot", "pi", "codex"]

AGENT_IDS: tuple[AgentId, ...] = ("cursor", "claude", "copilot", "pi", "codex")


@dataclass(frozen=True)
class AgentStatus:
    """Availability of a coding-agent CLI."""

    agent: AgentId
    available: bool
    command: str | None
    install_hint: str
    notes: str = ""


_INSTALL_HINTS: dict[AgentId, str] = {
    "cursor": "Install Cursor from https://cursor.com and ensure `cursor` is on PATH.",
    "claude": "Install Claude Code: https://docs.anthropic.com/en/docs/claude-code/setup",
    "copilot": "Install GitHub CLI, then: gh extension install github/gh-copilot",
    "pi": "Install Pi agent CLI from your provider (e.g. pip install pi-agent or vendor docs).",
    "codex": "Install OpenAI Codex CLI: https://github.com/openai/codex",
}


def _gh_copilot_available() -> bool:
    gh = shutil.which("gh")
    if gh is None:
        return False
    try:
        proc = subprocess.run(
            [gh, "copilot", "--help"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def detect_agent(agent: str) -> AgentStatus:
    """Return availability for a single agent id."""
    if agent not in AGENT_IDS:
        raise ValueError(f"Unknown agent: {agent}. Choose from: {', '.join(AGENT_IDS)}")
    return _detect_one(agent)


def detect_all() -> list[AgentStatus]:
    """Return availability for all supported agents."""
    return [_detect_one(agent) for agent in AGENT_IDS]


def _detect_one(agent: AgentId) -> AgentStatus:
    hint = _INSTALL_HINTS[agent]
    if agent == "copilot":
        if _gh_copilot_available():
            return AgentStatus(
                agent=agent,
                available=True,
                command="gh copilot",
                install_hint=hint,
            )
        return AgentStatus(
            agent=agent,
            available=False,
            command=None,
            install_hint=hint,
            notes="Requires GitHub CLI with the copilot extension.",
        )

    binary = agent
    path = shutil.which(binary)
    if path:
        return AgentStatus(
            agent=agent,
            available=True,
            command=binary,
            install_hint=hint,
        )
    return AgentStatus(
        agent=agent,
        available=False,
        command=None,
        install_hint=hint,
    )
