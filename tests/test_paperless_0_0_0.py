"""Paperless basic tests."""

import pytest

from pypaperless import Paperless, PaperlessSession
from pypaperless.const import PaperlessResource
from pypaperless.exceptions import DraftFieldRequired, RequestException, TaskNotFound
from pypaperless.models import DocumentMeta, Page
from pypaperless.models import documents as doc_helpers
from pypaperless.models.common import DocumentMetadataType, RetrieveFileMode
from pypaperless.models.documents import DownloadedDocument
from pypaperless.models.mixins import helpers as helper_mixins
from pypaperless.models.mixins import models as model_mixins

from . import (
    CORRESPONDENT_MAP,
    DOCUMENT_MAP,
    DOCUMENT_TYPE_MAP,
    GROUP_MAP,
    MAIL_ACCOUNT_MAP,
    MAIL_RULE_MAP,
    SAVED_VIEW_MAP,
    TAG_MAP,
    TASK_MAP,
    USER_MAP,
    ResourceTestMapping,
)

# mypy: ignore-errors
# pylint: disable=protected-access,redefined-outer-name


@pytest.fixture(scope="function")
async def p(api_00) -> Paperless:
    """Yield version for this test case."""
    yield api_00


# test api.py with legacy endpoint
class TestBeginPaperless:
    """Common Paperless test cases."""

    async def test_init(self, p: Paperless):
        """Test init."""
        assert isinstance(p._session, PaperlessSession)
        assert p.host_version == "0.0.0"
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
        assert not p.storage_paths.is_available
        assert p.tags.is_available
        assert p.users.is_available
        assert not p.workflows.is_available


