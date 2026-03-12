"""Paperless basic tests."""

import datetime
import re

import httpx
import pytest
from pytest_httpx import HTTPXMock

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
    DocumentCustomFieldList,
    DocumentDraft,
    DocumentHistory,
    DocumentHistoryAction,
    DocumentMeta,
    DocumentNote,
    DocumentNoteDraft,
    DocumentSuggestions,
    DownloadedDocument,
    Status,
    Task,
)
from pypaperless.models.types import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldBooleanValue,
    CustomFieldDocumentLinkValue,
    CustomFieldIntegerValue,
    CustomFieldStringValue,
    CustomFieldValue,
    DocumentMetaEntry,
    DocumentSearchHit,
    FileRetrieveMode,
    StatisticDocumentFileTypeCount,
    StatusDatabase,
    StatusStorage,
    StatusTasks,
)
from pypaperless.services.workflows import WorkflowActionService, WorkflowTriggerService

from . import DOCUMENT_MAP
from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_CONFIG,
    DATA_CUSTOM_FIELDS,
    DATA_DOCUMENT_HISTORY,
    DATA_DOCUMENT_METADATA,
    DATA_DOCUMENT_NOTES,
    DATA_DOCUMENT_SUGGESTIONS,
    DATA_DOCUMENTS,
    DATA_DOCUMENTS_SEARCH,
    DATA_REMOTE_VERSION,
    DATA_STATISTICS,
    DATA_STATUS,
    DATA_TASKS,
    DATA_TRASH,
)

# mypy: ignore-errors


# test models/config.py
class TestModelConfig:
    """Config test cases."""

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['config_single']}".format(pk=1),
            status_code=200,
            json=DATA_CONFIG[0],
        )
        item = await paperless.config(1)
        assert item
        assert isinstance(item, Config)
        # must raise as 1337 doesn't exist
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['config_single']}".format(pk=1337),
            status_code=404,
        )
        with pytest.raises(httpx.HTTPStatusError):
            await paperless.config(1337)


