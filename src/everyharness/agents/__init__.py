"""Coding-agent bridge for optional GUI generation."""

from everyharness.agents.bridge import (
    default_ui_root,
    materialize_ui_pack,
    prepare_ui_bridge,
    ui_dest_for_model,
)
from everyharness.agents.detect import AGENT_IDS, AgentId, AgentStatus, detect_agent, detect_all

__all__ = [
    "AGENT_IDS",
    "AgentId",
    "AgentStatus",
    "default_ui_root",
    "detect_agent",
    "detect_all",
    "materialize_ui_pack",
    "prepare_ui_bridge",
    "ui_dest_for_model",
]
