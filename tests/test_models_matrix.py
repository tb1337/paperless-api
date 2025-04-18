"""Paperless basic tests."""

import re
from typing import Any

import aiohttp
import pytest
from aioresponses import CallbackResult, aioresponses

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
    SAVED_VIEW_MAP,
    SHARE_LINK_MAP,
    STORAGE_PATH_MAP,
    TAG_MAP,
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
class TestReadOnly:
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

    async def test_as_dict(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test as_dict."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        items = await getattr(api_latest, mapping.resource).as_dict()
        for pk, obj in items.items():
            assert isinstance(pk, int)
            assert isinstance(obj, mapping.model_cls)

    async def test_as_list(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test as_dict."""
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload=PATCHWORK[mapping.resource],
        )
        items = await getattr(api_latest, mapping.resource).as_list()
        for obj in items:
            assert isinstance(obj, mapping.model_cls)

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
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(aiohttp.ClientResponseError):
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
class TestReadWrite:
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
        async with getattr(api_latest, mapping.resource).reduce(
            any_filter_param="1",
            any_filter_list__in=["1", "2"],
            any_filter_no_list__in="1",
        ) as q:
            async for item in q:
                assert isinstance(item, mapping.model_cls)

    async def test_call(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test call."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        item = await getattr(api_latest, mapping.resource)(1)
        assert item
        assert isinstance(item, mapping.model_cls)
        # must raise as 1337 doesn't exist
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1337),
            status=404,
        )
        with pytest.raises(aiohttp.ClientResponseError):
            await getattr(api_latest, mapping.resource)(1337)

    async def test_create(
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test create."""
        draft = getattr(api_latest, mapping.resource).draft(**mapping.draft_defaults)
        assert isinstance(draft, mapping.draft_cls)
        # test empty draft fields
        if mapping.model_cls not in (
            SHARE_LINK_MAP.model_cls,
            CUSTOM_FIELD_MAP.model_cls,
        ):
            backup = draft.name
            draft.name = None
            with pytest.raises(DraftFieldRequiredError):
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
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_update = await getattr(api_latest, mapping.resource)(1)
        setattr(to_update, update_field, update_value)
        # actually call the update endpoint
        resp.patch(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
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
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
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
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=200,
            payload=PATCHWORK[mapping.resource]["results"][0],
        )
        to_delete = await getattr(api_latest, mapping.resource)(1)
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=204,  # Paperless-ngx responds with 204 on deletion
        )
        assert await to_delete.delete()
        # test deletion failed
        resp.delete(
            f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1),
            status=404,  # we send another status code
        )
        assert not await to_delete.delete()


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
        self, resp: aioresponses, api_latest: Paperless, mapping: ResourceTestMapping
    ) -> None:
        """Test permissions."""
        getattr(api_latest, mapping.resource).request_permissions = True
        assert getattr(api_latest, mapping.resource).request_permissions
        # request single object
        resp.get(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1)
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
        # request by iterator
        resp.get(
            re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource]}" + r"\?.*$"),
            status=200,
            payload={
                **PATCHWORK[mapping.resource],
                "results": [
                    {**item, "permissions": PATCHWORK["object_permissions"]}
                    for item in PATCHWORK[mapping.resource]["results"]
                ],
            },
        )
        async for item in getattr(api_latest, mapping.resource):
            assert isinstance(item, mapping.model_cls)
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
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1)
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

        def _lookup_set_permissions(  # pylint: disable=unused-argument
            url: str,
            json: dict[str, Any],
            **kwargs: Any,  # noqa: ARG001
        ) -> CallbackResult:
            assert url
            assert "set_permissions" in json
            return CallbackResult(
                status=200,
                payload=item._data,  # pylint: disable=protected-access
            )

        resp.patch(
            re.compile(
                r"^"
                + f"{PAPERLESS_TEST_URL}{API_PATH[mapping.resource + '_single']}".format(pk=1)
                + r"\?.*$"
            ),
            callback=_lookup_set_permissions,
        )
        await item.update()
