"""Test documents."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import DocumentsEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.api.documents import (
    DocumentFilesService,
    DocumentNotesService,
    _get_document_id_helper,
)
from pypaperless.models import (
    Document,
    DocumentMetadata,
    DocumentMetaInformation,
    DocumentNote,
    DocumentNotePost,
)
from pypaperless.models.custom_fields import CustomFieldValue
from pypaperless.util import dataclass_from_dict


@pytest.fixture(scope="module")
def document_dataset(data):
    """Represent document data."""
    return data["documents"]


@pytest.fixture(scope="module")
def notes_dataset(data):
    """Represent notes data."""
    return data["document_notes"]


@pytest.fixture(scope="module")
def meta_dataset(data):
    """Represent notes data."""
    return data["document_metadata"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.documents, DocumentsEndpoint)
    assert isinstance(paperless.documents, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, document_dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=document_dataset):
        result = await paperless.documents.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.documents.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), Document)


async def test_iterate(paperless: Paperless, document_dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=document_dataset):
        async for item in paperless.documents.iterate():
            assert isinstance(item, Document)


async def test_one(paperless: Paperless, document_dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=document_dataset["results"][0]):
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


async def test_id_helper(document_dataset):
    """Test helper function."""
    data = document_dataset["results"][1]  # document id 226
    item = dataclass_from_dict(Document, data)

    assert isinstance(item, Document)

    id_pk = _get_document_id_helper(item.id)
    id_obj = _get_document_id_helper(item)

    assert id_pk == id_obj


async def test_notes_service(paperless: Paperless, document_dataset, notes_dataset):
    """Test notes service."""
    data = document_dataset["results"][1]  # document id 226
    item = dataclass_from_dict(Document, data)

    assert isinstance(item, Document)
    assert len(item.notes) > 0

    assert isinstance(paperless.documents.notes, DocumentNotesService)

    # test notes.get
    with patch.object(paperless, "request_json", return_value=notes_dataset):
        # get by pk and by object
        notes = await paperless.documents.notes.get(item.id)
        notes_by_item = await paperless.documents.notes.get(item)

    assert isinstance(notes, list)
    assert isinstance(notes[0], DocumentNote)

    # notes by pk and object must be the same
    assert notes == notes_by_item

    # lets test if making data even is working correctly
    # check tests/fixtures/data.json for structural diffs in data
    # check DocumentNotesService@pypaperless/api/documents.py for reviewing the ETL
    assert item.notes == notes

    # test notes.create
    new = DocumentNotePost(
        note="Sample note 4.",
        document=item.id,
    )
    with patch.object(paperless, "request_json"):
        await paperless.documents.notes.create(new)  # nothing will happen, no returns

    # test notes.delete
    note = notes.pop()
    with patch.object(paperless, "request_json"):
        await paperless.documents.notes.delete(note)  # nothing will happen, no returns


async def test_files_service(paperless: Paperless, document_dataset):
    """Test files service."""
    data = document_dataset["results"][1]  # document id 226
    item = dataclass_from_dict(Document, data)

    assert isinstance(item, Document)

    assert isinstance(paperless.documents.files, DocumentFilesService)

    example_file = bytes("This is a file.", "utf-8")

    # test all
    with patch.object(paperless, "request_file", return_value=example_file):
        download = await paperless.documents.files.download(item)
        preview = await paperless.documents.files.preview(item)
        thumbnail = await paperless.documents.files.thumb(item)

    # well...
    assert download == preview == thumbnail


async def test_metadata(paperless: Paperless, document_dataset, meta_dataset):
    """Test metadata."""
    data = document_dataset["results"][1]  # document id 226
    item = dataclass_from_dict(Document, data)

    assert isinstance(item, Document)

    with patch.object(paperless, "request_json", return_value=meta_dataset):
        meta = await paperless.documents.meta(item.id)
        meta_by_item = await paperless.documents.meta(item)

    # results by pk and object must be the same
    assert meta == meta_by_item

    assert isinstance(meta, DocumentMetaInformation)

    assert isinstance(meta.original_metadata, list)
    assert isinstance(meta.archive_metadata, list)
    assert isinstance(meta.archive_metadata.pop(), DocumentMetadata)

    assert meta.original_filename is None
