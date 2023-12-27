"""Test users."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.controllers import UsersController
from pypaperless.controllers.base import CreateMixin, DeleteMixin, ResultPage, UpdateMixin
from pypaperless.models import User


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["users"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.users, UsersController)
    assert not isinstance(paperless.users, CreateMixin | UpdateMixin | DeleteMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.users.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.users.get()

        assert isinstance(page, ResultPage)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), User)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.users.iterate():
            assert isinstance(item, User)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.users.one(72)

        assert isinstance(item, User)
