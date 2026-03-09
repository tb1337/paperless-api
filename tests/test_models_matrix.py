"""Paperless basic tests."""

import re

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.exceptions import DraftFieldRequiredError
from pypaperless.models import Page
from pypaperless.models.common import PermissionTableType

from . import (
    CORRESPONDENT_MAP,
    CUSTOM_FIELD_MAP,
    DOCUMENT_MAP,
    DOCUMENT_TYPE_MAP,
    GROUP_MAP,
    MAIL_ACCOUNT_MAP,
    MAIL_RULE_MAP,
    PROCESSED_MAIL_MAP,
    SAVED_VIEW_MAP,
    SHARE_LINK_MAP,
    STORAGE_PATH_MAP,
    TAG_MAP,
    USER_MAP,
    WORKFLOW_MAP,
    ResourceTestMapping,
)
from .const import PAPERLESS_TEST_URL
from .data import DATA_OBJECT_PERMISSIONS

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
        PROCESSED_MAIL_MAP,
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
class TestReadOnly:
    """Read only resources test cases."""

    async def test_pages(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test pages."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        page = await anext(aiter(getattr(paperless, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_as_dict(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test as_dict."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        items = await getattr(paperless, mapping.resource).as_dict()
        for pk, obj in items.items():
            assert isinstance(pk, int)
            assert isinstance(obj, mapping.model_cls)

    async def test_as_list(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test as_dict."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        items = await getattr(paperless, mapping.resource).as_list()
        for obj in items:
            assert isinstance(obj, mapping.model_cls)

    async def test_iter(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        async for item in getattr(paperless, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_all(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test all."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        items = await getattr(paperless, mapping.resource).all()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, int)

    async def test_call(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status_code=200,
            json=mapping.data["results"][0],
        )
        item = await getattr(paperless, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1337),
            status_code=404,
        )
        with pytest.raises(httpx.HTTPStatusError):
            await getattr(paperless, mapping.resource)(1337)


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
class TestReadWrite:
    """R/W models test cases."""

    async def test_pages(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test pages."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        page = await anext(aiter(getattr(paperless, mapping.resource).pages(1)))
        assert isinstance(page, Page)
        assert isinstance(page.items, list)
        for item in page.items:
            assert isinstance(item, mapping.model_cls)

    async def test_iter(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        async for item in getattr(paperless, mapping.resource):
            assert isinstance(item, mapping.model_cls)

    async def test_all(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test all."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        items = await getattr(paperless, mapping.resource).all()
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, int)

    async def test_reduce(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test iter with reduce."""
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json=mapping.data,
        )
        async with getattr(paperless, mapping.resource).reduce(
            any_filter_param="1",
            any_filter_list__in=["1", "2"],
            any_filter_no_list__in="1",
        ) as q:
            async for item in q:
                assert isinstance(item, mapping.model_cls)

    async def test_call(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status_code=200,
            json=mapping.data["results"][0],
        )
        item = await getattr(paperless, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1337),
            status_code=404,
        )
        with pytest.raises(httpx.HTTPStatusError):
            await getattr(paperless, mapping.resource)(1337)

    async def test_create(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test create."""
        service = getattr(paperless, mapping.resource)
        draft = service.draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)
        # test empty draft fields
        if mapping.model_cls not in (
            SHARE_LINK_MAP.model_cls,
            CUSTOM_FIELD_MAP.model_cls,
        ):
            backup = draft.name
            draft.name = None
            with pytest.raises(DraftFieldRequiredError):
                await service.save(draft)
            draft.name = backup
        # actually call the create endpoint
        httpx_mock.add_response(
            method="POST",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}",
            status_code=200,
            json={
                "id": len(mapping.data["results"]),
                **draft._serialize(),  # pylint: disable=protected-access
            },
        )
        new_pk = await service.save(draft)
        assert new_pk >= 1

    async def test_udpate(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test update."""
        update_field = "name"
        update_value = "Name Updated"
        if mapping.model_cls is SHARE_LINK_MAP.model_cls:
            update_field = "document"
            update_value = 2
        # go on
        pk = mapping.data["results"][0]["id"]
        service = getattr(paperless, mapping.resource)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=200,
            json=mapping.data["results"][0],
        )
        to_update = await service(pk)
        setattr(to_update, update_field, update_value)
        # actually call the update endpoint
        httpx_mock.add_response(
            method="PATCH",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=200,
            json={
                **to_update._data,  # pylint: disable=protected-access
                update_field: update_value,
            },
        )
        await service.update(to_update)
        assert getattr(to_update, update_field) == update_value
        # no updates
        assert not await service.update(to_update)
        # force update
        setattr(to_update, update_field, update_value)
        httpx_mock.add_response(
            method="PUT",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=200,
            json={
                **to_update._data,  # pylint: disable=protected-access
                update_field: update_value,
            },
        )
        await service.update(to_update, only_changed=False)
        assert getattr(to_update, update_field) == update_value

    async def test_delete(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test delete."""
        pk = mapping.data["results"][0]["id"]
        service = getattr(paperless, mapping.resource)
        httpx_mock.add_response(
            method="GET",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=200,
            json=mapping.data["results"][0],
        )
        to_delete = await service(pk)
        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await service.delete(to_delete)
        # test deletion failed
        httpx_mock.add_response(
            method="DELETE",
            url=f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk),
            status_code=404,  # we send another status code
        )
        assert not await service.delete(to_delete)


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
class TestSecurableMixin:
    """SecurableMixin test cases."""

    async def test_permissions(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test permissions."""
        getattr(paperless, mapping.resource).request_permissions = True
        assert getattr(paperless, mapping.resource).request_permissions
        # request single object
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1)
                + r"\?.*$"
            ),
            status_code=200,
            json={
                **mapping.data["results"][0],
                "permissions": DATA_OBJECT_PERMISSIONS,
            },
        )
        item = await getattr(paperless, mapping.resource)(1)
        assert item.has_permissions
        assert isinstance(item.permissions, PermissionTableType)
        # request by iterator
        httpx_mock.add_response(
            method="GET",
            url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status_code=200,
            json={
                **mapping.data,
                "results": [
                    {**item, "permissions": DATA_OBJECT_PERMISSIONS}
                    for item in mapping.data["results"]
                ],
            },
        )
        async for item in getattr(paperless, mapping.resource):
            assert isinstance(item, mapping.model_cls)
            assert item.has_permissions
            assert isinstance(item.permissions, PermissionTableType)

    async def test_permission_change(
        self, httpx_mock: HTTPXMock, paperless: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test permission changes."""
        pk = mapping.data["results"][0]["id"]
        getattr(paperless, mapping.resource).request_permissions = True
        assert getattr(paperless, mapping.resource).request_permissions
        httpx_mock.add_response(
            method="GET",
            url=re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk)
                + r"\?.*$"
            ),
            status_code=200,
            json={
                **mapping.data["results"][0],
                "permissions": DATA_OBJECT_PERMISSIONS,
            },
        )
        item = await getattr(paperless, mapping.resource)(pk)
        item.permissions.view.users.append(23)

        def _lookup_set_permissions(request: httpx.Request) -> httpx.Response:
            assert request.url
            import json as json_mod

            json_data = json_mod.loads(request.content)
            assert "set_permissions" in json_data
            return httpx.Response(
                status_code=200,
                json=item._data,  # pylint: disable=protected-access
            )

        httpx_mock.add_callback(
            _lookup_set_permissions,
            url=re.compile(
                r"^"
                + re.escape(
                    f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=pk)
                )
                + r"\?.*$"
            ),
            method="PATCH",
        )
        await getattr(paperless, mapping.resource).update(item)
