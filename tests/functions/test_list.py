"""Test CRUD."""

from unittest.mock import patch

from pypaperless import Paperless


async def test_empty_list(paperless: Paperless):
    """Test empty controller list."""
    with patch.object(paperless, "request_json", return_value={}):
        # list must be empty because "all" key is omitted in return value
        items = await paperless.documents.list()
        assert items == []
