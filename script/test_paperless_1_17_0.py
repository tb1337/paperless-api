"""Paperless v1.17.0 tests."""

from datetime import datetime

from pypaperless import Paperless
from pypaperless.const import PaperlessFeature
from pypaperless.controllers import DocumentsController
from pypaperless.models import Document, DocumentNote, DocumentNotePost


class TestBeginPaperless:
    """Paperless v1.17.0 test cases."""

    async def test_init(self, api_117: Paperless):
        """Test init."""
        assert api_117._token
        assert api_117._request_opts
        assert not api_117._session
        # test properties
        assert api_117.url
        assert api_117.is_initialized

    async def test_features(self, api_117: Paperless):
        """Test features."""
        # basic class has no features
        assert PaperlessFeature.CONTROLLER_STORAGE_PATHS in api_117.features
        assert PaperlessFeature.FEATURE_DOCUMENT_NOTES in api_117.features
        assert api_117.storage_paths
        assert not api_117.consumption_templates
        assert not api_117.custom_fields
        assert not api_117.share_links
        assert not api_117.workflows
        assert not api_117.workflow_actions
        assert not api_117.workflow_triggers


class TestDocumentNotes:
    """Document Notes test cases."""

    async def test_controller(self, api_117: Paperless):
        """Test controller."""
        assert isinstance(api_117.documents, DocumentsController)
        # test services
        assert api_117.documents.notes

    async def test_document_one(self, api_117: Paperless):
        """Test document one (notes edition)."""
        item = await api_117.documents.one(2)
        assert isinstance(item, Document)
        assert len(item.notes) > 0
        for note in item.notes:
            assert isinstance(note, DocumentNote)
            assert isinstance(note.created, datetime)

    async def test_get(self, api_117: Paperless):
        """Test get."""
        pk = 2
        results = await api_117.documents.notes.get(pk)
        assert isinstance(results, list)
        assert len(results) > 0
        for item in results:
            assert isinstance(item, DocumentNote)
            # Paperless fakes the pk on this endpoint, lets test
            # Read more about that in pypaperless/controllers/documents.py - DocumentNotesService
            assert item.document == pk

    async def test_create(self, api_117: Paperless):
        """Test create."""
        pk = 2
        to_create = DocumentNotePost(
            note="Sample text.",
            document=pk,
        )
        # there are no returns, just test if something fails
        # the fake PaperlessAPI won't even setup a new object
        await api_117.documents.notes.create(to_create)

    async def test_delete(self, api_117: Paperless):
        """Test delete."""
        pk = 2
        results = await api_117.documents.notes.get(pk)
        assert isinstance(results, list)
        assert len(results) > 0
        # there are no returns, just test if something fails
        # the fake PaperlessAPI won't even setup a new object
        await api_117.documents.notes.delete(results.pop())
