"""Paperless v1.17.0 tests."""

import datetime

import pytest

from pypaperless import Paperless, PaperlessSession
from pypaperless.exceptions import DraftFieldRequired
from pypaperless.models import documents as doc_helpers
from pypaperless.models.documents import DocumentNote, DocumentNoteDraft
from pypaperless.models.mixins import models as model_mixins

from . import DOCUMENT_MAP, ResourceTestMapping

# mypy: ignore-errors
# pylint: disable=protected-access,redefined-outer-name


@pytest.fixture(scope="function")
async def p(api_117) -> Paperless:
    """Yield version for this test case."""
    yield api_117


# test api.py with extra document notes endpoint
class TestBeginPaperless:
    """Paperless v1.8.0 test cases."""

    async def test_init(self, p: Paperless):
        """Test init."""
        assert isinstance(p._session, PaperlessSession)
        assert p.host_version == "1.17.0"
        assert p.is_initialized
        assert isinstance(p.local_resources, set)
        assert isinstance(p.remote_resources, set)

    async def test_resources(self, p: Paperless):
        """Test resources."""
        assert p.correspondents.is_available
        assert not p.custom_fields.is_available
        assert p.document_types.is_available
        assert p.documents.is_available
        assert p.groups.is_available
        assert p.mail_accounts.is_available
        assert p.mail_rules.is_available
        assert p.saved_views.is_available
        assert not p.share_links.is_available
        assert p.storage_paths.is_available
        assert p.tags.is_available
        assert p.users.is_available
        assert not p.workflows.is_available


@pytest.mark.parametrize(
    "mapping",
    [DOCUMENT_MAP],
    scope="class",
)
# test models/documents.py
class TestDocumentNotes:
    """Document Notes test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert isinstance(getattr(p, mapping.resource).notes, doc_helpers.DocumentNoteHelper)

    async def test_model(
        self, mapping: ResourceTestMapping  # pylint: disable=unused-argument # noqa ARG002
    ):
        """Test model."""
        assert model_mixins.DeletableMixin not in DocumentNote.__bases__
        assert model_mixins.MatchingFieldsMixin not in DocumentNote.__bases__
        assert model_mixins.PermissionFieldsMixin not in DocumentNote.__bases__
        assert model_mixins.UpdatableMixin not in DocumentNote.__bases__
        assert model_mixins.CreatableMixin in DocumentNoteDraft.__bases__

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        item = await getattr(p, mapping.resource)(1)
        assert isinstance(item, mapping.model_cls)
        results = await item.notes()
        assert isinstance(results, list)
        assert len(results) > 0
        for note in results:
            assert isinstance(note, DocumentNote)
            assert isinstance(note.created, datetime.datetime)

    async def test_create(self, p: Paperless, mapping: ResourceTestMapping):
        """Test create."""
        item = await getattr(p, mapping.resource)(1)
        draft = item.notes.draft(note="Test note.")
        assert isinstance(draft, DocumentNoteDraft)
        backup = draft.note
        draft.note = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.note = backup
        # actually call the create endpoint
        result = await draft.save()
        assert isinstance(result, tuple)

    async def test_delete(self, p: Paperless, mapping: ResourceTestMapping):
        """Test delete."""
        item = await getattr(p, mapping.resource)(1)
        results = await item.notes()
        assert isinstance(results, list)
        assert len(results) > 0
        # there are no returns, just test if something fails
        # the fake PaperlessAPI won't even setup a new object
        deletion = await results.pop().delete()
        assert deletion
