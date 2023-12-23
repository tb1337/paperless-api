"""Test document_types."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import DocumentTypesEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import DocumentType
from pypaperless.models.shared import MatchingAlgorithm


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["document_types"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.document_types, DocumentTypesEndpoint)
    assert isinstance(paperless.document_types, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.document_types.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.document_types.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), DocumentType)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.document_types.iterate():
            assert isinstance(item, DocumentType)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.document_types.one(72)

        assert isinstance(item, DocumentType)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
