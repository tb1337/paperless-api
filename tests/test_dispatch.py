"""Tests for the model operation dispatcher."""

import gc
from typing import ClassVar

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import PaperlessClient
from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.dispatch import (
    _MODEL_TO_PROP_NAME,
    DispatchableCachedProperty,
    dispatchable_cached_property,
)
from pypaperless.exceptions import DispatchError
from pypaperless.models import Correspondent, CorrespondentDraft, DocumentNote, DocumentNoteDraft
from pypaperless.models.base import PaperlessModel
from pypaperless.models.tasks import Task
from pypaperless.services import (
    CorrespondentService,
    CustomFieldService,
    DocumentNoteService,
    DocumentService,
    DocumentTypeService,
    ShareLinkService,
    StoragePathService,
    TagService,
)
from pypaperless.services.base import PaperlessService, ResourceService
from pypaperless.services.mixins import DeletableService

from .const import PAPERLESS_TEST_URL
from .data import DATA_CORRESPONDENTS

# ---------------------------------------------------------------------------
# Module-level helpers for DispatchableCachedProperty.__set_name__ edge cases
#
# Annotation mutation trick: define a function with a valid annotation that
# mypy can check, then replace __annotations__["return"] at module level with
# an unresolvable string so get_type_hints() raises NameError at runtime.
# This lets us cover defensive exception-handling branches without using any
# suppression comment.
# ---------------------------------------------------------------------------


def _factory_bad_type_hint(self: object) -> PaperlessService:
    """Provide a runtime-unresolvable return annotation (exercises L62-63)."""
    raise NotImplementedError


# Overwrite the return annotation with an undefined name so get_type_hints raises.
_factory_bad_type_hint.__annotations__["return"] = "_UndefinedTypeAtRuntime_XYZABC"


def _factory_no_return_annotation(self: object) -> PaperlessService:
    """Remove return annotation so hints.get('return') is None (exercises L66)."""
    raise NotImplementedError


# Removing the annotation makes hints.get("return") → None → not a PaperlessService.
del _factory_no_return_annotation.__annotations__["return"]


def _factory_base_service_return(self: object) -> PaperlessService:
    """Return PaperlessService base (no _resource_cls/_draft_cls, exercises L69->67)."""
    raise NotImplementedError


class _FakeDispatchTestModel(PaperlessModel):
    """Minimal PaperlessModel used only for dispatch coverage tests."""

    _api_path: ClassVar[str] = "/api/dispatch-fake/"


class _FakeWritableSubSvc(
    ResourceService,
    DeletableService[_FakeDispatchTestModel],
):
    """Writable sub-service with _resource_cls but no _draft_cls (exercises L85->83)."""

    _api_path = "/api/dispatch-fake/"
    _resource = PaperlessResource.DOCUMENTS

    _resource_cls = _FakeDispatchTestModel
    # Deliberately omit _draft_cls so the loop's False branch (L85->83) is taken.


def _bad_sub_fget(self: object) -> PaperlessService:
    """Property getter for bad_sub; annotation replaced below (L76-77 coverage)."""
    raise NotImplementedError


# Overwrite return annotation with an undefined name so get_type_hints raises.
_bad_sub_fget.__annotations__["return"] = "_UndefinedSubTypeAtRuntime_XYZABC"


class _FakeSvcWithSubProps(PaperlessService):
    """Service with sub-properties exercising __set_name__ sub-discovery edge cases."""

    # bad_sub: annotation is an unresolvable string → get_type_hints raises (L76-77).
    bad_sub: property = property(_bad_sub_fget)

    @property
    def str_sub(self) -> str:
        """Sub-property returning str — not a PaperlessService subclass (L80)."""
        return ""

    @property
    def writable_sub(self) -> _FakeWritableSubSvc:
        """Writable sub-service without _draft_cls — exercises L85->83 branch."""
        raise NotImplementedError


def _factory_fake_with_sub_props(self: object) -> _FakeSvcWithSubProps:
    """Return _FakeSvcWithSubProps for __set_name__ sub-discovery edge-case coverage."""
    raise NotImplementedError


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
        """Each _resource_cls must map to the correct service path."""
        expected: dict[type, tuple[str, ...]] = {
            Correspondent: ("correspondents",),
        }
        for model_cls, path in expected.items():
            assert _MODEL_TO_PROP_NAME.get(model_cls) == path

    def test_draft_cls_registered(self) -> None:
        """Each _draft_cls must map to the correct service path."""
        expected: dict[type, tuple[str, ...]] = {
            CorrespondentDraft: ("correspondents",),
        }
        for draft_cls, path in expected.items():
            assert _MODEL_TO_PROP_NAME.get(draft_cls) == path

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

    def test_sub_service_resource_cls_registered(self) -> None:
        """Sub-service _resource_cls must map to a 2-element path tuple."""
        assert _MODEL_TO_PROP_NAME.get(DocumentNote) == ("documents", "notes")

    def test_sub_service_draft_cls_registered(self) -> None:
        """Sub-service _draft_cls must map to a 2-element path tuple."""
        assert _MODEL_TO_PROP_NAME.get(DocumentNoteDraft) == ("documents", "notes")


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

    def test_get_service_sub_path(self, api: PaperlessClient) -> None:
        """_get_service navigates a 2-element path to reach a sub-service."""
        svc = api._dispatcher._get_service(DocumentNote)
        assert isinstance(svc, DocumentNoteService)


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


