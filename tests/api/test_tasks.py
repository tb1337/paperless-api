"""Test tasks."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import TasksEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin
from pypaperless.models import Task
from pypaperless.models.shared import TaskStatus


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["tasks"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.tasks, TasksEndpoint)
    assert not isinstance(paperless.tasks, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.tasks.list()

        assert isinstance(result, list)
        assert len(result) == 0

        tasks = await paperless.tasks.get()

        assert isinstance(tasks[0], Task)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.tasks.iterate():
            assert isinstance(item, Task)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset):
        item = await paperless.tasks.one("bd2de639-5ecd-4bc1-ab3d-106908ef00e1")

        assert isinstance(item, Task)
        assert isinstance(item.status, TaskStatus)
