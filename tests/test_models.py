"""Paperless basic tests."""

import datetime
import re
from typing import Any

from aioresponses import CallbackResult, aioresponses
import pytest

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.exceptions import (
    AsnRequestError,
    DraftFieldRequired,
    PrimaryKeyRequired,
    RequestException,
    TaskNotFound,
)
from pypaperless.models import DocumentMeta, DocumentNote, DocumentNoteDraft, Page
from pypaperless.models.common import (
    DocumentMetadataType,
    DocumentSearchHitType,
    PermissionTableType,
    RetrieveFileMode,
    StatusDatabaseType,
    StatusStorageType,
    StatusTasksType,
)
from pypaperless.models.documents import DocumentSuggestions, DownloadedDocument

from . import (
    CONFIG_MAP,
    CORRESPONDENT_MAP,
    CUSTOM_FIELD_MAP,
    DOCUMENT_MAP,
    DOCUMENT_TYPE_MAP,
    GROUP_MAP,
    MAIL_ACCOUNT_MAP,
    MAIL_RULE_MAP,
    SAVED_VIEW_MAP,
    SHARE_LINK_MAP,
    STATUS_MAP,
    STORAGE_PATH_MAP,
    TAG_MAP,
    TASK_MAP,
    USER_MAP,
    WORKFLOW_MAP,
    ResourceTestMapping,
)
from .const import PAPERLESS_TEST_URL
from .data import PATCHWORK

# mypy: ignore-errors


@pytest.mark.parametrize(
    "mapping",
    [
        DOCUMENT_MAP,
        DOCUMENT_TYPE_MAP,
        CORRESPONDENT_MAP,
        CUSTOM_FIELD_MAP,
        GROUP_MAP,
        MAIL_ACCOUNT_MAP,
        MAIL_RULE_MAP,
        SAVED_VIEW_MAP,
        SHARE_LINK_MAP,
        STORAGE_PATH_MAP,
        TAG_MAP,
        USER_MAP,
        WORKFLOW_MAP,
    ],
    scope="class",
)
# test models/classifiers.py
# test models/custom_fields.py
# test models/mails.py
# test models/permissions.py
# test models/saved_views.py
# test models/share_links.py
class TestGeneralRead:
    """Read only resources test cases."""

    async def test_pages(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test pages."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        page = await anext(aiter(getattr(api_latest, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        async for item in getattr(api_latest, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_all(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test all."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        items = await getattr(api_latest, mapping.resource).all()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, int)

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(RequestException):
            await getattr(api_latest, mapping.resource)(1337)


