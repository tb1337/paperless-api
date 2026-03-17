"""Tests for the Document service: CRUD, lazy fetch, files, notes, history, custom fields."""

import datetime
import json
import re

import pytest
from pydantic import BaseModel
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.exceptions import (
    AsnRequestError,
    DraftFieldRequiredError,
    PrimaryKeyRequiredError,
    SendEmailError,
)
from pypaperless.models import (
    Correspondent,
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
)
from pypaperless.services.mixins.updatable import UpdatableMixin

from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_CUSTOM_FIELDS,
    DATA_DOCUMENT_HISTORY,
    DATA_DOCUMENT_METADATA,
    DATA_DOCUMENT_NOTES,
    DATA_DOCUMENT_SUGGESTIONS,
    DATA_DOCUMENTS,
    DATA_DOCUMENTS_SEARCH,
)
from .mappings import DOCUMENT_MAP


class TestDocuments:
    """Document service: full CRUD, lazy loading, files, notes, history, custom fields."""

    async def test_lazy(self, paperless: Paperless) -> None:
        """Lazy-loaded document has id set but no title fetched."""
        document = await paperless.documents(42, lazy=True)
        assert document.id == 42
        assert document.title is None

    async def test_create(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Draft upload validates required fields and POSTs via the correct endpoint."""
        defaults = DOCUMENT_MAP.draft_defaults or {}
        draft = paperless.documents.create(**defaults)
        assert isinstance(draft, DocumentDraft)
        backup = draft.document
        draft.document = None
        with pytest.raises(DraftFieldRequiredError):
            await paperless.documents.save(draft)
        draft.document = backup
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_post']}",
            status_code=200,
            json="11112222-3333-4444-5555-666677778888",
        )
        await paperless.documents.save(draft)

    async def test_create_date_property(self, paperless: Paperless) -> None:
        """created_date is an alias for the created field."""
        document = Document.from_data(paperless, data={**DATA_DOCUMENTS["results"][0]})
        assert document.created_date == document.created

    async def test_update(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Updating a document PATCHes the changed field."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        to_update = await paperless.documents(1)
        new_title = f"{to_update.title} Updated"
        to_update.title = new_title
        httpx_mock.add_response(
            method="PATCH",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json={**to_update._data, "title": new_title},
        )
        await paperless.documents.update(to_update)
        assert to_update.title == new_title

    async def test_delete(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Deleting a document returns True on 204 and False on any other status."""
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
            status_code=204,
        )
        assert await paperless.documents.delete(to_delete)
        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=404,
        )
        assert not await paperless.documents.delete(to_delete)

    async def test_meta(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """get_metadata() returns a DocumentMeta with original and archive metadata lists."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_meta']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_METADATA,
        )
        meta = await paperless.documents.metadata(1)
        assert isinstance(meta, DocumentMeta)
        assert isinstance(meta.original_metadata, list)
        for item in meta.original_metadata:
            assert isinstance(item, DocumentMetaEntry)
        assert isinstance(meta.archive_metadata, list)
        for item in meta.archive_metadata:
            assert isinstance(item, DocumentMetaEntry)

    async def test_files(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """get_download/preview/thumbnail each return a DownloadedDocument."""
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
        download = await paperless.documents.download(1)
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
            headers={"Content-Type": "application/pdf"},
            content=b"Binary data: preview",
        )
        preview = await paperless.documents.preview(1)
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
        thumbnail = await paperless.documents.thumbnail(1)
        assert isinstance(thumbnail, DownloadedDocument)
        assert thumbnail.mode == FileRetrieveMode.THUMBNAIL

    async def test_suggestions(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """get_suggestions() returns a DocumentSuggestions instance."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_suggestions']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_SUGGESTIONS,
        )
        assert isinstance(await paperless.documents.suggestions(1), DocumentSuggestions)

    async def test_get_next_asn(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """get_next_asn() returns an int on success and raises AsnRequestError on failure."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status_code=200,
            json=1337,
        )
        assert isinstance(await paperless.documents.get_next_asn(), int)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_next_asn']}",
            status_code=500,
        )
        with pytest.raises(AsnRequestError):
            await paperless.documents.get_next_asn()

    async def test_searching(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """search(), search(custom_field_query=), and more_like() return typed items."""
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

        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                f"{PAPERLESS_TEST_URL}{API_PATH['documents']}"
                r"\?.*custom_field_query.*$"
            ),
            status_code=200,
            json=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.search(custom_field_query="1337"):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHit)

        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                f"{PAPERLESS_TEST_URL}{API_PATH['documents']}"
                r"\?.*more_like_id.*$"
            ),
            status_code=200,
            json=DATA_DOCUMENTS_SEARCH,
        )
        async for item in paperless.documents.more_like(1337):
            assert isinstance(item, Document)
            assert item.has_search_hit
            assert isinstance(item.search_hit, DocumentSearchHit)

    async def test_note_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Notes list returns DocumentNote instances; missing pk raises PrimaryKeyRequiredError."""
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
        """Note draft validates required fields and POSTs to the notes endpoint."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENTS["results"][0],
        )
        item = await paperless.documents(1)
        draft = item.notes.create(note="Test note.")
        assert isinstance(draft, DocumentNoteDraft)
        backup = draft.note
        draft.note = None
        with pytest.raises(DraftFieldRequiredError):
            await item.notes.save(draft)
        draft.note = backup
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_notes']}".format(pk=1),
            status_code=200,
            json=DATA_DOCUMENT_NOTES,
        )
        result = await item.notes.save(draft)
        assert isinstance(result, tuple)

    async def test_note_delete(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Deleting a note returns True on 204."""
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
            status_code=204,
        )
        assert await item.notes.delete(results.pop())

    async def test_history_call(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """History returns typed entries; direct service call and missing pk error both work."""
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

        with pytest.raises(PrimaryKeyRequiredError):
            await paperless.documents.history()

    async def test_custom_field_list_without_cache(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Without cache, custom fields are plain CustomFieldValue instances."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status_code=200,
            json=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)
        for field in item.custom_fields:
            for value_type in CUSTOM_FIELD_TYPE_VALUE_MAP.values():
                assert not isinstance(field, value_type)
            assert isinstance(field, CustomFieldValue)

    async def test_custom_field_list_with_cache(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """With cache, custom fields are typed; operators += and -= update the list."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['custom_fields']}" + r"\?.*$"),
            status_code=200,
            json=DATA_CUSTOM_FIELDS,
        )
        paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_single']}".format(pk=2),
            status_code=200,
            json=DATA_DOCUMENTS["results"][1],
        )
        item = await paperless.documents(2)
        assert isinstance(item.custom_fields, DocumentCustomFieldList)
        for field in item.custom_fields:
            assert isinstance(field, CustomFieldValue)

        test_cf = CustomField.from_data(
            client=paperless,
            data=DATA_CUSTOM_FIELDS["results"][0],
        )
        assert test_cf in item.custom_fields
        assert isinstance(item.custom_fields.get(test_cf), CustomFieldValue)
        assert item.custom_fields.default(test_cf) is not None
        assert item.custom_fields.default(-1337) is None

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

        item.custom_fields -= test_cf
        assert test_cf not in item.custom_fields

        item.custom_fields += test_cf.draft_value(1337)
        assert test_cf in item.custom_fields

    async def test_draft_custom_fields_as_id_list(self, paperless: Paperless) -> None:
        """DocumentDraft serialises list[int] custom_fields as repeated form values."""
        draft = paperless.documents.create(document=b"pdf", custom_fields=[1, 3, 5])
        serialized = draft.serialize()
        assert serialized["form"]["custom_fields"] == [1, 3, 5]

    async def test_draft_custom_fields_as_object_mapping(self, paperless: Paperless) -> None:
        """DocumentDraft serialises DocumentCustomFieldList as a JSON string."""
        cf = DocumentCustomFieldList.from_data(paperless, [])
        cf += CustomFieldStringValue(field=6, value="hello")
        cf += CustomFieldIntegerValue(field=3, value=42)

        draft = paperless.documents.create(document=b"pdf")
        draft.custom_fields = cf

        serialized = draft.serialize()
        raw = serialized["form"]["custom_fields"]
        assert isinstance(raw, str)
        decoded = json.loads(raw)
        assert isinstance(decoded, dict)
        assert decoded["6"] == "hello"
        assert decoded["3"] == 42

    async def test_draft_custom_fields_object_mapping_upload(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """A draft with a DocumentCustomFieldList can be POSTed successfully."""
        cf = DocumentCustomFieldList.from_data(paperless, [])
        cf += CustomFieldStringValue(field=6, value="smoke")

        draft = paperless.documents.create(document=b"%PDF-fake", title="CF Mapping Test")
        draft.custom_fields = cf

        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_post']}",
            status_code=200,
            json="aaaabbbb-cccc-dddd-eeee-ffffffffffff",
        )
        task_id = await paperless.documents.save(draft)
        assert task_id == "aaaabbbb-cccc-dddd-eeee-ffffffffffff"

        request = httpx_mock.get_request(method="POST")
        assert request is not None
        body = request.content.decode(errors="replace")
        match = re.search(r'name="custom_fields"\r\n\r\n(\{.*?\})\r\n', body, re.DOTALL)
        assert match is not None, f"custom_fields not found as JSON object in body: {body!r}"
        decoded = json.loads(match.group(1))
        assert decoded == {"6": "smoke"}

    async def test_email(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """Email dispatch succeeds on 200 and raises SendEmailError on 400."""
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

        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['documents_email']}",
            status_code=400,
        )
        with pytest.raises(SendEmailError):
            await paperless.documents.email(
                documents=[1, 2],
                addresses="test@example.org",
                subject="Test Email",
                message="Test Message",
            )

    async def test_is_deleted(self, paperless: Paperless) -> None:
        """Document.is_deleted is True when deleted_at is set, False otherwise."""
        doc_alive = Document.from_data(paperless, data={**DATA_DOCUMENTS["results"][0]})
        assert not doc_alive.is_deleted

        doc_trashed = Document.from_data(
            paperless,
            data={**DATA_DOCUMENTS["results"][0], "deleted_at": "2024-01-01T00:00:00Z"},
        )
        assert doc_trashed.is_deleted

    async def test_custom_field_list_from_data(self, paperless: Paperless) -> None:
        """DocumentCustomFieldList.from_data() constructs the list from raw API data."""
        raw = [{"field": 1, "value": "hello"}, {"field": 2, "value": 42}]
        cf_list = DocumentCustomFieldList.from_data(paperless, raw)
        assert isinstance(cf_list, DocumentCustomFieldList)
        assert len(list(cf_list)) == 2

    async def test_download_content_disposition_non_filename_part(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Download with a Content-Disposition that has a non-filename= part is handled."""
        # Content-Disposition has an extra part that is NOT filename=
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
                "Content-Disposition": "attachment; charset=utf-8; filename=doc.pdf",
            },
            content=b"binary",
        )
        download = await paperless.documents.download(1)
        assert isinstance(download, DownloadedDocument)
        assert download.disposition_filename == "doc.pdf"

    async def test_update_no_changes(self, httpx_mock: HTTPXMock, paperless: Paperless) -> None:
        """update() returns False without calling the API when nothing has changed."""
        # Use Correspondent which has only simple string/int fields that won't mismatch
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=1),
            status_code=200,
            json={"id": 1, "name": "ACME", "slug": "acme"},
        )
        item = await paperless.correspondents(1)
        # Sync model fields with _data so nothing appears changed
        item._data = {"id": item.id, "name": item.name, "slug": item.slug}
        result = await paperless.correspondents.update(item)
        assert result is False

    async def test_check_permissions_field_non_securable(self) -> None:
        """_check_permissions_field returns early for models without has_permissions."""

        class _PlainModel(BaseModel):
            id: int | None = None

        data: dict = {}
        # Should return without touching data (has no has_permissions attr)
        UpdatableMixin._check_permissions_field(_PlainModel(id=1), data)
        assert data == {}

    async def test_check_permissions_field_has_permissions_no_perms_key(
        self, paperless: Paperless
    ) -> None:
        """_check_permissions_field exits without changes when permissions not in data."""
        item = Correspondent.from_data(
            paperless,
            data={
                "id": 1,
                "name": "ACME",
                "permissions": {"view": {"users": []}, "change": {"users": []}},
            },
        )
        assert item.has_permissions
        changed: dict = {"name": "New Name"}
        UpdatableMixin._check_permissions_field(item, changed)
        # permissions not in changed, so no set_permissions key added
        assert "set_permissions" not in changed
        assert "name" in changed
