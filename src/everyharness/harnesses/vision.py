"""Vision harness (image classification)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from everyharness.finetune import finetune_model
from everyharness.harnesses._util import missing_extra, print_json
from everyharness.plugin.protocols import (
    PLUGIN_API_VERSION,
    ModelRef,
    PluginInfo,
    TemplateRef,
    TrainOpts,
)


def _load_image(path: str) -> Any:
    try:
        from PIL import Image
    except ImportError as exc:
        raise ImportError("Pillow required for vision harness") from exc
    return Image.open(path).convert("RGB")


def _classify(model: ModelRef, image_path: str) -> dict[str, Any]:
    path = model.metadata.get("cached_path") or model.uri
    if str(path).endswith(".onnx"):
        try:
            import numpy as np
            import onnxruntime as ort
        except ImportError as exc:
            raise ImportError("onnxruntime and numpy required for ONNX vision") from exc
        img = _load_image(image_path)
        arr = np.asarray(img.resize((224, 224))).astype("float32") / 255.0
        arr = np.transpose(arr, (2, 0, 1))[None, ...]
        sess = ort.InferenceSession(str(path))
        input_name = sess.get_inputs()[0].name
        out = sess.run(None, {input_name: arr})[0]
        idx = int(out.argmax())
        return {"label_index": idx, "scores": out.flatten().tolist()}
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise ImportError("transformers required for HF vision models") from exc
    clf = pipeline("image-classification", model=str(path))
    result = clf(image_path)
    return {"predictions": result}


class VisionHarness:
    name = "vision"
    api_version = PLUGIN_API_VERSION

    def matches(self, model: ModelRef) -> float:
        if model.kind == "vision":
            return 0.95
        uri = model.uri.lower()
        # Model weights only — never treat input images as vision models.
        if uri.endswith((".onnx", ".pt", ".pth")):
            return 0.7
        repo = str(model.metadata.get("repo_id", "")).lower()
        if any(token in repo for token in ("vit", "resnet", "clip", "vision")):
            return 0.75
        return 0.0

    def run_cli(self, model: ModelRef, argv: list[str]) -> int:
        if not argv:
            print("Usage: classify <image> | list <directory>")
            return 1
        cmd = argv[0]
        if cmd == "classify":
            if len(argv) < 2:
                print("classify requires an image path", file=sys.stderr)
                return 1
            try:
                result = _classify(model, argv[1])
            except ImportError:
                return missing_extra("vision harness", "vision")
            except Exception as exc:
                print(f"Error: {exc}", file=sys.stderr)
                return 1
            print_json(result)
            return 0
        if cmd == "list":
            directory = Path(argv[1] if len(argv) > 1 else ".")
            exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
            files = sorted(p for p in directory.iterdir() if p.suffix.lower() in exts)
            print_json({"images": [str(p) for p in files]})
            return 0
        if cmd == "detect":
            print(
                "Object detection is not implemented in v1. Use: classify <image>",
                file=sys.stderr,
            )
            return 1
        print(f"Unknown vision command: {cmd}", file=sys.stderr)
        return 1

    def serve(self, model: ModelRef, host: str, port: int) -> None:
        try:
            import uvicorn
            from fastapi import FastAPI, UploadFile
        except ImportError:
            missing_extra("vision serve", "vision")
            return
        app = FastAPI(title="everyharness vision")

        @app.post("/classify")
        async def classify_endpoint(file: UploadFile) -> dict[str, Any]:
            tmp = Path("/tmp") / f"eh-vision-{file.filename}"
            tmp.write_bytes(await file.read())
            return _classify(model, str(tmp))

        uvicorn.run(app, host=host, port=port, log_level="warning")

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
            summary="Image classification via ONNX Runtime or Hugging Face pipelines.",
            requires_api=">=1,<2",
        )
