"""Test consumption_templates."""

from unittest.mock import patch

import pytest

from pypaperless import Paperless
from pypaperless.api import ConsumptionTemplatesEndpoint
from pypaperless.api.base import BaseEndpointCrudMixin, PaginatedResult
from pypaperless.models import ConsumptionTemplate
from pypaperless.models.shared import ConsumptionTemplateSource


@pytest.fixture(scope="module")
def dataset(data):
    """Represent current data."""
    return data["consumption_templates"]


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.consumption_templates, ConsumptionTemplatesEndpoint)
    assert not isinstance(paperless.consumption_templates, BaseEndpointCrudMixin)


async def test_list_and_get(paperless: Paperless, dataset):
    """Test list."""
    with patch.object(paperless, "request_json", return_value=dataset):
        result = await paperless.consumption_templates.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.consumption_templates.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), ConsumptionTemplate)


async def test_iterate(paperless: Paperless, dataset):
    """Test iterate."""
    with patch.object(paperless, "request_json", return_value=dataset):
        async for item in paperless.consumption_templates.iterate():
            assert isinstance(item, ConsumptionTemplate)


async def test_one(paperless: Paperless, dataset):
    """Test one."""
    with patch.object(paperless, "request_json", return_value=dataset["results"][0]):
        item = await paperless.consumption_templates.one(72)

        assert isinstance(item, ConsumptionTemplate)
        assert isinstance(item.sources.pop(), ConsumptionTemplateSource)
