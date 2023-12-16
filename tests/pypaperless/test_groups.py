"""Test groups."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import EndpointCUDMixin, GroupsEndpoint, PaginatedResult
from pypaperless.models import Group


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.groups, GroupsEndpoint)
    assert not isinstance(paperless.groups, EndpointCUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["groups"]):
        result = await paperless.groups.list()

        assert isinstance(result, list)
        assert len(result) > 0

        page = await paperless.groups.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Group)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["groups"]["results"][0]):
        item = await paperless.groups.one(72)

        assert isinstance(item, Group)
