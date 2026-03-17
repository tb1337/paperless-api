"""Tests for the CLI commands."""

import json
import re

import httpx as _httpx
import pytest
from click.testing import CliRunner
from pytest_httpx import HTTPXMock

from pypaperless.cli import cli
from pypaperless.const import API_PATH

from .const import PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL
from .data import (
    DATA_PROFILE,
    DATA_REMOTE_VERSION,
    DATA_SCHEMA,
    DATA_STATUS,
    DATA_TAGS,
    DATA_TASKS,
)

# Common CLI args for explicit credentials
_ARGS = ["--url", PAPERLESS_TEST_URL, "--token", PAPERLESS_TEST_TOKEN]


def _mock_init(httpx_mock: HTTPXMock) -> None:
    """Add a successful initialization response."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=200,
        json=DATA_SCHEMA,
    )


# ── help / smoke ──────────────────────────────────────────────────────────────


def test_cli_help() -> None:
    """--help returns exit code 0 and shows usage."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "pypaperless" in result.output.lower()


def test_cli_subcommand_help() -> None:
    """Tags --help shows list and get subcommands."""
    runner = CliRunner()
    result = runner.invoke(cli, ["tags", "--help"])
    assert result.exit_code == 0
    assert "list" in result.output
    assert "get" in result.output


def test_cli_list_subcommand_help() -> None:
    """Tags list --help shows --limit option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["tags", "list", "--help"])
    assert result.exit_code == 0
    assert "--limit" in result.output


# ── status ────────────────────────────────────────────────────────────────────


def test_cli_status(httpx_mock: HTTPXMock) -> None:
    """Status outputs host_version, api_version, status and remote_version keys."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['status']}",
        method="GET",
        status_code=200,
        json=DATA_STATUS,
    )
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['remote_version']}",
        method="GET",
        status_code=200,
        json=DATA_REMOTE_VERSION,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "status"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "host_version" in data
    assert "api_version" in data
    assert "status" in data
    assert "remote_version" in data


# ── profile ───────────────────────────────────────────────────────────────────


def test_cli_profile(httpx_mock: HTTPXMock) -> None:
    """Profile outputs user profile as JSON."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['profile']}",
        method="GET",
        status_code=200,
        json=DATA_PROFILE,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "profile"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["email"] == DATA_PROFILE["email"]


# ── resource list ─────────────────────────────────────────────────────────────


def test_cli_tags_list(httpx_mock: HTTPXMock) -> None:
    """Tags list returns a JSON array of all tag items."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['tags']}") + r"(\?.*)?$"),
        method="GET",
        status_code=200,
        json=DATA_TAGS,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert isinstance(items, list)
    assert len(items) == len(DATA_TAGS["results"])


def test_cli_tags_list_limit(httpx_mock: HTTPXMock) -> None:
    """Tags list --limit 1 returns exactly 1 item."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['tags']}") + r"(\?.*)?$"),
        method="GET",
        status_code=200,
        json=DATA_TAGS,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list", "--limit", "1"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 1


# ── resource get ──────────────────────────────────────────────────────────────


def test_cli_tags_get(httpx_mock: HTTPXMock) -> None:
    """Tags get <id> returns a single tag as JSON."""
    _mock_init(httpx_mock)
    tag_data = DATA_TAGS["results"][0]
    tag_id = tag_data["id"]
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['tags_single']}".format(pk=tag_id),
        method="GET",
        status_code=200,
        json=tag_data,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "get", str(tag_id)])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["id"] == tag_id


def test_cli_tasks_get_by_string_id(httpx_mock: HTTPXMock) -> None:
    """Tasks get accepts a string (UUID) as the task id argument."""
    _mock_init(httpx_mock)
    # tasks.filter() is called for string IDs
    task_data = DATA_TASKS[0]
    task_uuid = task_data["task_id"]
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}",
        method="GET",
        match_params={"task_id": task_uuid},
        status_code=200,
        json=[task_data],
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tasks", "get", task_uuid])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["task_id"] == task_uuid


# ── env var configuration ─────────────────────────────────────────────────────


def test_cli_env_credentials(httpx_mock: HTTPXMock, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI reads PYPAPERLESS_URL + PYPAPERLESS_TOKEN from the environment."""
    monkeypatch.setenv("PYPAPERLESS_URL", PAPERLESS_TEST_URL)
    monkeypatch.setenv("PYPAPERLESS_TOKEN", PAPERLESS_TEST_TOKEN)
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['tags']}") + r"(\?.*)?$"),
        method="GET",
        status_code=200,
        json=DATA_TAGS,
    )

    runner = CliRunner()
    # No --url / --token options — should pick up from env
    result = runner.invoke(cli, ["tags", "list"])
    assert result.exit_code == 0, result.output
    assert isinstance(json.loads(result.output), list)


# ── error handling ────────────────────────────────────────────────────────────


def test_cli_connection_error(httpx_mock: HTTPXMock) -> None:
    """CLI reports a clean error on connection failure."""
    httpx_mock.add_exception(
        _httpx.ConnectError("refused"),
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list"])
    assert result.exit_code != 0
    assert "Connection error" in result.output


def test_cli_invalid_token(httpx_mock: HTTPXMock) -> None:
    """CLI reports a clean error on 401 Unauthorized."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=401,
        text="Unauthorized",
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list"])
    assert result.exit_code != 0
    assert "token" in result.output.lower()


def test_cli_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI raises a config error when no URL is configured at all."""
    monkeypatch.delenv("PYPAPERLESS_URL", raising=False)
    monkeypatch.delenv("PYPAPERLESS_TOKEN", raising=False)

    runner = CliRunner()
    result = runner.invoke(cli, ["tags", "list"])
    assert result.exit_code != 0
    assert "Configuration error" in result.output
