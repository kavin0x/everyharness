"""Local model registry."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from everyharness.core.config import registry_path
from everyharness.core.errors import RegistryError
from everyharness.plugin.protocols import ModelRef


class ModelRecord(BaseModel):
    """Persisted model entry."""

    id: str
    ref: str
    kind: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str

    def to_model_ref(self) -> ModelRef:
        return ModelRef(
            id=self.id,
            uri=self.ref,
            kind=self.kind,
            metadata=dict(self.metadata),
        )


class ModelRegistry:
    """JSON-backed registry of known models."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or registry_path()
        self._models: dict[str, ModelRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._models = {}
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RegistryError(f"Invalid registry file: {self._path}") from exc
        models = raw.get("models", {})
        self._models = {mid: ModelRecord.model_validate(data) for mid, data in models.items()}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"models": {mid: rec.model_dump() for mid, rec in self._models.items()}}
        text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        self._path.write_text(text, encoding="utf-8")

    def list(self) -> list[ModelRecord]:
        return sorted(self._models.values(), key=lambda m: m.created_at)

    def get(self, model_id: str) -> ModelRecord | None:
        return self._models.get(model_id)

    def add(
        self,
        ref: str,
        *,
        kind: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ModelRecord:
        now = datetime.now(UTC).isoformat()
        model_id = str(uuid.uuid4())[:8]
        record = ModelRecord(
            id=model_id,
            ref=ref,
            kind=kind,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
        )
        self._models[model_id] = record
        self._save()
        return record

    def remove(self, model_id: str) -> bool:
        if model_id not in self._models:
            return False
        del self._models[model_id]
        self._save()
        return True

    def update(self, model_id: str, **fields: Any) -> ModelRecord:
        record = self._models.get(model_id)
        if record is None:
            raise RegistryError(f"Unknown model id: {model_id}")
        data = record.model_dump()
        data.update(fields)
        data["updated_at"] = datetime.now(UTC).isoformat()
        updated = ModelRecord.model_validate(data)
        self._models[model_id] = updated
        self._save()
        return updated