# test models/documents.py
class TestModelDocuments:
    """Documents test cases."""

    async def test_lazy(self, paperless: Paperless) -> None:
        """Test laziness."""
        document = await paperless.documents(42, lazy=True)
        assert document.id == 42
        assert document.title is None

    async def test_create(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test create."""
        defaults = DOCUMENT_MAP.draft_defaults or {}
        draft = paperless.documents.draft(**defaults)
        assert isinstance(draft, DocumentDraft)
        backup = draft.document
        draft.document = None
        with pytest.raises(DraftFieldRequiredError):
            await paperless.documents.save(draft)
        draft.document = backup
        # actually call the create endpoint
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_post']}",
            status_code=200,
            json="11112222-3333-4444-5555-666677778888",
        )
        await paperless.documents.save(draft)

    async def test_create_date_property(self, paperless: Paperless) -> None:
        """Test create_date property - well, lol."""
        document = Document.create_with_data(paperless, data={**DATA_DOCUMENTS["results"][0]})
        assert document.created_date == document.created

    async def test_udpate(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test update."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        to_update = await paperless.documents(1)
        new_title = f"{to_update.title} Updated"
        to_update.title = new_title
        # actually call the update endpoint
        httpx_mock.add_response(
            method="PATCH",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json={
                **to_update._data,
                "title": new_title,
            },
        )
        await paperless.documents.update(to_update)
        assert to_update.title == new_title

    async def test_delete(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test delete."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        to_delete = await paperless.documents(1)
        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await paperless.documents.delete(to_delete)
        # test deletion failed
        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=404,  # we send another status code
        )
        assert not await paperless.documents.delete(to_delete)

    async def test_meta(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test meta."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_meta']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_METADATA,
        )
        meta = await document.get_metadata()
        assert isinstance(meta, DocumentMeta)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetaEntry)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetaEntry)

    async def test_files(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test files."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_download']}".format(pk=1)
                + r"\?.*$"
            ),
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment;filename=any_filename.pdf",
            },
            content=b"Binary data: download",
        )
        download = await document.get_download()
        assert isinstance(download, DownloadedDocument)
        assert download.mode == FileRetrieveMode.DOWNLOAD
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_preview']}".format(pk=1)
                + r"\?.*$"
            ),
            status_code=200,
            headers={
                "Content-Type": "application/pdf",
            },
            content=b"Binary data: preview",
        )
        preview = await document.get_preview()
        assert isinstance(preview, DownloadedDocument)
        assert preview.mode == FileRetrieveMode.PREVIEW
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH['documents_thumbnail']}".format(pk=1)
                + r"\?.*$"
            ),
            status_code=200,
            content=b"Binary data: thumbnail",
        )
        thumbnail = await document.get_thumbnail()
        assert isinstance(thumbnail, DownloadedDocument)
        assert thumbnail.mode == FileRetrieveMode.THUMBNAIL

    async def test_suggestions(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test suggestions."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        document = await paperless.documents(1)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_suggestions']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_SUGGESTIONS,
        )
        suggestions = await document.get_suggestions()
        assert isinstance(suggestions, DocumentSuggestions)

    async def test_get_next_an(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test get next asn."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status_code=200,
            json=1337,
        )
        asn = await paperless.documents.get_next_asn()
        assert isinstance(asn, int)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status_code=500,
        )
        with pytest.raises(AsnRequestError):
            await paperless.documents.get_next_asn()

    async def test_searching(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test searching."""
        # search
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents']}" + r"\?.*query.*$"),
            status_code=200,
            json=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.search("1337"):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHit)
        # custom_field_query
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents']}" + r"\?.*custom_field_query.*$"
            ),
            status_code=200,
            json=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.search(custom_field_query="1337"):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHit)
        # more_like
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents']}" + r"\?.*more_like_id.*$"
            ),
            status_code=200,
            json=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.more_like(1337):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHit)

    async def test_note_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        assert isinstance(item, Document)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_NOTES,
        )
        results = await item.notes()
        assert isinstance(results, list)
        assert len(results) > 0
        for note in results:
            assert isinstance(note, DocumentNote)
            assert isinstance(note.created, datetime.datetime)
        with pytest.raises(PrimaryKeyRequiredError):
            item = await paperless.documents.notes()

    async def test_note_create(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test create."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        draft = item.notes.draft(note="Test note.")
        assert isinstance(draft, DocumentNoteDraft)
        backup = draft.note
        draft.note = None
        with pytest.raises(DraftFieldRequiredError):
            await item.notes.save(draft)
        draft.note = backup
        # actually call the create endpoint
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_NOTES,
        )
        result = await item.notes.save(draft)
        assert isinstance(result, tuple)

    async def test_note_delete(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test delete."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_NOTES,
        )
        results = await item.notes()
        httpx_mock.add_response(
            method="DELETE",
            url=re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1) + r"\?.*$"
            ),
            status_code=204,  # Paperless-ngx responds with 204 on deletion
        )
        deletion = await item.notes.delete(results.pop())
        assert deletion

    async def test_history_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test history endpoint via document property and service directly."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents_history']}".format(pk=1) + r".*$"
            ),
            status_code=200,
            json=DATA_DOCUMENT_HISTORY,
        )
        results = await item.history()
        assert isinstance(results, list)
        assert len(results) == len(DATA_DOCUMENT_HISTORY)
        for entry in results:
            assert isinstance(entry, DocumentHistory)
            assert entry.document == item.id
            assert isinstance(entry.timestamp, datetime.datetime)
            assert isinstance(entry.action, DocumentHistoryAction)
            assert isinstance(entry.changes, dict)

        # direct service call
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['documents_history']}".format(pk=1) + r".*$"
            ),
            status_code=200,
            json=DATA_DOCUMENT_HISTORY,
        )
        results_direct = await paperless.documents.history(1)
        assert isinstance(results_direct, list)
        assert len(results_direct) == len(DATA_DOCUMENT_HISTORY)

        # missing pk raises error
        with pytest.raises(PrimaryKeyRequiredError):
            await paperless.documents.history()

    async def test_custom_field_list_wo_cache(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Test custom field list without cache."""
        # request document
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status_code=200,
            json=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)

        # every item MUST NOT be a derived CustomFieldValue instance
        for field in item.custom_fields:
            for value_type in CUSTOM_FIELD_TYPE_VALUE_MAP.values():
                assert not isinstance(field, value_type)
            assert isinstance(field, CustomFieldValue)

    async def test_custom_field_list_wslash_cache(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Test custom fields list with cache."""
        # set custom fields cache
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['custom_fields']}" + r"\?.*$"),
            status_code=200,
            json=DATA_CUSTOM_FIELDS,
        )
        paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

        # request document
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status_code=200,
            json=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)

        # every item may be a derived class or not
        for field in item.custom_fields:
            assert isinstance(field, CustomFieldValue)

        # test if custom field is in document custom field values
        test_cf = CustomField.create_with_data(
            client=paperless,
            data=DATA_CUSTOM_FIELDS["results"][0],
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

    async def test_draft_custom_fields_as_id_list(self, paperless: Paperless) -> None:
        """Test DocumentDraft serialises list[int] custom_fields as repeated form values."""
        draft = paperless.documents.draft(
            document=b"pdf",
            custom_fields=[1, 3, 5],
        )
        serialized = draft.serialize()
        assert serialized["form"]["custom_fields"] == [1, 3, 5]

    async def test_draft_custom_fields_as_object_mapping(self, paperless: Paperless) -> None:
        """Test DocumentDraft serialises DocumentCustomFieldList as a JSON string."""
        import json  # noqa: PLC0415

        cf = DocumentCustomFieldList(paperless, [])
        cf += CustomFieldStringValue(field=6, value="hello")
        cf += CustomFieldIntegerValue(field=3, value=42)

        draft = paperless.documents.draft(document=b"pdf")
        draft.custom_fields = cf

        serialized = draft.serialize()
        raw = serialized["form"]["custom_fields"]
        # Must be a JSON-encoded string, not a plain list
        assert isinstance(raw, str)
        decoded = json.loads(raw)
        assert isinstance(decoded, dict)
        assert decoded["6"] == "hello"
        assert decoded["3"] == 42

    async def test_draft_custom_fields_object_mapping_upload(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Test that a draft with a DocumentCustomFieldList can actually be POSTed."""
        import json  # noqa: PLC0415

        cf = DocumentCustomFieldList(paperless, [])
        cf += CustomFieldStringValue(field=6, value="smoke")

        draft = paperless.documents.draft(document=b"%PDF-fake", title="CF Mapping Test")
        draft.custom_fields = cf

        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_post']}",
            status_code=200,
            json="aaaabbbb-cccc-dddd-eeee-ffffffffffff",
        )
        task_id = await paperless.documents.save(draft)
        assert task_id == "aaaabbbb-cccc-dddd-eeee-ffffffffffff"

        # Verify the HTTP request that was sent contained valid JSON in custom_fields
        request = httpx_mock.get_request(method="POST")
        assert request is not None
        body = request.content.decode(errors="replace")
        assert '"field": 6' in body or '"field":6' in body or "field" in body
        # custom_fields value in multipart body must be parseable JSON array
        import re  # noqa: PLC0415

        match = re.search(r'name="custom_fields"\r\n\r\n(\{.*?\})\r\n', body, re.DOTALL)
        assert match is not None, f"custom_fields not found as JSON object in body: {body!r}"
        decoded = json.loads(match.group(1))
        assert decoded == {"6": "smoke"}

    async def test_email(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test sending emails."""
        # successful email sending
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_email']}",
            status_code=200,
            json={"message": "Email sent"},
        )
        await paperless.documents.email(
            documents=1,
            addresses="test@example.org",
            subject="Test Email",
            message="Test Message",
        )

        # unsuccessful email sending
        httpx_mock.add_response(
            method="POST", url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_email']}", status_code=400
        )
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

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['remote_version']}",
            status_code=200,
            json=DATA_REMOTE_VERSION,
        )
        remote_version = await paperless.remote_version()
        assert remote_version
        assert isinstance(remote_version.version, str)
        assert isinstance(remote_version.update_available, bool)


