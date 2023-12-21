"""Test saved_views."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import SavedViewsEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import SavedView, SavedViewFilterRule


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.saved_views, SavedViewsEndpoint)
    assert not isinstance(paperless.saved_views, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["saved_views"]):
        result = await paperless.saved_views.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.saved_views.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), SavedView)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["saved_views"]):
        async for item in paperless.saved_views.iterate():
            assert isinstance(item, SavedView)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["saved_views"]["results"][0]):
        item = await paperless.saved_views.one(72)

        assert isinstance(item, SavedView)

        if isinstance(item.filter_rules, list):
            if len(item.filter_rules) > 0:
                assert isinstance(item.filter_rules.pop(), SavedViewFilterRule)
        else:
            assert False
