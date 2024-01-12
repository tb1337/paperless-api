"""Paperless v1.8.0 tests."""

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless
from pypaperless.const import PaperlessFeature
from pypaperless.controllers import StoragePathsController
from pypaperless.controllers.base import ResultPage
from pypaperless.models import StoragePath, StoragePathPost
from pypaperless.models.matching import MatchingAlgorithm


class TestBeginPaperless:
    """Paperless v1.8.0 test cases."""

    async def test_init(self, api_18: Paperless):
        """Test init."""
        assert api_18._token
        assert api_18._request_opts
        assert not api_18._session
        # test properties
        assert api_18.url
        assert api_18.is_initialized

    async def test_features(self, api_18: Paperless):
        """Test features."""
        # basic class has no features
        assert PaperlessFeature.CONTROLLER_STORAGE_PATHS in api_18.features
        assert api_18.storage_paths
        assert not api_18.consumption_templates
        assert not api_18.custom_fields
        assert not api_18.share_links
        assert not api_18.workflows
        assert not api_18.workflow_actions
        assert not api_18.workflow_triggers


class TestStoragePaths:
    """Storage Paths test cases."""

    async def test_controller(self, api_18: Paperless):
        """Test controller."""
        assert isinstance(api_18.storage_paths, StoragePathsController)
        # test mixins
        assert hasattr(api_18.storage_paths, "list")
        assert hasattr(api_18.storage_paths, "get")
        assert hasattr(api_18.storage_paths, "iterate")
        assert hasattr(api_18.storage_paths, "one")
        assert hasattr(api_18.storage_paths, "create")
        assert hasattr(api_18.storage_paths, "update")
        assert hasattr(api_18.storage_paths, "delete")

    async def test_list(self, api_18: Paperless):
        """Test list."""
        items = await api_18.storage_paths.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_get(self, api_18: Paperless):
        """Test get."""
        results = await api_18.storage_paths.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, StoragePath)

    async def test_iterate(self, api_18: Paperless):
        """Test iterate."""
        async for item in api_18.storage_paths.iterate():
            assert isinstance(item, StoragePath)

    async def test_one(self, api_18: Paperless):
        """Test one."""
        item = await api_18.storage_paths.one(1)
        assert item
        assert isinstance(item, StoragePath)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_18.storage_paths.one(1337)

    async def test_create(self, api_18: Paperless):
        """Test create."""
        new_name = "Created Storage Path"
        new_path = "test/test/{doc_pk}"
        to_create = StoragePathPost(name=new_name, path=new_path)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = StoragePathPost(
            name=new_name,
            path=new_path,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_18.storage_paths.create(to_create)
        assert isinstance(created, StoragePath)
        assert created.id == 4
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_udpate(self, api_18: Paperless):
        """Test update."""
        new_name = "Created Storage Path Update"
        to_update = await api_18.storage_paths.one(4)
        to_update.name = new_name
        updated = await api_18.storage_paths.update(to_update)
        assert isinstance(updated, StoragePath)
        assert updated.name == new_name

    async def test_delete(self, api_18: Paperless):
        """Test delete."""
        to_delete = await api_18.storage_paths.one(4)
        deleted = await api_18.storage_paths.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_18.storage_paths.one(4)
