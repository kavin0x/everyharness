"""Speech harness (Whisper transcription)."""

from __future__ import annotations

import sys
from pathlib import Path

from everyharness.harnesses._util import print_json, unsupported
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


class SpeechHarness:
    name = "speech"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "speech":
            return 0.95
        # Audio files are inputs, not speech models.
        repo = str(model.metadata.get("repo_id", "")).lower()
        uri = model.uri.lower()
        if "whisper" in repo or "whisper" in uri:
            return 0.9
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: transcribe <audio-file>")
            print("Note: TTS (speak) is not implemented in v1.")
            return 1
        cmd = argv[0]
        if cmd == "transcribe":
            if len(argv) < 2:
                print("transcribe requires an audio file path", file=sys.stderr)
                return 1
            audio = argv[1]
            try:
                import whisper
            except ImportError:
                print(
                    "Missing optional dependency for speech transcribe: openai-whisper. "
                    "Install with: pip install openai-whisper "
                    "(not bundled in everyharness extras: upstream numba/llvmlite pins "
                    "may not support your Python version).",
                    file=sys.stderr,
                )
                return 1
            model_name = model.metadata.get("repo_id") or model.metadata.get("model") or "base"
            if str(model_name).startswith("hf:"):
                model_name = str(model_name).split(":", 1)[1]
            wmodel = whisper.load_model(str(model_name))
            result = wmodel.transcribe(audio)
            print_json({"text": result.get("text", ""), "language": result.get("language")})
            return 0
        if cmd == "speak":
            return unsupported("TTS (speak) is not implemented in v1; only transcribe is available")
        print(f"Unknown speech command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError(
            "Speech HTTP serve is not implemented in v1. "
            "Use: everyharness run <id> transcribe <audio>"
        )

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        raise NotImplementedError("Speech fine-tuning is not supported in v1")

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary=(
                "Whisper transcription only (install openai-whisper separately); "
                "no TTS/serve in v1."
            ),
            requires_api=">=1,<2",
        )
