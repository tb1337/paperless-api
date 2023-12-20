"""Test consumption_templates."""

from unittest.mock import patch

from pypaperless import Paperless
from pypaperless.api import ConsumptionTemplatesEndpoint, EnableCRUDMixin, PaginatedResult
from pypaperless.models import ConsumptionTemplate
from pypaperless.models.shared import ConsumptionTemplateSource


async def test_endpoint(paperless: Paperless) -> None:
    """Test endpoint."""
    assert isinstance(paperless.consumption_templates, ConsumptionTemplatesEndpoint)
    assert not isinstance(paperless.consumption_templates, EnableCRUDMixin)


async def test_list_and_get(paperless: Paperless, data):
    """Test list."""
    with patch.object(paperless, "request", return_value=data["consumption_templates"]):
        result = await paperless.consumption_templates.list()

        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert isinstance(item, int)

        page = await paperless.consumption_templates.get()

        assert isinstance(page, PaginatedResult)
        assert len(page.items) > 0
        assert isinstance(page.items.pop(), ConsumptionTemplate)


async def test_iterate(paperless: Paperless, data):
    """Test iterate."""
    with patch.object(paperless, "request", return_value=data["consumption_templates"]):
        async for item in paperless.consumption_templates.iterate():
            assert isinstance(item, ConsumptionTemplate)


async def test_one(paperless: Paperless, data):
    """Test one."""
    with patch.object(
        paperless, "request", return_value=data["consumption_templates"]["results"][0]
    ):
        item = await paperless.consumption_templates.one(72)

        assert isinstance(item, ConsumptionTemplate)
        assert isinstance(item.sources.pop(), ConsumptionTemplateSource)
