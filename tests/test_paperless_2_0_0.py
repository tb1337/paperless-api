"""Paperless v2.0.0 tests."""

import datetime

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless
from pypaperless.const import PaperlessFeature
from pypaperless.controllers import (
    ConsumptionTemplatesController,
    CustomFieldsController,
    ShareLinksController,
)
from pypaperless.controllers.base import ResultPage
from pypaperless.models import (
    ConsumptionTemplate,
    CustomField,
    CustomFieldPost,
    Document,
    ShareLink,
    ShareLinkPost,
)
from pypaperless.models.custom_fields import CustomFieldType, CustomFieldValue
from pypaperless.models.share_links import ShareLinkFileVersion


class TestBeginPaperless:
    """Paperless v2.0.0 test cases."""

    async def test_init(self, api_20: Paperless):
        """Test init."""
        assert api_20._token
        assert api_20._request_opts
        assert not api_20._session
        # test properties
        assert api_20.url
        assert api_20.is_initialized

    async def test_features(self, api_20: Paperless):
        """Test features."""
        # basic class has no features
        assert PaperlessFeature.CONTROLLER_STORAGE_PATHS in api_20.features
        assert PaperlessFeature.FEATURE_DOCUMENT_NOTES in api_20.features
        assert PaperlessFeature.CONTROLLER_SHARE_LINKS in api_20.features
        assert PaperlessFeature.CONTROLLER_CONSUMPTION_TEMPLATES in api_20.features
        assert PaperlessFeature.CONTROLLER_CUSTOM_FIELDS in api_20.features
        assert api_20.storage_paths
        assert api_20.consumption_templates
        assert api_20.custom_fields
        assert api_20.share_links
        assert not api_20.workflows
        assert not api_20.workflow_actions
        assert not api_20.workflow_triggers

    async def test_enums(self):
        """Test enums."""
        assert CustomFieldType(999) == CustomFieldType.UNKNOWN
        assert ShareLinkFileVersion("nope") == ShareLinkFileVersion.UNKNOWN


class TestConsumptionTemplates:
    """Consumption Templates test cases."""

    async def test_controller(self, api_20: Paperless):
        """Test controller."""
        assert isinstance(api_20.consumption_templates, ConsumptionTemplatesController)
        # test mixins
        assert hasattr(api_20.consumption_templates, "list")
        assert hasattr(api_20.consumption_templates, "get")
        assert hasattr(api_20.consumption_templates, "iterate")
        assert hasattr(api_20.consumption_templates, "one")
        assert not hasattr(api_20.consumption_templates, "create")
        assert not hasattr(api_20.consumption_templates, "update")
        assert not hasattr(api_20.consumption_templates, "delete")

    async def test_list(self, api_20: Paperless):
        """Test list."""
        items = await api_20.consumption_templates.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_20: Paperless):
        """Test get."""
        results = await api_20.consumption_templates.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, ConsumptionTemplate)

    async def test_iterate(self, api_20: Paperless):
        """Test iterate."""
        async for item in api_20.consumption_templates.iterate():
            assert isinstance(item, ConsumptionTemplate)

    async def test_one(self, api_20: Paperless):
        """Test one."""
        item = await api_20.consumption_templates.one(1)
        assert item
        assert isinstance(item, ConsumptionTemplate)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_20.consumption_templates.one(1337)


