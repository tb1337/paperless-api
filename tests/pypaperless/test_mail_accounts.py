"""Test mail_accounts."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import EndpointCUDMixin, MailAccountsEndpoint, PaginatedResult
from pypaperless.models import MailAccount


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.mail_accounts, MailAccountsEndpoint)
    assert not isinstance(paperless.mail_accounts, EndpointCUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["mail_accounts"]):
        result = await paperless.mail_accounts.list()

        assert isinstance(result, list)
        assert len(result) > 0

        page = await paperless.mail_accounts.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), MailAccount)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["mail_accounts"]["results"][0]):
        item = await paperless.mail_accounts.one(72)

        assert isinstance(item, MailAccount)
