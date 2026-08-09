"""Diffusion harness (text-to-image generation)."""

from __future__ import annotations

import sys
from pathlib import Path

from everyharness.finetune import finetune_model
from everyharness.harnesses._util import missing_extra, print_json
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


class DiffusionHarness:
    name = "diffusion"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "diffusion":
            return 0.95
        if model.uri.lower().startswith("diffusion:"):
            return 0.9
        repo = str(model.metadata.get("repo_id", "")).lower()
        if "stable-diffusion" in repo or "diffusion" in repo:
            return 0.85
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: generate <prompt> [--out FILE] [--steps N] [--seed N]")
            return 1
        if argv[0] != "generate":
            print(f"Unknown diffusion command: {argv[0]}", file=sys.stderr)
            return 1
        prompt = argv[1] if len(argv) > 1 else ""
        out_path = Path("output.png")
        steps = 20
        seed = 0
        if "--out" in argv:
            out_path = Path(argv[argv.index("--out") + 1])
        if "--steps" in argv:
            steps = int(argv[argv.index("--steps") + 1])
        if "--seed" in argv:
            seed = int(argv[argv.index("--seed") + 1])
        try:
            import torch
            from diffusers import StableDiffusionPipeline
        except ImportError:
            return missing_extra("diffusion generate", "diffusion")
        model_id = model.metadata.get("repo_id") or model.metadata.get("snapshot_path") or model.uri
        if str(model_id).startswith("diffusion:"):
            model_id = str(model_id).split(":", 1)[1]
        pipe = StableDiffusionPipeline.from_pretrained(str(model_id))  # type: ignore[no-untyped-call]
        generator = torch.Generator().manual_seed(seed)
        image = pipe(prompt, num_inference_steps=steps, generator=generator).images[0]
        image.save(out_path)
        print_json({"output": str(out_path), "prompt": prompt, "steps": steps, "seed": seed})
        return 0

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        raise NotImplementedError(
            "Diffusion HTTP serve is not implemented in v1. "
            "Use: everyharness run <id> generate '<prompt>'"
        )

    def finetune(self, model: ModelRef, dataset: Path, opts: TrainOpts) -> ModelRef:
        return finetune_model(model, dataset, opts, harness=self.name)

    def templates(self) -> list[TemplateRef]:
        return []

    def describe(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            version="0.1.0",
            api_version=self.api_version,
            kind="harness",
            summary="Text-to-image generate via Diffusers (CLI only; no HTTP serve in v1).",
            requires_api=">=1,<2",
        )
