"""Test correspondents."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import CorrespondentsEndpoint, PaginatedResult
from pypaperless.models import Correspondent
from pypaperless.models.shared import MatchingAlgorithm


async def test_endpoint(paperless: Paperless) -> None:
    """Test correspondents endpoint."""
    assert isinstance(paperless.correspondents, CorrespondentsEndpoint)

    # test endpoint implements CUD features
    assert paperless.correspondents.create
    assert paperless.correspondents.update
    assert paperless.correspondents.delete


async def test_list_and_get(paperless: Paperless, data):
    """Test correspondents list."""
    with patch.object(paperless, "request", return_value=data["correspondents"]):
        result = await paperless.correspondents.list()

        assert isinstance(result, list)
        assert len(result) > 0

        page = await paperless.correspondents.get()

        assert isinstance(page, PaginatedResult)
        assert page.current_page == 1
        assert page.next_page == 2
        assert len(page.items) >= 5
        assert isinstance(page.items.pop(), Correspondent)


async def test_one(paperless: Paperless, data):
    """Test correspondents one."""
    with patch.object(paperless, "request", return_value=data["correspondents"]["results"][0]):
        item = await paperless.correspondents.one(72)

        assert isinstance(item, Correspondent)
        assert isinstance(item.matching_algorithm, MatchingAlgorithm)
