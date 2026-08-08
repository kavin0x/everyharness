"""Autoupdate helpers — PyPI primary, GitHub Releases fallback."""

from __future__ import annotations

import re

import httpx

from everyharness import __version__
from everyharness.core.config import is_offline
from everyharness.core.errors import OfflineError

PYPI_JSON_URL = "https://pypi.org/pypi/everyharness/json"
GITHUB_LATEST_RELEASE_URL = "https://api.github.com/repos/kavin0x/everyharness/releases/latest"
_USER_AGENT = "everyharness-update/0.1"


def current_version() -> str:
    return __version__


def _normalize_tag(tag: str) -> str:
    tag = tag.strip()
    if tag.startswith("v"):
        tag = tag[1:]
    return tag


def fetch_latest_pypi_version(timeout: float = 10.0) -> str | None:
    """Return latest version string from PyPI JSON API."""
    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": _USER_AGENT}) as client:
            response = client.get(PYPI_JSON_URL)
        if response.status_code != 200:
            return None
        info = response.json().get("info", {})
        version = info.get("version")
        if isinstance(version, str) and version.strip():
            return version.strip()
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    return None


def fetch_latest_github_version(timeout: float = 10.0) -> str | None:
    """Return latest release version from GitHub (tag_name without leading v)."""
    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": _USER_AGENT}) as client:
            response = client.get(GITHUB_LATEST_RELEASE_URL)
        if response.status_code != 200:
            return None
        tag = response.json().get("tag_name")
        if isinstance(tag, str) and tag.strip():
            return _normalize_tag(tag)
    except (httpx.HTTPError, ValueError, KeyError):
        return None
    return None


def fetch_latest_version(timeout: float = 10.0) -> str | None:
    """Resolve latest published version (PyPI, then GitHub Releases)."""
    if is_offline():
        raise OfflineError("Update checks are disabled in offline mode (EVERYHARNESS_OFFLINE=1).")
    latest = fetch_latest_pypi_version(timeout=timeout)
    if latest is not None:
        return latest
    return fetch_latest_github_version(timeout=timeout)


def check_for_update(timeout: float = 10.0) -> str | None:
    """Return latest version when newer than installed; None if up to date or unknown."""
    if is_offline():
        raise OfflineError("Update checks are disabled in offline mode (EVERYHARNESS_OFFLINE=1).")

    latest = fetch_latest_version(timeout=timeout)
    if latest is None:
        return None

    from packaging.version import Version

    try:
        if Version(latest) > Version(__version__):
            return latest
    except Exception:
        # Fallback string compare for non-semver tags
        if latest != __version__:
            return latest
    return None


def upgrade_command(latest: str | None = None) -> str:
    """Suggested pip upgrade command."""
    version = latest or fetch_latest_version() or ""
    if version and re.fullmatch(r"\d+\.\d+\.\d+", version):
        return f"pip install 'everyharness=={version}'"
    return "pip install -U everyharness"