# test models/statistics.py
class TestModelStatistics:
    """Statistics test cases."""

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['statistics']}",
            status_code=200,
            json=DATA_STATISTICS,
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

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['status']}",
            status_code=200,
            json=DATA_STATUS,
        )
        status = await paperless.status()
        assert status
        assert isinstance(status, Status)
        assert isinstance(status.storage, StatusStorage)
        assert isinstance(status.database, StatusDatabase)
        assert isinstance(status.tasks, StatusTasks)

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
        status = Status.create_with_data(paperless, data=data)
        assert status.has_errors is False

        # lets set something to ERROR
        data["database"]["status"] = "ERROR"
        status = Status.create_with_data(paperless, data=data)
        assert status.has_errors is True

        # assume any status value is None; None values are treated as no errors
        del data["database"]["status"]
        status = Status.create_with_data(paperless, data=data)
        assert status.has_errors is False


# test models/tasks.py
class TestModelTasks:
    """Tasks test cases."""

    async def test_iter(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test iter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r".*$"),
            status_code=200,
            json=DATA_TASKS,
        )
        async for item in paperless.tasks:
            assert isinstance(item, Task)

    async def test_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test call."""
        # by pk
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1),
            status_code=200,
            json=DATA_TASKS[0],
        )
        item = await paperless.tasks(1)
        assert item
        assert isinstance(item, Task)
        # by uuid
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status_code=200,
            json=DATA_TASKS,
        )
        item = await paperless.tasks("dummy-found")
        assert item
        assert isinstance(item, Task)
        # must raise as pk doesn't exist
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['tasks_single']}".format(pk=1337),
            status_code=404,
        )
        with pytest.raises(httpx.HTTPStatusError):
            await paperless.tasks(1337)
        # must raise as task_id doesn't exist
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['tasks']}" + r"\?task_id.*$"),
            status_code=200,
            json=[],
        )
        with pytest.raises(TaskNotFoundError):
            await paperless.tasks("dummy-not-found")


# test models/workflows.py
class TestModelWorkflows:
    """Tasks test cases."""

    async def test_services(self, paperless: Paperless) -> None:
        """Test services."""
        assert isinstance(paperless.workflows.actions, WorkflowActionService)
        assert isinstance(paperless.workflows.triggers, WorkflowTriggerService)


# test services/trash.py
class TestModelTrash:
    """Trash test cases."""

    async def test_iter(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test iterating over trashed documents."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['trash']}" + r"\?.*$"),
            status_code=200,
            json=DATA_TRASH,
        )
        items = [item async for item in paperless.trash]
        assert len(items) == len(DATA_TRASH["results"])
        for item in items:
            assert isinstance(item, Document)
            assert item.deleted_at is not None

    async def test_restore(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test restore action."""
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "restored"},
        )
        await paperless.trash.restore([100, 101])

    async def test_empty(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Test empty action — all trash and specific documents."""
        # empty all
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "emptied"},
        )
        await paperless.trash.empty()
        # empty specific documents
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",
            status_code=200,
            json={"result": "emptied"},
        )
        await paperless.trash.empty([100])
