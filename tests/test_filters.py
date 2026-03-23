"""Tests for filter TypedDicts and typed service .filter() methods."""

import re
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import PaperlessClient
from pypaperless.const import API_PATH
from pypaperless.models.types import (
    CorrespondentFilters,
    CustomFieldFilters,
    DocumentFilters,
    DocumentTypeFilters,
    GroupFilters,
    ShareLinkFilters,
    StoragePathFilters,
    TagFilters,
    TaskFilters,
    UserFilters,
)

from .const import PAPERLESS_TEST_URL
from .data import (
    DATA_CORRESPONDENTS,
    DATA_DOCUMENTS,
    DATA_GROUPS,
    DATA_STORAGE_PATHS,
    DATA_TAGS,
    DATA_TRASH,
    DATA_USERS,
)

_ALL_FILTER_CLASSES = (
    CorrespondentFilters,
    CustomFieldFilters,
    DocumentFilters,
    DocumentTypeFilters,
    GroupFilters,
    ShareLinkFilters,
    StoragePathFilters,
    TagFilters,
    TaskFilters,
    UserFilters,
)


# ---------------------------------------------------------------------------
# TypedDict structural checks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", _ALL_FILTER_CLASSES, ids=lambda c: c.__name__)
def test_filter_has_fields(cls: Any) -> None:
    """Every filter TypedDict must expose at least one filter field."""
    assert cls.__optional_keys__ | cls.__required_keys__


@pytest.mark.parametrize("cls", _ALL_FILTER_CLASSES, ids=lambda c: c.__name__)
def test_filter_excludes_pagination_keys(cls: Any) -> None:
    """Filter TypedDicts must NOT contain page or page_size (those are pagination params)."""
    all_keys = cls.__optional_keys__ | cls.__required_keys__
    assert "page" not in all_keys
    assert "page_size" not in all_keys


@pytest.mark.parametrize(
    ("cls", "expected_keys"),
    [
        (
            DocumentFilters,
            [
                "title__icontains",
                "is_tagged",
                "is_in_inbox",
                "correspondent__id",
                "tags__id__all",
                "custom_field_query",
                "mime_type",
            ],
        ),
        (TagFilters, ["is_root"]),
        (StoragePathFilters, ["path__icontains", "path__istartswith"]),
        (ShareLinkFilters, ["expiration__year", "expiration__date__gte"]),
        (TaskFilters, ["acknowledged", "status", "task_name", "type"]),
        (UserFilters, ["username__icontains", "username__iexact"]),
    ],
    ids=[
        "DocumentFilters",
        "TagFilters",
        "StoragePathFilters",
        "ShareLinkFilters",
        "TaskFilters",
        "UserFilters",
    ],
)
def test_filter_contains_expected_fields(cls: Any, expected_keys: Any) -> None:
    """Each filter TypedDict must contain its resource-specific fields."""
    all_keys = cls.__optional_keys__ | cls.__required_keys__
    for key in expected_keys:
        assert key in all_keys, f"{cls.__name__} missing {key!r}"


# ---------------------------------------------------------------------------
# Typed service .filter() acceptance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("api_key", "service_attr", "filter_kwargs", "mock_data"),
    [
        (
            "documents",
            "documents",
            {"title__icontains": "invoice", "is_tagged": True},
            DATA_DOCUMENTS,
        ),
        ("correspondents", "correspondents", {"name__icontains": "acme"}, DATA_CORRESPONDENTS),
        ("tags", "tags", {"is_root": True}, DATA_TAGS),
        ("storage_paths", "storage_paths", {"path__icontains": "/invoices"}, DATA_STORAGE_PATHS),
        ("trash", "trash", {"title__icontains": "old"}, DATA_TRASH),
        ("groups", "groups", {"name__icontains": "admin"}, DATA_GROUPS),
        ("users", "users", {"username__icontains": "admin"}, DATA_USERS),
    ],
    ids=["documents", "correspondents", "tags", "storage_paths", "trash", "groups", "users"],
)
async def test_service_filter_accepts_typed_kwargs(
    httpx_mock: HTTPXMock,
    paperless: PaperlessClient,
    api_key: str,
    service_attr: str,
    filter_kwargs: dict,
    mock_data: dict,
) -> None:
    """service.filter() accepts typed filter kwargs and iterates results without error."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH[api_key]}" + r"\?.*$"),
        status_code=200,
        json=mock_data,
    )
    async with getattr(paperless, service_attr).filter(**filter_kwargs) as q:
        async for item in q:
            assert item is not None