@pytest.mark.parametrize(
    "mapping",
    [CORRESPONDENT_MAP, DOCUMENT_TYPE_MAP, TAG_MAP],
    scope="class",
)
# test models/classifiers.py
class TestClassifiers:
    """Classifiers test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin in mapping.helper_cls.__bases__

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        assert model_mixins.DeletableMixin in mapping.model_cls.__bases__
        assert model_mixins.MatchingFieldsMixin in mapping.model_cls.__bases__
        assert model_mixins.PermissionFieldsMixin in mapping.model_cls.__bases__
        assert model_mixins.UpdatableMixin in mapping.model_cls.__bases__
        assert model_mixins.CreatableMixin in mapping.draft_cls.__bases__

    async def test_pages(self, p: Paperless, mapping: ResourceTestMapping):
        """Test pages."""
        page = await anext(aiter(getattr(p, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter."""
        async for item in getattr(p, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_reduce(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter with reduce."""
        async with getattr(p, mapping.resource).reduce(any_filter_param="1") as q:
            async for item in q:
                assert isinstance(item, mapping.model_cls)

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        item = await getattr(p, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(1337)

    async def test_create(self, p: Paperless, mapping: ResourceTestMapping):
        """Test create."""
        draft = getattr(p, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)
        backup = draft.name
        draft.name = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.name = backup
        # actually call the create endpoint
        assert await draft.save() >= 1

    async def test_udpate(self, p: Paperless, mapping: ResourceTestMapping):
        """Test update."""
        to_update = await getattr(p, mapping.resource)(5)
        new_name = f"{to_update.name} Updated"
        to_update.name = new_name
        await to_update.update()
        assert to_update.name == new_name
        # force update
        new_name = f"{to_update.name} again"
        to_update.name = new_name
        await to_update.update(only_changed=False)
        assert to_update.name == new_name

    async def test_delete(self, p: Paperless, mapping: ResourceTestMapping):
        """Test delete."""
        to_delete = await getattr(p, mapping.resource)(5)
        assert await to_delete.delete()
        # must raise as we deleted 5
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(5)


@pytest.mark.parametrize(
    "mapping",
    [GROUP_MAP, MAIL_ACCOUNT_MAP, MAIL_RULE_MAP, SAVED_VIEW_MAP, USER_MAP],
    scope="class",
)
# test models/mails.py
# test models/permissions.py
# test models/saved_views.py
class TestReadOnly:
    """Read only resources test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin not in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin in mapping.helper_cls.__bases__

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        assert model_mixins.DeletableMixin not in mapping.model_cls.__bases__
        assert model_mixins.MatchingFieldsMixin not in mapping.model_cls.__bases__
        assert model_mixins.UpdatableMixin not in mapping.model_cls.__bases__

        perms = model_mixins.PermissionFieldsMixin in mapping.model_cls.__bases__
        if mapping.resource in (PaperlessResource.GROUPS, PaperlessResource.USERS):
            assert not perms
        else:
            assert perms

    async def test_pages(self, p: Paperless, mapping: ResourceTestMapping):
        """Test pages."""
        page = await anext(aiter(getattr(p, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter."""
        async for item in getattr(p, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        item = await getattr(p, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(1337)


@pytest.mark.parametrize(
    "mapping",
    [TASK_MAP],
    scope="class",
)
# test models/tasks.py
class TestTasks:
    """Tasks test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin not in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin not in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin not in mapping.helper_cls.__bases__

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        assert model_mixins.DeletableMixin not in mapping.model_cls.__bases__
        assert model_mixins.MatchingFieldsMixin not in mapping.model_cls.__bases__
        assert model_mixins.PermissionFieldsMixin not in mapping.model_cls.__bases__
        assert model_mixins.UpdatableMixin not in mapping.model_cls.__bases__

    async def test_iter(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter."""
        async for item in getattr(p, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        # by pk
        item = await getattr(p, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # by uuid
        item = await getattr(p, mapping.resource)("abcdef12-3456-7890-abcd-ef1234567890")
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(1337)
        # must raise as abcdef doesn't exist
        with pytest.raises(TaskNotFound):
            await getattr(p, mapping.resource)("abcdef")


@pytest.mark.parametrize(
    "mapping",
    [DOCUMENT_MAP],
    scope="class",
)
# test models/documents.py
class TestDocuments:
    """Documents test cases."""

    async def test_helper(self, p: Paperless, mapping: ResourceTestMapping):
        """Test helper."""
        assert hasattr(p, mapping.resource)
        assert isinstance(getattr(p, mapping.resource), mapping.helper_cls)
        assert helper_mixins.CallableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.DraftableMixin in mapping.helper_cls.__bases__
        assert helper_mixins.IterableMixin in mapping.helper_cls.__bases__
        # test sub helpers
        assert isinstance(p.documents.download, doc_helpers.DocumentFileDownloadHelper)
        assert isinstance(p.documents.metadata, doc_helpers.DocumentMetaHelper)
        assert isinstance(p.documents.preview, doc_helpers.DocumentFilePreviewHelper)
        assert isinstance(p.documents.thumbnail, doc_helpers.DocumentFileThumbnailHelper)

    async def test_model(self, mapping: ResourceTestMapping):
        """Test model."""
        assert model_mixins.DeletableMixin in mapping.model_cls.__bases__
        assert model_mixins.MatchingFieldsMixin not in mapping.model_cls.__bases__
        assert model_mixins.PermissionFieldsMixin in mapping.model_cls.__bases__
        assert model_mixins.UpdatableMixin in mapping.model_cls.__bases__
        assert model_mixins.CreatableMixin in mapping.draft_cls.__bases__

    async def test_pages(self, p: Paperless, mapping: ResourceTestMapping):
        """Test pages."""
        page = await anext(aiter(getattr(p, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(self, p: Paperless, mapping: ResourceTestMapping):
        """Test iter."""
        async for item in getattr(p, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_call(self, p: Paperless, mapping: ResourceTestMapping):
        """Test call."""
        item = await getattr(p, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(1337)

    async def test_create(self, p: Paperless, mapping: ResourceTestMapping):
        """Test create."""
        draft = getattr(p, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)
        backup = draft.document
        draft.document = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.document = backup
        # actually call the create endpoint
        task_id = await draft.save()
        # get the task
        assert isinstance(task_id, str)
        task = await p.tasks(task_id)
        assert task.related_document
        # get the document
        created = await getattr(p, mapping.resource)(task.related_document)
        assert isinstance(created, mapping.model_cls)
        assert created.tags.count(1) == 1
        assert created.tags.count(2) == 1
        assert created.tags.count(3) == 1

    async def test_udpate(self, p: Paperless, mapping: ResourceTestMapping):
        """Test update."""
        to_update = await getattr(p, mapping.resource)(2)
        new_title = f"{to_update.title} Updated"
        to_update.title = new_title
        await to_update.update()
        assert to_update.title == new_title

    async def test_delete(self, p: Paperless, mapping: ResourceTestMapping):
        """Test delete."""
        to_delete = await getattr(p, mapping.resource)(2)
        assert await to_delete.delete()
        # must raise as we deleted 2
        with pytest.raises(RequestException):
            await getattr(p, mapping.resource)(2)

    async def test_meta(self, p: Paperless, mapping: ResourceTestMapping):
        """Test meta."""
        document = await getattr(p, mapping.resource)(1)
        meta = await document.get_metadata()
        assert isinstance(meta, DocumentMeta)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetadataType)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetadataType)

    async def test_files(self, p: Paperless, mapping: ResourceTestMapping):
        """Test files."""
        document = await getattr(p, mapping.resource)(1)
        download = await document.get_download()
        assert isinstance(download, DownloadedDocument)
        assert download.mode == RetrieveFileMode.DOWNLOAD
        preview = await document.get_preview()
        assert isinstance(preview, DownloadedDocument)
        assert preview.mode == RetrieveFileMode.PREVIEW
        thumbnail = await document.get_thumbnail()
        assert isinstance(thumbnail, DownloadedDocument)
        assert thumbnail.mode == RetrieveFileMode.THUMBNAIL
