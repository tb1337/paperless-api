"""Paperless basic tests."""

import datetime
import re

import aiohttp
import pytest
from aioresponses import aioresponses

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.exceptions import (
    AsnRequestError,
    DraftFieldRequiredError,
    PrimaryKeyRequiredError,
    SendEmailError,
    TaskNotFoundError,
)
from pypaperless.models import (
    Config,
    CustomField,
    Document,
    DocumentDraft,
    DocumentMeta,
    DocumentNote,
    DocumentNoteDraft,
    Status,
    Task,
)
from pypaperless.models.common import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldBooleanValue,
    CustomFieldDocumentLinkValue,
    CustomFieldValue,
    DocumentMetadataType,
    DocumentSearchHitType,
    RetrieveFileMode,
    StatisticDocumentFileTypeCount,
    StatusDatabaseType,
    StatusStorageType,
    StatusTasksType,
)
from pypaperless.models.documents import (
    DocumentCustomFieldList,
    DocumentSuggestions,
    DownloadedDocument,
)
from pypaperless.models.workflows import WorkflowActionHelper, WorkflowTriggerHelper

from . import DOCUMENT_MAP
from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_CONFIG,
    DATA_CUSTOM_FIELDS,
    DATA_DOCUMENT_METADATA,
    DATA_DOCUMENT_NOTES,
    DATA_DOCUMENT_SUGGESTIONS,
    DATA_DOCUMENTS,
    DATA_DOCUMENTS_SEARCH,
    DATA_REMOTE_VERSION,
    DATA_STATISTICS,
    DATA_STATUS,
    DATA_TASKS,
)

# mypy: ignore-errors