class TestCustomFields:
    """Custom Fields test cases."""

    async def test_controller(self, api_20: Paperless):
        """Test controller."""
        assert isinstance(api_20.custom_fields, CustomFieldsController)
        # test mixins
        assert hasattr(api_20.custom_fields, "list")
        assert hasattr(api_20.custom_fields, "get")
        assert hasattr(api_20.custom_fields, "iterate")
        assert hasattr(api_20.custom_fields, "one")
        assert hasattr(api_20.custom_fields, "create")
        assert hasattr(api_20.custom_fields, "update")
        assert hasattr(api_20.custom_fields, "delete")

    async def test_list(self, api_20: Paperless):
        """Test list."""
        items = await api_20.custom_fields.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_20: Paperless):
        """Test get."""
        results = await api_20.custom_fields.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, CustomField)

    async def test_iterate(self, api_20: Paperless):
        """Test iterate."""
        async for item in api_20.custom_fields.iterate():
            assert isinstance(item, CustomField)

    async def test_one(self, api_20: Paperless):
        """Test one."""
        item = await api_20.custom_fields.one(1)
        assert item
        assert isinstance(item, CustomField)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_20.custom_fields.one(1337)

    async def test_create(self, api_20: Paperless):
        """Test create."""
        new_name = "Created Custom Field"
        to_create = CustomFieldPost(name=new_name, data_type=CustomFieldType.BOOLEAN)
        created = await api_20.custom_fields.create(to_create)
        assert isinstance(created, CustomField)
        assert created.id == 9
        assert created.data_type == CustomFieldType.BOOLEAN

    async def test_udpate(self, api_20: Paperless):
        """Test update."""
        new_name = "Created Custom Field Update"
        to_update = await api_20.custom_fields.one(9)
        to_update.name = new_name
        updated = await api_20.custom_fields.update(to_update)
        assert isinstance(updated, CustomField)
        assert updated.name == new_name

    async def test_delete(self, api_20: Paperless):
        """Test delete."""
        to_delete = await api_20.custom_fields.one(9)
        deleted = await api_20.custom_fields.delete(to_delete)
        assert deleted
        # must raise as we deleted 9
        with pytest.raises(HTTPNotFound):
            await api_20.custom_fields.one(9)


class TestCustomFieldValues:
    """Custom Field Values test cases."""

    async def test_set(self, api_20: Paperless):
        """Test set."""
        document = await api_20.documents.one(2)
        assert isinstance(document, Document)
        assert isinstance(document.custom_fields, list)
        assert len(document.custom_fields) > 0
        for item in document.custom_fields:
            assert isinstance(item, CustomFieldValue)
        # manipulate custom fields
        fields = document.custom_fields
        new_field = CustomFieldValue(field=1, value=False)
        fields.append(new_field)
        document = await api_20.documents.custom_fields(document, fields)
        assert isinstance(document.custom_fields, list)
        for item in document.custom_fields:
            assert isinstance(item, CustomFieldValue)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_20.documents.custom_fields(1337, fields)


class TestShareLinks:
    """Share Links test cases."""

    async def test_controller(self, api_20: Paperless):
        """Test controller."""
        assert isinstance(api_20.share_links, ShareLinksController)
        # test mixins
        assert hasattr(api_20.share_links, "list")
        assert hasattr(api_20.share_links, "get")
        assert hasattr(api_20.share_links, "iterate")
        assert hasattr(api_20.share_links, "one")
        assert hasattr(api_20.share_links, "create")
        assert hasattr(api_20.share_links, "update")
        assert hasattr(api_20.share_links, "delete")

    async def test_list(self, api_20: Paperless):
        """Test list."""
        items = await api_20.share_links.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_20: Paperless):
        """Test get."""
        results = await api_20.share_links.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, ShareLink)

    async def test_iterate(self, api_20: Paperless):
        """Test iterate."""
        async for item in api_20.share_links.iterate():
            assert isinstance(item, ShareLink)

    async def test_one(self, api_20: Paperless):
        """Test one."""
        item = await api_20.share_links.one(1)
        assert item
        assert isinstance(item, ShareLink)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_20.share_links.one(1337)

    async def test_create(self, api_20: Paperless):
        """Test create."""
        new_document = 1
        new_expiration = datetime.datetime.now() + datetime.timedelta(30)
        new_file_version = ShareLinkFileVersion.ORIGINAL
        to_create = ShareLinkPost(
            document=new_document,
            expiration=new_expiration,
            file_version=new_file_version,
        )
        created = await api_20.share_links.create(to_create)
        assert isinstance(created, ShareLink)
        assert created.id == 6
        assert isinstance(created.expiration, datetime.datetime)
        assert created.file_version == ShareLinkFileVersion.ORIGINAL

    async def test_udpate(self, api_20: Paperless):
        """Test update."""
        new_expiration = None
        to_update = await api_20.share_links.one(6)
        to_update.expiration = new_expiration
        updated = await api_20.share_links.update(to_update)
        assert isinstance(updated, ShareLink)
        assert not updated.expiration

    async def test_delete(self, api_20: Paperless):
        """Test delete."""
        to_delete = await api_20.share_links.one(6)
        deleted = await api_20.share_links.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_20.share_links.one(6)