class TestDispatchableCachedPropertyBehavior:
    """Verify DispatchableCachedProperty descriptor behaviour and __set_name__ edge cases."""

    def test_class_level_access_returns_descriptor(self) -> None:
        """Accessing the property on the class (obj=None) must return the descriptor itself."""
        result = PaperlessClient.correspondents
        assert isinstance(result, dispatchable_cached_property)

    def test_cached_service_not_reconstructed(self, api: PaperlessClient) -> None:
        """Second access must return the cached instance without calling the factory again."""
        svc1 = api.correspondents  # cache miss — factory called, stored in inst_dict
        svc2 = api.correspondents  # Python attribute-lookup returns inst_dict value directly
        assert svc1 is svc2

    def test_set_name_silences_type_hints_error(self) -> None:
        """__set_name__ must return silently when get_type_hints raises (L62-63)."""
        prop = DispatchableCachedProperty(_factory_bad_type_hint)
        prop.__set_name__(object, "bad_hint_prop")
        assert prop._attr_name == "bad_hint_prop"

    def test_set_name_skips_non_service_return(self) -> None:
        """__set_name__ must not touch the registry when return is not a service (L66)."""
        prop = DispatchableCachedProperty(_factory_no_return_annotation)
        before = dict(_MODEL_TO_PROP_NAME)
        prop.__set_name__(object, "no_return_prop")
        assert before == _MODEL_TO_PROP_NAME

    def test_set_name_handles_service_without_model_cls(self) -> None:
        """__set_name__ must not crash when _resource_cls/_draft_cls are absent (L69->67).

        PaperlessService base has neither attribute, so both loop iterations take the False branch.
        """
        prop = DispatchableCachedProperty(_factory_base_service_return)
        before = dict(_MODEL_TO_PROP_NAME)
        prop.__set_name__(object, "base_svc_prop")
        assert before == _MODEL_TO_PROP_NAME

    def test_set_name_sub_prop_silences_type_hints_error(self) -> None:
        """__set_name__ must silently skip sub-properties with unresolvable annotations (L76-77)."""
        prop = DispatchableCachedProperty(_factory_fake_with_sub_props)
        prop.__set_name__(object, "fake_sub_prop_a")
        assert prop._attr_name == "fake_sub_prop_a"
        _MODEL_TO_PROP_NAME.pop(_FakeDispatchTestModel, None)

    def test_set_name_sub_prop_skips_non_service(self) -> None:
        """__set_name__ must skip sub-properties that return a non-PaperlessService type (L80)."""
        prop = DispatchableCachedProperty(_factory_fake_with_sub_props)
        prop.__set_name__(object, "fake_sub_prop_b")
        assert str not in _MODEL_TO_PROP_NAME
        _MODEL_TO_PROP_NAME.pop(_FakeDispatchTestModel, None)

    def test_set_name_sub_prop_handles_missing_draft_cls(self) -> None:
        """__set_name__ must handle a writable sub-service with only _resource_cls (L85->83).

        The inner loop's False branch for _draft_cls is taken because _FakeWritableSubSvc
        has no _draft_cls attribute.
        """
        prop = DispatchableCachedProperty(_factory_fake_with_sub_props)
        prop.__set_name__(object, "fake_sub_prop_c")
        assert _MODEL_TO_PROP_NAME.get(_FakeDispatchTestModel) == (
            "fake_sub_prop_c",
            "writable_sub",
        )
        del _MODEL_TO_PROP_NAME[_FakeDispatchTestModel]


class TestDispatchGuards:
    """Verify DispatchError is raised when a service lacks a required operation."""

    async def test_update_raises_for_non_updatable_service(self, api: PaperlessClient) -> None:
        """update() must raise DispatchError when the resolved service is not UpdatableService."""
        note = DocumentNote.model_construct(id=1, document=42)
        with pytest.raises(DispatchError, match="does not support 'update'"):
            await api._dispatcher.update(note)

    async def test_delete_raises_for_non_deletable_service(self, api: PaperlessClient) -> None:
        """delete() must raise DispatchError when the resolved service is not DeletableService."""
        _MODEL_TO_PROP_NAME[DocumentNote] = ("profile",)
        try:
            note = DocumentNote.model_construct(id=1, document=42)
            with pytest.raises(DispatchError, match="does not support 'delete'"):
                await api._dispatcher.delete(note)
        finally:
            _MODEL_TO_PROP_NAME[DocumentNote] = ("documents", "notes")

    async def test_save_raises_for_non_creatable_service(self, api: PaperlessClient) -> None:
        """save() must raise DispatchError when the resolved service is not CreatableService."""
        _MODEL_TO_PROP_NAME[DocumentNoteDraft] = ("profile",)
        try:
            draft = DocumentNoteDraft.model_construct(note="x", document=42)
            with pytest.raises(DispatchError, match="does not support 'save'"):
                await api._dispatcher.save(draft)
        finally:
            _MODEL_TO_PROP_NAME[DocumentNoteDraft] = ("documents", "notes")