# test models/config.py
class TestModelConfig:
    """Config test cases."""

    async def test_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['config_single']}".format(pk=1),
            status=200,
            payload=DATA_CONFIG[0],
        )
        item = await paperless.config(1)
        assert item
        assert isinstance(item, Config)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['config_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(aiohttp.ClientResponseError):
            await paperless.config(1337)


# test models/documents.py
class TestModelDocuments:
    """Documents test cases."""

    async def test_lazy(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test laziness."""
        document = Document(paperless, data={"id": 1})
        assert not document.is_fetched

        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        await document.load()
        assert document.is_fetched

    async def test_create(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test create."""
        defaults = DOCUMENT_MAP.draft_defaults or {}
        draft = paperless.documents.draft(**defaults)
        assert isinstance(draft, DocumentDraft)
        backup = draft.document
        draft.document = None
        with pytest.raises(DraftFieldRequiredError):
            await draft.save()
        draft.document = backup
        # actually call the create endpoint
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_post']}",
            status=200,
            payload="11112222-3333-4444-5555-666677778888",
        )
        await draft.save()

    async def test_create_date_property(self, paperless: Paperless) -> None:
        """Test create_date property - well, lol."""
        document = Document.create_with_data(
            paperless, data={**DATA_DOCUMENTS["results"][0]}, fetched=True
        )
        assert document.created_date == document.created

    async def test_udpate(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test update."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        to_update = await paperless.documents(1)
        new_title = f"{to_update.title} Updated"
        to_update.title = new_title
        # actually call the update endpoint
        resp.patch(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload={
                **to_update._data,  # pylint: disable=protected-access
                "title": new_title,
            },
        )
        await to_update.update()
        assert to_update.title == new_title

    async def test_delete(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test delete."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        to_delete = await paperless.documents(1)
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await to_delete.delete()
        # test deletion failed
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=404,  # we send another status code
        )
        assert not await to_delete.delete()

    async def test_meta(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test meta."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_meta']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENT_METADATA,
        )
        meta = await document.get_metadata()
        assert isinstance(meta, DocumentMeta)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetadataType)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetadataType)

    async def test_files(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test files."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_download']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment;filename=any_filename.pdf",
            },
            body=b"Binary data: download",
        )
        download = await document.get_download()
        assert isinstance(download, DownloadedDocument)
        assert download.mode == RetrieveFileMode.DOWNLOAD
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_preview']}".format(pk=1)
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
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_thumbnail']}".format(pk=1)
                + r"\?.*$"
            ),
            status=200,
            body=b"Binary data: thumbnail",
        )
        thumbnail = await document.get_thumbnail()
        assert isinstance(thumbnail, DownloadedDocument)
        assert thumbnail.mode == RetrieveFileMode.THUMBNAIL

    async def test_suggestions(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test suggestions."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_suggestions']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENT_SUGGESTIONS,
        )
        suggestions = await document.get_suggestions()
        assert isinstance(suggestions, DocumentSuggestions)

    async def test_get_next_an(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test get next asn."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status=200,
            payload=1337,
        )
        asn = await paperless.documents.get_next_asn()
        assert isinstance(asn, int)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status=500,
        )
        with pytest.raises(AsnRequestError):
            await paperless.documents.get_next_asn()

    async def test_searching(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test searching."""
        # search
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents']}" + r"\?.*query.*$"),
            status=200,
            payload=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.search("1337"):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHitType)
        # more_like
        resp.get(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents']}" + r"\?.*more_like_id.*$"
            ),
            status=200,
            payload=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.more_like(1337):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHitType)

    async def test_note_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        assert isinstance(item, Document)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENT_NOTES,
        )
        results = await item.notes()
        assert isinstance(results, list)
        assert len(results) > 0
        for note in results:
            assert isinstance(note, DocumentNote)
            assert isinstance(note.created, datetime.datetime)
        with pytest.raises(PrimaryKeyRequiredError):
            item = await paperless.documents.notes()

    async def test_note_create(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test create."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        draft = item.notes.draft(note="Test note.")
        assert isinstance(draft, DocumentNoteDraft)
        backup = draft.note
        draft.note = None
        with pytest.raises(DraftFieldRequiredError):
            await draft.save()
        draft.note = backup
        # actually call the create endpoint
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENT_NOTES,
        )
        result = await draft.save()
        assert isinstance(result, tuple)

    async def test_note_delete(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test delete."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status=200,
            payload=DATA_DOCUMENT_NOTES,
        )
        results = await item.notes()
        resp.delete(
            re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1) + r"\?.*$"
            ),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        deletion = await results.pop().delete()
        assert deletion

    async def test_custom_field_list_wo_cache(
        self, resp: aioresponses, paperless: Paperless
    ) -> None:
        """Test custom field list without cache."""
        # request document
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status=200,
            payload=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)

        # every item MUST NOT be a derived CustomFieldValue instance
        for field in item.custom_fields:
            for value_type in CUSTOM_FIELD_TYPE_VALUE_MAP.values():
                assert not isinstance(field, value_type)
            assert isinstance(field, CustomFieldValue)

    async def test_custom_field_list_wslash_cache(
        self, resp: aioresponses, paperless: Paperless
    ) -> None:
        """Test custom fields list with cache."""
        # set custom fields cache
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['custom_fields']}" + r"\?.*$"),
            status=200,
            payload=DATA_CUSTOM_FIELDS,
        )
        paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

        # request document
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status=200,
            payload=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)

        # every item may be a derived class or not
        for field in item.custom_fields:
            assert isinstance(field, CustomFieldValue)

        # test if custom field is in document custom field values
        test_cf = CustomField.create_with_data(
            api=paperless,
            data=DATA_CUSTOM_FIELDS["results"][0],
            fetched=True,
        )
        assert test_cf in item.custom_fields
        assert isinstance(item.custom_fields.get(test_cf), CustomFieldValue)
        assert item.custom_fields.default(test_cf) is not None
        assert item.custom_fields.default(-1337) is None

        # test typed getters
        assert isinstance(
            item.custom_fields.get(test_cf, CustomFieldDocumentLinkValue),
            CustomFieldDocumentLinkValue,
        )
        assert isinstance(
            item.custom_fields.default(test_cf, CustomFieldDocumentLinkValue),
            CustomFieldDocumentLinkValue,
        )
        with pytest.raises(TypeError):
            item.custom_fields.get(test_cf, CustomFieldBooleanValue)
        with pytest.raises(TypeError):
            item.custom_fields.default(test_cf, CustomFieldBooleanValue)

        # test remove field value
        item.custom_fields -= test_cf
        assert test_cf not in item.custom_fields

        # test add field value
        item.custom_fields += test_cf.draft_value(1337)
        assert test_cf in item.custom_fields

    async def test_email(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test sending emails."""
        # successful email sending
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['documents_email']}",
            status=200,
            payload={"message": "Email sent"},
        )
        await paperless.documents.email(
            documents=1,
            addresses="test@example.org",
            subject="Test Email",
            message="Test Message",
        )

        # unsuccessful email sending
        resp.post(f"{PAPERLESS_TEST_URL}{API_PATH['documents_email']}", status=400)
        with pytest.raises(SendEmailError):
            await paperless.documents.email(
                documents=[1, 2],
                addresses="test@example.org",
                subject="Test Email",
                message="Test Message",
            )