@pytest.mark.parametrize(
    "mapping",
    [
        CORRESPONDENT_MAP,
        CUSTOM_FIELD_MAP,
        DOCUMENT_TYPE_MAP,
        SHARE_LINK_MAP,
        STORAGE_PATH_MAP,
        TAG_MAP,
    ],
    scope="class",
)
# test models/classifiers.py
# test models/custom_fields.py
# test models/share_links.py
class TestGeneralWrite:
    """R/W models test cases."""

    async def test_pages(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test pages."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        page = await anext(aiter(getattr(api_latest, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        async for item in getattr(api_latest, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_all(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test all."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        items = await getattr(api_latest, mapping.resource).all()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, int)

    async def test_reduce(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter with reduce."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        async with getattr(api_latest, mapping.resource).reduce(any_filter_param="1") as q:
            async for item in q:
                assert isinstance(item, mapping.model_cls)

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(RequestException):
            await getattr(api_latest, mapping.resource)(1337)

    async def test_create(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test create."""
        draft = getattr(api_latest, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)  # type: ignore # noqa
        # test empty draft fields
        if mapping.model_cls not in (
            SHARE_LINK_MAP.model_cls,
            CUSTOM_FIELD_MAP.model_cls,
        ):
            backup = draft.name
            draft.name = None
            with pytest.raises(DraftFieldRequired):
                await draft.save()
            draft.name = backup
        # actually call the create endpoint
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}",
            status=200,
            payload={
                "id": len(PATCHWORK[mapping.resource]["results"]),
                **draft._serialize(),  # pylint: disable=protected-access
            },
        )
        new_pk = await draft.save()
        assert new_pk >= 1

    async def test_udpate(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test update."""
        update_field = "name"
        update_value = "Name Updated"
        if mapping.model_cls is SHARE_LINK_MAP.model_cls:
            update_field = "document"
            update_value = 2
        # go on
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_update = await getattr(api_latest, mapping.resource)(1)
        setattr(to_update, update_field, update_value)
        # actually call the update endpoint
        resp.patch(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload={
                **to_update._data,  # pylint: disable=protected-access
                update_field: update_value,
            },
        )
        await to_update.update()
        assert getattr(to_update, update_field) == update_value
        # no updates
        assert not await to_update.update()
        # force update
        setattr(to_update, update_field, update_value)
        resp.put(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload={
                **to_update._data,  # pylint: disable=protected-access
                update_field: update_value,
            },
        )
        await to_update.update(only_changed=False)
        assert getattr(to_update, update_field) == update_value

    async def test_delete(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test delete."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_delete = await getattr(api_latest, mapping.resource)(1)
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await to_delete.delete()
        # test deletion failed
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=404,  # we send another status code
        )
        assert not await to_delete.delete()


@pytest.mark.parametrize(
    "mapping",
    [CONFIG_MAP],
    scope="class",
)
# test models/config.py
class TestModelConfig:
    """Config test cases."""

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(RequestException):
            await getattr(api_latest, mapping.resource)(1337)


@pytest.mark.parametrize(
    "mapping",
    [DOCUMENT_MAP],
    scope="class",
)
# test models/documents.py
class TestModelDocuments:
    """Documents test cases."""

    async def test_create(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test create."""
        draft = getattr(api_latest, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)  # type: ignore
        backup = draft.document
        draft.document = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.document = backup
        # actually call the create endpoint
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_post']}",
            status=200,
            payload="11112222-3333-4444-5555-666677778888",
        )
        await draft.save()

    async def test_udpate(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test update."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_update = await getattr(api_latest, mapping.resource)(1)
        new_title = f"{to_update.title} Updated"
        to_update.title = new_title
        # actually call the update endpoint
        resp.patch(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload={
                **to_update._data,  # pylint: disable=protected-access
                "title": new_title,
            },
        )
        await to_update.update()
        assert to_update.title == new_title

    async def test_delete(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test delete."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_delete = await getattr(api_latest, mapping.resource)(1)
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await to_delete.delete()
        # test deletion failed
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=404,  # we send another status code
        )
        assert not await to_delete.delete()

    async def test_meta(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test meta."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        document = await getattr(api_latest, mapping.resource)(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_meta']}".format(pk=1),
            status=200,
            payload=PATCHWORK["documents_metadata"],
        )
        meta = await document.get_metadata()
        assert isinstance(meta, DocumentMeta)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetadataType)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetadataType)

    async def test_files(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test files."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        document = await getattr(api_latest, mapping.resource)(1)
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_download']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment;any_filename.pdf",
            },
            body=b"Binary data: download",
        )
        download = await document.get_download()
        assert isinstance(download, DownloadedDocument)
        assert download.mode == RetrieveFileMode.DOWNLOAD
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_preview']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            headers={
                "Content-Type": "application/pdf",
            },
            body=b"Binary data: preview",
        )
        preview = await document.get_preview()
        assert isinstance(preview, DownloadedDocument)
        assert preview.mode == RetrieveFileMode.PREVIEW
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_thumbnail']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            body=b"Binary data: thumbnail",
        )
        thumbnail = await document.get_thumbnail()
        assert isinstance(thumbnail, DownloadedDocument)
        assert thumbnail.mode == RetrieveFileMode.THUMBNAIL

    async def test_suggestions(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test suggestions."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        document = await getattr(api_latest, mapping.resource)(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_suggestions']}".format(pk=1),
            status=200,
            payload=PATCHWORK["documents_suggestions"],
        )
        suggestions = await document.get_suggestions()
        assert isinstance(suggestions, DocumentSuggestions)

    async def test_get_next_an(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test get next asn."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_next_asn']}",
            status=200,
            payload=1337,
        )
        asn = await getattr(api_latest, mapping.resource).get_next_asn()
        assert isinstance(asn, int)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_next_asn']}",
            status=500,
        )
        with pytest.raises(AsnRequestError):
            await getattr(api_latest, mapping.resource).get_next_asn()

    async def test_searching(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test searching."""
        # search
        resp.get(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*query.*$"
            ),
            status=200,
            payload=PATCHWORK["documents_search"],
        )
        async for item in getattr(api_latest, mapping.resource).search("1337"):
            assert isinstance(item, mapping.model_cls)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHitType)
        # more_like
        resp.get(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*more_like_id.*$"
            ),
            status=200,
            payload=PATCHWORK["documents_search"],
        )
        async for item in getattr(api_latest, mapping.resource).more_like(1337):
            assert isinstance(item, mapping.model_cls)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHitType)

    async def test_note_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert isinstance(item, mapping.model_cls)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_notes']}".format(pk=1),
            status=200,
            payload=PATCHWORK["document_notes"],
        )
        results = await item.notes()
        assert isinstance(results, list)
        assert len(results) > 0
        for note in results:
            assert isinstance(note, DocumentNote)
            assert isinstance(note.created, datetime.datetime)
        with pytest.raises(PrimaryKeyRequired):
            item = await getattr(api_latest, mapping.resource).notes()

    async def test_note_create(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test create."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        draft = item.notes.draft(note="Test note.")
        assert isinstance(draft, DocumentNoteDraft)
        backup = draft.note
        draft.note = None
        with pytest.raises(DraftFieldRequired):
            await draft.save()
        draft.note = backup
        # actually call the create endpoint
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_notes']}".format(pk=1),
            status=200,
            payload=PATCHWORK["document_notes"],
        )
        result = await draft.save()
        assert isinstance(result, tuple)

    async def test_note_delete(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test delete."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_notes']}".format(pk=1),
            status=200,
            payload=PATCHWORK["document_notes"],
        )
        results = await item.notes()
        resp.delete(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_notes']}".format(pk=1)
                + r"\?.*$"
            ),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        deletion = await results.pop().delete()
        assert deletion


