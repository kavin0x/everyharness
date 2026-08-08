"""Tests for PyPI / GitHub autoupdate."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from everyharness import __version__
from everyharness.core.errors import OfflineError
from everyharness.core.update import (
    check_for_update,
    fetch_latest_github_version,
    fetch_latest_pypi_version,
    fetch_latest_version,
    upgrade_command,
)


def test_fetch_latest_pypi_version():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"info": {"version": "0.2.0"}}

    with patch("everyharness.core.update.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.return_value = mock_response
        assert fetch_latest_pypi_version() == "0.2.0"


def test_fetch_latest_github_version_normalizes_tag():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"tag_name": "v0.2.0"}

    with patch("everyharness.core.update.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.return_value = mock_response
        assert fetch_latest_github_version() == "0.2.0"


def test_fetch_latest_version_falls_back_to_github():
    pypi_response = MagicMock(status_code=404)
    gh_response = MagicMock(status_code=200)
    gh_response.json.return_value = {"tag_name": "v0.3.0"}

    with patch("everyharness.core.update.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.side_effect = [pypi_response, gh_response]
        assert fetch_latest_version() == "0.3.0"


def test_check_for_update_returns_none_when_current():
    with patch("everyharness.core.update.fetch_latest_version", return_value=__version__):
        assert check_for_update() is None


def test_check_for_update_returns_newer_version():
    with patch("everyharness.core.update.fetch_latest_version", return_value="9.9.9"):
        assert check_for_update() == "9.9.9"


def test_check_for_update_offline_raises():
    with patch.dict(os.environ, {"EVERYHARNESS_OFFLINE": "1"}), pytest.raises(OfflineError):
        check_for_update()


def test_fetch_latest_pypi_version_handles_http_error():
    with patch("everyharness.core.update.httpx.Client") as client_cls:
        client = client_cls.return_value.__enter__.return_value
        client.get.side_effect = httpx.ConnectError("offline")
        assert fetch_latest_pypi_version() is None


def test_fetch_latest_version_offline_raises():
    with patch.dict(os.environ, {"EVERYHARNESS_OFFLINE": "1"}), pytest.raises(OfflineError):
        fetch_latest_version()


def test_upgrade_command_semver():
    assert upgrade_command("0.2.0") == "pip install 'everyharness==0.2.0'"


def test_upgrade_command_fallback():
    assert upgrade_command("0.2.0-beta") == "pip install -U everyharness"
