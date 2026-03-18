"""Tests for resource services: Config, Version, Profile, Statistics, Status, Tasks, Trash."""

import re

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.exceptions import TaskNotFoundError
from pypaperless.models import (
    Config,
    Document,
    Profile,
    Status,
    Task,
)
from pypaperless.models.types import (
    StatisticDocumentFileTypeCount,
    StatusDatabase,
    StatusStorage,
    StatusTasks,
)
from pypaperless.services.workflows import WorkflowActionService, WorkflowTriggerService

from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_CONFIG,
    DATA_PROFILE,
    DATA_REMOTE_VERSION,
    DATA_STATISTICS,
    DATA_STATUS,
    DATA_TASKS,
    DATA_TRASH,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


async def test_config_call(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """config() fetches the singleton Config without requiring a pk."""
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['config_single']}".format(pk=1),
        status_code=200,
        json=DATA_CONFIG[0],
    )
    item = await paperless.config()
    assert item
    assert isinstance(item, Config)


# ---------------------------------------------------------------------------
# Remote version
# ---------------------------------------------------------------------------


async def test_remote_version_call(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """remote_version() returns version string and update_available flag."""
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['remote_version']}",
        status_code=200,
        json=DATA_REMOTE_VERSION,
    )
    remote_version = await paperless.remote_version()
    assert remote_version
    assert isinstance(remote_version.version, str)
    assert isinstance(remote_version.update_available, bool)


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


async def test_profile_call(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """profile() returns a Profile with expected field types."""
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['profile']}",
        status_code=200,
        json=DATA_PROFILE,
    )
    profile = await paperless.profile()
    assert profile
    assert isinstance(profile, Profile)
    assert isinstance(profile.email, str)
    assert isinstance(profile.auth_token, str)
    assert isinstance(profile.has_usable_password, bool)
    assert isinstance(profile.is_mfa_enabled, bool)
    assert isinstance(profile.social_accounts, list)


async def test_profile_update(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """profile.update() PATCHes the profile and returns the updated model."""
    updated = {**DATA_PROFILE, "first_name": "Patched", "last_name": "User"}
    httpx_mock.add_response(
        method="PATCH",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['profile']}",
        status_code=200,
        json=updated,
    )
    profile = await paperless.profile.update(first_name="Patched", last_name="User")
    assert isinstance(profile, Profile)
    assert profile.first_name == "Patched"
    assert profile.last_name == "User"


async def test_profile_update_email(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """profile.update(email=) PATCHes only the email field."""
    updated = {**DATA_PROFILE, "email": "new@example.com"}
    httpx_mock.add_response(
        method="PATCH",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['profile']}",
        status_code=200,
        json=updated,
    )
    profile = await paperless.profile.update(email="new@example.com")
    assert isinstance(profile, Profile)
    assert profile.email == "new@example.com"


async def test_profile_update_password(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """profile.update(password=) PATCHes only the password field."""
    httpx_mock.add_response(
        method="PATCH",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['profile']}",
        status_code=200,
        json=DATA_PROFILE,
    )
    profile = await paperless.profile.update(password="s3cr3t")  # noqa: S106
    assert isinstance(profile, Profile)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


async def test_statistics_call(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """statistics() returns typed statistics with document file type counts."""
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['statistics']}",
        status_code=200,
        json=DATA_STATISTICS,
    )
    stats = await paperless.statistics()
    assert stats
    assert isinstance(stats.character_count, int)
    assert isinstance(stats.document_file_type_counts, list)
    for item in stats.document_file_type_counts:
        assert isinstance(item, StatisticDocumentFileTypeCount)


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


async def test_status_call(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """status() returns a Status with typed sub-objects."""
    httpx_mock.add_response(
        method="GET",
        url=f"{PAPERLESS_TEST_URL}{API_PATH['status']}",
        status_code=200,
        json=DATA_STATUS,
    )
    status = await paperless.status()
    assert status
    assert isinstance(status, Status)
    assert isinstance(status.storage, StatusStorage)
    assert isinstance(status.database, StatusDatabase)
    assert isinstance(status.tasks, StatusTasks)


async def test_status_has_errors(paperless: Paperless) -> None:
    """Status.has_errors is True when any component is in ERROR state."""
    data = {
        "database": {"status": "OK"},
        "tasks": {
            "redis_status": "OK",
            "celery_status": "OK",
            "classifier_status": "OK",
        },
    }
    status = Status.from_data(paperless, data=data)
    assert status.has_errors is False

    data["database"]["status"] = "ERROR"
    status = Status.from_data(paperless, data=data)
    assert status.has_errors is True

    # None values are treated as no errors
    del data["database"]["status"]
    status = Status.from_data(paperless, data=data)
    assert status.has_errors is False


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------


class TestTasks:
    """Task service: iteration, filter, single fetch by pk and uuid."""

    async def test_iter(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Iterating over tasks yields Task instances."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r".*$"),
            status_code=200,
            json=DATA_TASKS,
        )
        async for item in paperless.tasks:
            assert isinstance(item, Task)

    async def test_filter(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks.filter() passes kwargs as query params."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?.*status.*$"),
            status_code=200,
            json=DATA_TASKS,
        )
        async for item in paperless.tasks.filter(status="SUCCESS"):
            assert isinstance(item, Task)

    async def test_call_by_pk(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks(pk) fetches by primary key."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1),
            status_code=200,
            json=DATA_TASKS[0],
        )
        item = await paperless.tasks(1)
        assert item
        assert isinstance(item, Task)

    async def test_call_by_uuid(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks(uuid) fetches by task UUID."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status_code=200,
            json=DATA_TASKS,
        )
        item = await paperless.tasks("dummy-found")
        assert item
        assert isinstance(item, Task)

    async def test_call_pk_not_found(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks(unknown_pk) raises HTTPStatusError."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1337),
            status_code=404,
        )
        with pytest.raises(httpx.HTTPStatusError):
            await paperless.tasks(1337)

    async def test_call_uuid_not_found(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks(unknown_uuid) raises TaskNotFoundError."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status_code=200,
            json=[],
        )
        with pytest.raises(TaskNotFoundError):
            await paperless.tasks("dummy-not-found")


# ---------------------------------------------------------------------------
# Workflows
# ---------------------------------------------------------------------------


async def test_workflow_sub_services(paperless: Paperless) -> None:
    """workflows.actions and workflows.triggers are the expected service types."""
    assert isinstance(paperless.workflows.actions, WorkflowActionService)
    assert isinstance(paperless.workflows.triggers, WorkflowTriggerService)


# ---------------------------------------------------------------------------
# Trash
# ---------------------------------------------------------------------------


class TestTrash:
    """Trash service: iteration, restore, and empty operations."""

    async def test_iter(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Iterating over trash yields Document instances with deleted_at set."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['trash']}" + r"\?.*$"),
            status_code=200,
            json=DATA_TRASH,
        )
        items = [item async for item in paperless.trash]
        assert len(items) == len(DATA_TRASH["results"])
        for item in items:
            assert isinstance(item, Document)
            assert item.deleted_at is not None

    async def test_restore(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """restore() POSTs to the trash endpoint."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "restored"},
        )
        await paperless.trash.restore([100, 101])

    async def test_empty(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """empty() empties all or specific documents from the trash."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "emptied"},
        )
        await paperless.trash.empty()

        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "emptied"},
        )
        await paperless.trash.empty([100])