@pytest.mark.parametrize(
    "mapping",
    [STATUS_MAP],
    scope="class",
)
# test models/status.py
class TestModelStatus:
    """Status test cases."""

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}",
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        status = await getattr(api_latest, mapping.resource)()
        assert status
        assert isinstance(status, mapping.model_cls)
        assert isinstance(status.storage, StatusStorageType)
        assert isinstance(status.database, StatusDatabaseType)
        assert isinstance(status.tasks, StatusTasksType)


@pytest.mark.parametrize(
    "mapping",
    [TASK_MAP],
    scope="class",
)
# test models/tasks.py
class TestModelTasks:
    """Tasks test cases."""

    async def test_iter(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r".*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        async for item in getattr(api_latest, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        # by pk
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # by uuid
        resp.get(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?task_id.*$"
            ),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        item = await getattr(api_latest, mapping.resource)("dummy-found")
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as pk doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(RequestException):
            await getattr(api_latest, mapping.resource)(1337)
        # must raise as task_id doesn't exist
        resp.get(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?task_id.*$"
            ),
            status=200,
            payload=[],
        )
        with pytest.raises(TaskNotFound):
            await getattr(api_latest, mapping.resource)("dummy-not-found")


@pytest.mark.parametrize(
    "mapping",
    [
        CORRESPONDENT_MAP,
        DOCUMENT_MAP,
        DOCUMENT_TYPE_MAP,
        STORAGE_PATH_MAP,
        TAG_MAP,
    ],
    scope="class",
)
# test models/classifiers.py
class TestPermissionModels:
    """Permissions test cases."""

    async def test_permissions(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test permissions."""
        getattr(api_latest, mapping.resource).request_permissions = True
        assert getattr(api_latest, mapping.resource).request_permissions
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            payload={
                **PATCHWORK[mapping.resource]["results"][0],
                "permissions": PATCHWORK["object_permissions"],
            },
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item.has_permissions
        assert isinstance(item.permissions, PermissionTableType)

    async def test_permission_change(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test permission changes."""
        getattr(api_latest, mapping.resource).request_permissions = True
        assert getattr(api_latest, mapping.resource).request_permissions
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            payload={
                **PATCHWORK[mapping.resource]["results"][0],
                "permissions": PATCHWORK["object_permissions"],
            },
        )
        item = await getattr(api_latest, mapping.resource)(1)
        item.permissions.view.users.append(23)

        def _lookup_set_permissions(
            url: str,  # noqa
            json: dict[str, Any],
            **kwargs,  # pylint: disable=unused-argument # noqa
        ):
            assert "set_permissions" in json
            return CallbackResult(
                status=200,
                payload=item._data,  # pylint: disable=protected-access
            )

        resp.patch(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource+'_single']}".format(pk=1)
                + r"\?.*$"
            ),
            callback=_lookup_set_permissions,
        )
        await item.update()
