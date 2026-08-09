"""Experimental computer-action harness (dry-run / echo only in v1)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from everyharness.harnesses._util import print_json
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


class ComputerHarness:
    name = "computer"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "computer":
            return 0.95
        if model.uri.lower().startswith("computer:"):
            return 0.9
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        allow_control = "--allow-control" in argv
        filtered = [a for a in argv if a != "--allow-control"]
        if not filtered:
            print("Usage: plan|dry-run <json-action> [--allow-control]")
            print("Default mode is dry-run (logs JSON; does not control the OS).")
            print("With --allow-control, only {\"type\":\"echo\",\"message\":\"...\"} is executed.")
            return 1
        cmd = filtered[0]
        if cmd in {"plan", "dry-run"}:
            action_raw = filtered[1] if len(filtered) > 1 else "{}"
            try:
                action = json.loads(action_raw)
            except json.JSONDecodeError:
                action = {"type": "raw", "text": action_raw}
            # dry-run alias always logs without executing, even with --allow-control
            force_dry = cmd == "dry-run"
            effective_allow = allow_control and not force_dry
            session_log = {
                "model": model.uri,
                "dry_run": not effective_allow,
                "action": action,
            }
            if not effective_allow:
                session_log["result"] = "dry-run: action logged, not executed"
                print_json(session_log)
                return 0
            if not _permissions_ok():
                print(
                    "Control blocked: set EVERYHARNESS_ALLOW_COMPUTER=1 "
                    "(and grant OS permissions if required).",
                    file=sys.stderr,
                )
                return 1
            session_log["result"] = _execute_action(action)
            print_json(session_log)
            return 0
        print(f"Unknown computer command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError(
            "Computer harness has no HTTP serve in v1. Use: everyharness run <id> plan '<json>'"
        )

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        raise NotImplementedError("Computer harness does not support fine-tuning")

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary=(
                "Experimental action planner: dry-run logs JSON; "
                "--allow-control only supports echo (no real OS control)."
            ),
            requires_api=">=1,<2",
        )


def _permissions_ok() -> bool:
    """Best-effort permission gate; always false in CI."""
    import os

    if os.environ.get("CI"):
        return False
    return os.environ.get("EVERYHARNESS_ALLOW_COMPUTER", "").lower() in {"1", "true", "yes"}


def _execute_action(action: dict[str, object]) -> str:
    """Minimal safe executor for v1 — only supports echo actions."""
    action_type = action.get("type")
    if action_type == "echo":
        return str(action.get("message", ""))
    return (
        f"unsupported action type: {action_type} "
        '(v1 only supports {"type":"echo","message":"..."})'
    )