# test models/remote_version.py
class TestModelVersion:
    """Version test cases."""

    async def test_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['remote_version']}",
            status=200,
            payload=DATA_REMOTE_VERSION,
        )
        remote_version = await paperless.remote_version()
        assert remote_version
        assert isinstance(remote_version.version, str)
        assert isinstance(remote_version.update_available, bool)


# test models/statistics.py
class TestModelStatistics:
    """Statistics test cases."""

    async def test_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['statistics']}",
            status=200,
            payload=DATA_STATISTICS,
        )
        stats = await paperless.statistics()
        assert stats
        assert isinstance(stats.character_count, int)
        assert isinstance(stats.document_file_type_counts, list)
        for item in stats.document_file_type_counts:
            assert isinstance(item, StatisticDocumentFileTypeCount)


# test models/status.py
class TestModelStatus:
    """Status test cases."""

    async def test_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['status']}",
            status=200,
            payload=DATA_STATUS,
        )
        status = await paperless.status()
        assert status
        assert isinstance(status, Status)
        assert isinstance(status.storage, StatusStorageType)
        assert isinstance(status.database, StatusDatabaseType)
        assert isinstance(status.tasks, StatusTasksType)

    async def test_has_errors(self, paperless: Paperless) -> None:
        """Test has errors."""
        data = {
            "database": {
                "status": "OK",
            },
            "tasks": {
                "redis_status": "OK",
                "celery_status": "OK",
                "classifier_status": "OK",
            },
        }

        # everything fine as we initialized Status with OK values only
        status = Status.create_with_data(paperless, data=data, fetched=True)
        assert status.has_errors is False

        # lets set something to ERROR
        data["database"]["status"] = "ERROR"
        status = Status.create_with_data(paperless, data=data, fetched=True)
        assert status.has_errors is True

        # assume any status value is None; None values are treated as no errors
        del data["database"]["status"]
        status = Status.create_with_data(paperless, data=data, fetched=True)
        assert status.has_errors is False


# test models/tasks.py
class TestModelTasks:
    """Tasks test cases."""

    async def test_iter(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test iter."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r".*$"),
            status=200,
            payload=DATA_TASKS,
        )
        async for item in paperless.tasks:
            assert isinstance(item, Task)

    async def test_call(self, resp: aioresponses, paperless: Paperless) -> None:
        """Test call."""
        # by pk
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1),
            status=200,
            payload=DATA_TASKS[0],
        )
        item = await paperless.tasks(1)
        assert item
        assert isinstance(item, Task)
        # by uuid
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status=200,
            payload=DATA_TASKS,
        )
        item = await paperless.tasks("dummy-found")
        assert item
        assert isinstance(item, Task)
        # must raise as pk doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(aiohttp.ClientResponseError):
            await paperless.tasks(1337)
        # must raise as task_id doesn't exist
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status=200,
            payload=[],
        )
        with pytest.raises(TaskNotFoundError):
            await paperless.tasks("dummy-not-found")


# test models/workflows.py
class TestModelWorkflows:
    """Tasks test cases."""

    async def test_helpers(self, paperless: Paperless) -> None:
        """Test helpers."""
        assert isinstance(paperless.workflows.actions, WorkflowActionHelper)
        assert isinstance(paperless.workflows.triggers, WorkflowTriggerHelper)
