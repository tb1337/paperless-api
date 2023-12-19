"""Test documents."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import DocumentsEndpoint, EndpointCUDMixin, PaginatedResult
from pypaperless.models import Document, DocumentNote
from pypaperless.models.custom_fields import CustomFieldValue


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.documents, DocumentsEndpoint)
    assert isinstance(paperless.documents, EndpointCUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["documents"]):
        result = await paperless.documents.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.documents.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Document)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["documents"]):
        async for item in paperless.documents.iterate():
            assert isinstance(item, Document)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["documents"]["results"][0]):
        item = await paperless.documents.one(72)

        assert isinstance(item, Document)

        if isinstance(item.notes, list):
            if len(item.notes) > 0:
                assert isinstance(item.notes.pop(), DocumentNote)
        else:
            assert False

        if isinstance(item.custom_fields, list):
            if len(item.custom_fields) > 0:
                assert isinstance(item.custom_fields.pop(), CustomFieldValue)
        else:
            assert False
