"""Configuration and directory layout."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import PlatformDirs
from pydantic import BaseModel, Field

APP_NAME = "everyharness"
APP_AUTHOR = "everyharness"


def is_offline() -> bool:
    """Return True when network operations should be blocked."""
    value = os.environ.get("EVERYHARNESS_OFFLINE", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_dirs() -> PlatformDirs:
    return PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)


class Config(BaseModel):
    """User configuration persisted under the config directory."""

    offline: bool = Field(default=False)
    default_profile: str = Field(default="default")

    @classmethod
    def load(cls) -> Config:
        path = config_path()
        if not path.exists():
            return cls(offline=is_offline())
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        cfg = cls.model_validate(data)
        if is_offline():
            cfg.offline = True
        return cfg

    def save(self) -> None:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        import json

        path.write_text(
            json.dumps(self.model_dump(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def config_dir() -> Path:
    return get_dirs().user_config_path


def config_path() -> Path:
    return config_dir() / "config.json"


def cache_dir() -> Path:
    path = get_dirs().user_cache_path
    path.mkdir(parents=True, exist_ok=True)
    return path


def data_dir() -> Path:
    path = get_dirs().user_data_path
    path.mkdir(parents=True, exist_ok=True)
    return path


def registry_path() -> Path:
    return data_dir() / "registry.json"


def templates_dir() -> Path:
    path = data_dir() / "templates"
    path.mkdir(parents=True, exist_ok=True)
    return path
