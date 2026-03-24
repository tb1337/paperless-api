"""Tests for filter TypedDicts and typed service .filter() methods."""

import re

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import PaperlessClient
from pypaperless.const import API_PATH

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
