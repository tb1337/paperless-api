"""Test mail_rules."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import EnableCRUDMixin, MailRulesEndpoint, PaginatedResult
from pypaperless.models import MailRule


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.mail_rules, MailRulesEndpoint)
    assert not isinstance(paperless.mail_rules, EnableCRUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["mail_rules"]):
        result = await paperless.mail_rules.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.mail_rules.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), MailRule)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["mail_rules"]):
        async for item in paperless.mail_rules.iterate():
            assert isinstance(item, MailRule)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(paperless, "request", return_value=data["mail_rules"]["results"][0]):
        item = await paperless.mail_rules.one(72)

        assert isinstance(item, MailRule)
