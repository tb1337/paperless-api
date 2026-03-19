"""Tests for resource services: Config, Version, Profile, Statistics, Status, Tasks, Trash."""

import re

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.builders import SearchQuery
from pypaperless.const import API_PATH
from pypaperless.exceptions import TaskNotFoundError
from pypaperless.models import (
    Config,
    Document,
    MailAccount,
    Profile,
    SearchResult,
    Status,
    Task,
)
from pypaperless.models.mixins.securable import Permissions
from pypaperless.models.types import (
    StatisticDocumentFileTypeCount,
    StatusDatabase,
    StatusStorage,
    StatusTasks,
)
from pypaperless.services.workflows import WorkflowActionService, WorkflowTriggerService

from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_BULK_EDIT_OBJECTS,
    DATA_CONFIG,
    DATA_MAIL_ACCOUNTS,
    DATA_PROFILE,
    DATA_REMOTE_VERSION,
    DATA_SEARCH,
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

    async def test_acknowledge(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks.acknowledge([...]) POSTs and returns acknowledged count."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_acknowledge']}",
            status_code=200,
            json={"result": 1},
        )
        result = await paperless.tasks.acknowledge([1])
        assert result == 1

    async def test_run(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """tasks.run(task_id) POSTs and returns a Task."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_run']}",
            status_code=200,
            json=DATA_TASKS[0],
        )
        item = await paperless.tasks.run(DATA_TASKS[0]["task_id"])
        assert isinstance(item, Task)

    async def test_model_acknowledge_shortcut(
        self,
        httpx_mock: HTTPXMock,
        paperless: Paperless,
    ) -> None:
        """Task.acknowledge() delegates to tasks.acknowledge([self.id])."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1),
            status_code=200,
            json=DATA_TASKS[0],
        )
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_acknowledge']}",
            status_code=200,
            json={"result": 1},
        )
        task = await paperless.tasks(1)
        assert isinstance(task, Task)
        result = await task.acknowledge()
        assert result == 1

    async def test_model_run_shortcut(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Task.run() delegates to tasks.run(self.task_id)."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1),
            status_code=200,
            json=DATA_TASKS[0],
        )
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_run']}",
            status_code=200,
            json=DATA_TASKS[0],
        )
        task = await paperless.tasks(1)
        assert isinstance(task, Task)
        rerun = await task.run()
        assert isinstance(rerun, Task)


# ---------------------------------------------------------------------------
# Mail Accounts
# ---------------------------------------------------------------------------


class TestMailAccounts:
    """Mail account service action endpoints."""

    async def test_test(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """mail_accounts.test() POSTs to the endpoint and returns JSON."""
        payload = {"success": True}
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['mail_accounts_test']}",
            status_code=200,
            json=payload,
        )
        response = await paperless.mail_accounts.test()
        assert response == payload

    async def test_process(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """mail_accounts.process(pk) POSTs to the account process endpoint."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['mail_accounts_process']}".format(pk=1),
            status_code=200,
            json={"result": "ok"},
        )
        await paperless.mail_accounts.process(1)

    async def test_model_process_shortcut(
        self,
        httpx_mock: HTTPXMock,
        paperless: Paperless,
    ) -> None:
        """MailAccount.process() delegates to mail_accounts.process(self.id)."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['mail_accounts_single']}".format(pk=1),
            status_code=200,
            json=DATA_MAIL_ACCOUNTS["results"][0],
        )
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['mail_accounts_process']}".format(pk=1),
            status_code=200,
            json={"result": "ok"},
        )
        account = await paperless.mail_accounts(1)
        assert isinstance(account, MailAccount)
        await account.process()


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


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestSearch:
    """Global search service: query and db_only flag."""

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """search('query') returns a SearchResult with documents."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['search']}" + r".*$"),
            status_code=200,
            json=DATA_SEARCH,
        )
        result = await paperless.search("invoice")
        assert isinstance(result, SearchResult)
        assert result.total == DATA_SEARCH["total"]
        assert result.documents is not None
        assert len(result.documents) == len(DATA_SEARCH["documents"])

    async def test_call_with_db_only(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """search('query', db_only=True) passes db_only param and returns SearchResult."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['search']}" + r".*db_only.*$"),
            status_code=200,
            json=DATA_SEARCH,
        )
        result = await paperless.search("invoice", db_only=True)
        assert isinstance(result, SearchResult)
        assert result.total == DATA_SEARCH["total"]

    async def test_call_with_builder(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """search(SearchQuery(...)) converts the builder to a string automatically."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['search']}" + r".*$"),
            status_code=200,
            json=DATA_SEARCH,
        )
        q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
        result = await paperless.search(q)
        assert isinstance(result, SearchResult)
        assert result.total == DATA_SEARCH["total"]


# ---------------------------------------------------------------------------
# BulkEditObjects
# ---------------------------------------------------------------------------


class TestBulkEditObjects:
    """BulkEditObjects service: set_permissions and delete operations."""

    async def test_set_permissions(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """set_permissions() POSTs the correct payload and returns None."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['bulk_edit_objects']}",
            status_code=200,
            json=DATA_BULK_EDIT_OBJECTS,
        )
        perms = Permissions(view_users=[2], change_users=[1])
        result = await paperless.bulk_edit_objects.set_permissions(
            "tags",
            [1, 2, 3],
            owner=1,
            permissions=perms,
        )
        assert result is None

        request = httpx_mock.get_requests()[-1]
        body = __import__("json").loads(request.content)
        assert body["object_type"] == "tags"
        assert body["operation"] == "set_permissions"
        assert body["objects"] == [1, 2, 3]
        assert body["owner"] == 1
        assert "permissions" in body

    async def test_set_permissions_no_optional_fields(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """set_permissions() without owner/permissions omits those keys."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['bulk_edit_objects']}",
            status_code=200,
            json=DATA_BULK_EDIT_OBJECTS,
        )
        await paperless.bulk_edit_objects.set_permissions("correspondents", [7])

        request = httpx_mock.get_requests()[-1]
        body = __import__("json").loads(request.content)
        assert "owner" not in body
        assert "permissions" not in body
        assert body["merge"] is False

    async def test_delete(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """delete() POSTs the correct payload and returns None."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['bulk_edit_objects']}",
            status_code=200,
            json=DATA_BULK_EDIT_OBJECTS,
        )
        result = await paperless.bulk_edit_objects.delete("document_types", [10, 11])
        assert result is None

        request = httpx_mock.get_requests()[-1]
        body = __import__("json").loads(request.content)
        assert body["object_type"] == "document_types"
        assert body["operation"] == "delete"
        assert body["objects"] == [10, 11]
