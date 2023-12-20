"""Test document_types."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import DocumentTypesEndpoint, EnableCRUDMixin, PaginatedResult
from pypaperless.models import DocumentType
from pypaperless.models.shared import MatchingAlgorithm


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.document_types, DocumentTypesEndpoint)
    assert isinstance(paperless.document_types, EnableCRUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["document_types"]):
        result = await paperless.document_types.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.document_types.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), DocumentType)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["document_types"]):
        async for item in paperless.document_types.iterate():
            assert isinstance(item, DocumentType)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["document_types"]["results"][0]):
        item = await paperless.document_types.one(72)

        assert isinstance(item, DocumentType)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
