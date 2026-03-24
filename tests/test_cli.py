"""Tests for the CLI commands."""

import json
import re
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import httpx as _httpx
import pytest
from click.testing import CliRunner
from pytest_httpx import HTTPXMock

import pypaperless.cli as cli_module
from pypaperless.cli import _out, _render_compact_list, _resource_group, cli
from pypaperless.const import API_PATH

from .const import PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL
from .data import (
    DATA_PROFILE,
    DATA_REMOTE_VERSION,
    DATA_SCHEMA,
    DATA_SEARCH,
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
    """Tags list returns a structured ID/name console table."""
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
    assert "ID" in result.output
    assert "Name" in result.output
    assert DATA_TAGS["results"][0]["name"] in result.output


def test_cli_tags_list_limit(httpx_mock: HTTPXMock) -> None:
    """Tags list --limit 1 prints exactly one data row."""
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
    lines = [line for line in result.output.splitlines() if line.strip()]
    data_lines = lines[2:]
    assert len(data_lines) == 1


def test_cli_tags_json(httpx_mock: HTTPXMock) -> None:
    """Tags json returns a JSON array of all tag items."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['tags']}") + r"(\?.*)?$"),
        method="GET",
        status_code=200,
        json=DATA_TAGS,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "json"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert isinstance(items, list)
    assert len(items) == len(DATA_TAGS["results"])


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
    result = runner.invoke(cli, ["tags", "json"])
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


def test_cli_forbidden_error(httpx_mock: HTTPXMock) -> None:
    """CLI reports 'Access denied' when the server returns 403."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=403,
        text="Forbidden",
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list"])
    assert result.exit_code != 0
    assert "Access denied" in result.output


def test_cli_initialization_error(httpx_mock: HTTPXMock) -> None:
    """CLI reports 'Initialization failed' when the server returns 500 during init."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=500,
        text="Internal Server Error",
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "list"])
    assert result.exit_code != 0
    assert "Initialization failed" in result.output


# ── json --limit ──────────────────────────────────────────────────────────────


def test_cli_tags_json_limit(httpx_mock: HTTPXMock) -> None:
    """Tags json --limit 1 returns exactly one item."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['tags']}") + r"(\?.*)?$"),
        method="GET",
        status_code=200,
        json=DATA_TAGS,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "tags", "json", "--limit", "1"])
    assert result.exit_code == 0, result.output
    items = json.loads(result.output)
    assert len(items) == 1


# ── _render_compact_list unit tests ──────────────────────────────────────────


def test_render_compact_list_no_name_key(capsys: pytest.CaptureFixture[str]) -> None:
    """_render_compact_list renders item with id only when no name-like key exists."""
    # Item has no name/title/username/task_id/slug — row_name stays ""
    _render_compact_list([SimpleNamespace(id=42)])
    out = capsys.readouterr().out
    assert "42" in out


def test_render_compact_list_fallback_key(capsys: pytest.CaptureFixture[str]) -> None:
    """_render_compact_list falls back to the first key that is not None or empty."""
    # name=None forces the loop to continue; title provides the value
    _render_compact_list([SimpleNamespace(id=1, name=None, title="My Title")])
    out = capsys.readouterr().out
    assert "My Title" in out


# ── _out unit tests ───────────────────────────────────────────────────────────


def test_out_pygments_highlight(monkeypatch: pytest.MonkeyPatch) -> None:
    """_out uses pygments highlight when stdout is a TTY and pygments is available."""
    if not cli_module._PYGMENTS:
        pytest.skip("pygments not installed")

    mock_stdout = MagicMock()
    mock_stdout.isatty.return_value = True
    monkeypatch.setattr(sys, "stdout", mock_stdout)

    captured: list[str] = []
    monkeypatch.setattr(cli_module.click, "echo", captured.append)

    _out({"key": "value"})
    assert len(captured) == 1
    assert "key" in captured[0]


# ── _resource_group factory ───────────────────────────────────────────────────


def test_cli_resource_group_no_list() -> None:
    """_resource_group with supports_list=False omits list and json subcommands."""
    grp = _resource_group("test", "tags", supports_list=False)
    commands = set(grp.commands or {})
    assert "list" not in commands
    assert "json" not in commands
    assert "get" in commands


def test_cli_search_plain(httpx_mock: HTTPXMock) -> None:
    """Search command outputs total and section headings for non-empty results (L180-192)."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['search']}") + r".*$"),
        method="GET",
        status_code=200,
        json=DATA_SEARCH,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "search", "invoice"])
    assert result.exit_code == 0, result.output
    assert "Total matches" in result.output
    assert str(DATA_SEARCH["total"]) in result.output


def test_cli_search_json(httpx_mock: HTTPXMock) -> None:
    """Search --json outputs the full SearchResult as a JSON object (L183)."""
    _mock_init(httpx_mock)
    httpx_mock.add_response(
        url=re.compile(r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['search']}") + r".*$"),
        method="GET",
        status_code=200,
        json=DATA_SEARCH,
    )

    runner = CliRunner()
    result = runner.invoke(cli, [*_ARGS, "search", "--json", "invoice"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "total" in data
