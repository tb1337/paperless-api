"""Test custom_fields."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import CustomFieldEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import CustomField
from pypaperless.models.shared import CustomFieldType


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["custom_fields"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.custom_fields, CustomFieldEndpoint)
    assert isinstance(paperless.custom_fields, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.custom_fields.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.custom_fields.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), CustomField)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.custom_fields.iterate():
            assert isinstance(item, CustomField)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.custom_fields.one(72)

        assert isinstance(item, CustomField)
        assert isinstance(item.data_type, CustomFieldType)
