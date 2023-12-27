"""Test mail_rules."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.controllers import MailRulesController
from pypaperless.controllers.base import CreateMixin, DeleteMixin, ResultPage, UpdateMixin
from pypaperless.models import MailRule


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["mail_rules"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.mail_rules, MailRulesController)
    assert not isinstance(paperless.mail_rules, CreateMixin | UpdateMixin | DeleteMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.mail_rules.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.mail_rules.get()

        assert isinstance(page, ResultPage)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), MailRule)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.mail_rules.iterate():
            assert isinstance(item, MailRule)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.mail_rules.one(72)

        assert isinstance(item, MailRule)
