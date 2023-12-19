"""Test tasks."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import EndpointCUDMixin, TasksEndpoint
from pypaperless.models import Task
from pypaperless.models.shared import TaskStatus


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.tasks, TasksEndpoint)
    assert not isinstance(paperless.tasks, EndpointCUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["tasks"]):
        result = await paperless.tasks.list()

        # tasks have no list-all attribute...
        # TODO: we have to do something with it
        assert result is None

        tasks = await paperless.tasks.get()

        assert isinstance(tasks[0], Task)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["tasks"]):
        async for item in paperless.tasks.iterate():
            assert isinstance(item, Task)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["tasks"]):
        item = await paperless.tasks.one("bd2de639-5ecd-4bc1-ab3d-106908ef00e1")

        assert isinstance(item, Task)
        assert isinstance(item.status, TaskStatus)
