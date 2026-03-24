"""Tests for the model operation dispatcher."""

import gc

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import PaperlessClient
from pypaperless.const import API_PATH
from pypaperless.dispatch import _MODEL_TO_PROP_NAME, dispatchable_cached_property
from pypaperless.exceptions import DispatchError
from pypaperless.models import Correspondent, CorrespondentDraft
from pypaperless.models.tasks import Task
from pypaperless.services import (
    CorrespondentService,
    CustomFieldService,
    DocumentService,
    DocumentTypeService,
    ShareLinkService,
    StoragePathService,
    TagService,
)

from .const import PAPERLESS_TEST_URL
from .data import DATA_CORRESPONDENTS


class TestRegistry:
    """Verify that _MODEL_TO_PROP_NAME is populated correctly at import time."""

    def test_seven_services_use_dispatchable_cached_property(self) -> None:
        """All seven CRUD services must be dispatchable_cached_property descriptors."""
        for name in (
            "correspondents",
            "custom_fields",
            "documents",
            "document_types",
            "share_links",
            "storage_paths",
            "tags",
        ):
            assert isinstance(
                PaperlessClient.__dict__[name],
                dispatchable_cached_property,
            ), f"{name!r} is not a dispatchable_cached_property"

    def test_resource_cls_registered(self) -> None:
        """Each _resource_cls must map to the correct property name."""
        expected: dict[type, str] = {
            Correspondent: "correspondents",
        }
        for model_cls, prop_name in expected.items():
            assert _MODEL_TO_PROP_NAME.get(model_cls) == prop_name

    def test_draft_cls_registered(self) -> None:
        """Each _draft_cls must map to the correct property name."""
        expected: dict[type, str] = {
            CorrespondentDraft: "correspondents",
        }
        for draft_cls, prop_name in expected.items():
            assert _MODEL_TO_PROP_NAME.get(draft_cls) == prop_name

    def test_all_crud_service_models_registered(self) -> None:
        """All seven service classes contribute their model types to the registry."""
        for svc_cls in (
            CorrespondentService,
            CustomFieldService,
            DocumentService,
            DocumentTypeService,
            ShareLinkService,
            StoragePathService,
            TagService,
        ):
            resource_cls = getattr(svc_cls, "_resource_cls", None)
            draft_cls = getattr(svc_cls, "_draft_cls", None)
            if resource_cls is not None:
                assert resource_cls in _MODEL_TO_PROP_NAME, (
                    f"_resource_cls {resource_cls.__name__!r} of {svc_cls.__name__!r} "
                    "not in registry"
                )
            if draft_cls is not None:
                assert draft_cls in _MODEL_TO_PROP_NAME, (
                    f"_draft_cls {draft_cls.__name__!r} of {svc_cls.__name__!r} not in registry"
                )

    def test_service_is_cached(self, api: PaperlessClient) -> None:
        """Accessing dispatchable_cached_property twice must return the same object."""
        svc1 = api.correspondents
        svc2 = api.correspondents
        assert svc1 is svc2


class TestDispatcherInit:
    """Verify ModelDispatcher construction and weakref behaviour."""

    def test_weakref_stored(self, api: PaperlessClient) -> None:
        """The dispatcher must hold a weakref to the client, not a strong reference."""
        dispatcher = api._dispatcher
        assert isinstance(dispatcher._client_ref, type(dispatcher._client_ref))
        assert dispatcher._client_ref() is api

    def test_weakref_gc(self) -> None:
        """After the client is garbage-collected, _resolve_client must raise DispatchError."""
        client = PaperlessClient(PAPERLESS_TEST_URL, "tok")
        dispatcher = client._dispatcher
        del client
        gc.collect()
        with pytest.raises(DispatchError, match="garbage collected"):
            dispatcher._resolve_client()

    def test_unknown_model_type_raises(self, api: PaperlessClient) -> None:
        """Dispatching a model type with no registered service raises DispatchError."""
        task = Task.model_construct()
        with pytest.raises(DispatchError, match="No service registered"):
            api._dispatcher._get_service(type(task))


class TestDispatchUpdate:
    """Verify that update() delegates to the correct service."""

    async def test_update_dispatches(
        self, httpx_mock: HTTPXMock, paperless: PaperlessClient
    ) -> None:
        """update() on a Correspondent must call CorrespondentService.update."""
        pk = DATA_CORRESPONDENTS["results"][0]["id"]
        # fetch the model via the service
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=pk),
            status_code=200,
            json=DATA_CORRESPONDENTS["results"][0],
        )
        corr = await paperless.correspondents(pk)

        # mutate and mock the PATCH
        corr.name = "Dispatcher Updated"
        httpx_mock.add_response(
            method="PATCH",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=pk),
            status_code=200,
            json={**corr._snapshot, "name": "Dispatcher Updated"},
        )
        result = await paperless.update(corr)
        assert result is True
        assert corr.name == "Dispatcher Updated"

    async def test_update_no_change_returns_false(
        self, httpx_mock: HTTPXMock, paperless: PaperlessClient
    ) -> None:
        """update() without any mutations must return False (no request sent)."""
        pk = DATA_CORRESPONDENTS["results"][0]["id"]
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=pk),
            status_code=200,
            json=DATA_CORRESPONDENTS["results"][0],
        )
        corr = await paperless.correspondents(pk)
        result = await paperless.update(corr)
        assert result is False


class TestDispatchDelete:
    """Verify that delete() delegates to the correct service."""

    async def test_delete_dispatches(
        self, httpx_mock: HTTPXMock, paperless: PaperlessClient
    ) -> None:
        """delete() on a Correspondent must call CorrespondentService.delete."""
        pk = DATA_CORRESPONDENTS["results"][0]["id"]
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=pk),
            status_code=200,
            json=DATA_CORRESPONDENTS["results"][0],
        )
        corr = await paperless.correspondents(pk)

        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents_single']}".format(pk=pk),
            status_code=204,
        )
        await paperless.delete(corr)  # must not raise


class TestDispatchSave:
    """Verify that save() delegates to the correct service."""

    async def test_save_dispatches(self, httpx_mock: HTTPXMock, paperless: PaperlessClient) -> None:
        """save() on a CorrespondentDraft must call CorrespondentService.save."""
        draft = paperless.correspondents.create(
            name="New via Dispatcher",
            match="",
            matching_algorithm=1,
            is_insensitive=True,
        )
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH['correspondents']}",
            status_code=200,
            json={"id": 99, "name": "New via Dispatcher"},
        )
        new_id = await paperless.save(draft)
        assert new_id == 99
