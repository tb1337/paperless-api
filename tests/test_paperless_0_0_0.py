"""Paperless basic tests."""

import pytest
from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless
from pypaperless.controllers import CorrespondentsController, DocumentTypesController
from pypaperless.controllers.base import ResultPage
from pypaperless.models import Correspondent, CorrespondentPost, DocumentType, DocumentTypePost
from pypaperless.models.matching import MatchingAlgorithm


class TestPaperlessV00:
    """Common Paperless test cases."""

    async def test_init(self, api_00: Paperless):
        """Test init."""
        assert api_00._url
        assert api_00._token
        assert api_00._request_opts
        assert not api_00._session
        assert api_00._initialized

    async def test_features(self, api_00: Paperless):
        """Test features."""
        # basic class has no features
        assert api_00.features == 0
        assert not api_00.storage_paths
        assert not api_00.consumption_templates
        assert not api_00.custom_fields
        assert not api_00.share_links
        assert not api_00.workflows
        assert not api_00.workflow_actions
        assert not api_00.workflow_triggers

    async def test_correspondents(self, api_00: Paperless):
        """Test correspondents."""
        assert isinstance(api_00.correspondents, CorrespondentsController)
        # test mixins
        assert getattr(api_00.correspondents, "list")
        assert getattr(api_00.correspondents, "get")
        assert getattr(api_00.correspondents, "iterate")
        assert getattr(api_00.correspondents, "one")
        assert getattr(api_00.correspondents, "create")
        assert getattr(api_00.correspondents, "update")
        assert getattr(api_00.correspondents, "delete")

    async def test_correspondents_list(self, api_00: Paperless):
        """Test correspondents list."""
        items = await api_00.correspondents.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_correspondents_get(self, api_00: Paperless):
        """Test correspondents get."""
        results = await api_00.correspondents.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, Correspondent)

    async def test_correspondents_iterate(self, api_00: Paperless):
        """Test correspondents iterate."""
        async for item in api_00.correspondents.iterate():
            assert isinstance(item, Correspondent)

    async def test_correspondents_one(self, api_00: Paperless):
        """Test correspondents one."""
        item = await api_00.correspondents.one(1)
        assert item
        assert isinstance(item, Correspondent)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.correspondents.one(1337)

    async def test_correspondents_create(self, api_00: Paperless):
        """Test correspondents create."""
        new_name = "Created Correspondent"
        to_create = CorrespondentPost(name=new_name)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = CorrespondentPost(
            name=new_name,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_00.correspondents.create(to_create)
        assert isinstance(created, Correspondent)
        assert created.id == 6
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_correspondents_udpate(self, api_00: Paperless):
        """Test correspondents update."""
        new_name = "Created Correspondent Update"
        to_update = await api_00.correspondents.one(6)
        to_update.name = new_name
        updated = await api_00.correspondents.update(to_update)
        assert isinstance(updated, Correspondent)
        assert updated.name == new_name

    async def test_correspondent_delete(self, api_00: Paperless):
        """Test correspondent delete."""
        to_delete = await api_00.correspondents.one(6)
        deleted = await api_00.correspondents.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_00.correspondents.one(6)

    async def test_document_types(self, api_00: Paperless):
        """Test document_types."""
        assert isinstance(api_00.document_types, DocumentTypesController)
        # test mixins
        assert getattr(api_00.document_types, "list")
        assert getattr(api_00.document_types, "get")
        assert getattr(api_00.document_types, "iterate")
        assert getattr(api_00.document_types, "one")
        assert getattr(api_00.document_types, "create")
        assert getattr(api_00.document_types, "update")
        assert getattr(api_00.document_types, "delete")

    async def test_document_types_list(self, api_00: Paperless):
        """Test document_types list."""
        items = await api_00.document_types.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)

    async def test_document_types_get(self, api_00: Paperless):
        """Test document_types get."""
        results = await api_00.document_types.get()
        assert isinstance(results, ResultPage)
        assert results.current_page == 1
        assert not results.next_page  # there is 1 page in sample data
        assert results.last_page == 1  # there is 1 page in sample data
        assert isinstance(results.items, list)
        for item in results.items:
            assert isinstance(item, DocumentType)

    async def test_document_types_iterate(self, api_00: Paperless):
        """Test document_types iterate."""
        async for item in api_00.document_types.iterate():
            assert isinstance(item, DocumentType)

    async def test_document_types_one(self, api_00: Paperless):
        """Test document_types one."""
        item = await api_00.document_types.one(1)
        assert item
        assert isinstance(item, DocumentType)
        # must raise as 1337 doesn't exist
        with pytest.raises(HTTPNotFound):
            await api_00.document_types.one(1337)

    async def test_document_types_create(self, api_00: Paperless):
        """Test document_types create."""
        new_name = "Created Document Type"
        to_create = DocumentTypePost(name=new_name)
        # test mixins, and their defaults
        assert to_create.is_insensitive is True
        assert to_create.match == ""
        assert to_create.matching_algorithm == MatchingAlgorithm.NONE
        # test default override
        to_create = DocumentTypePost(
            name=new_name,
            matching_algorithm=MatchingAlgorithm.FUZZY,
        )
        assert to_create.matching_algorithm == MatchingAlgorithm.FUZZY
        # actually call the create endpoint
        created = await api_00.document_types.create(to_create)
        assert isinstance(created, DocumentType)
        assert created.id == 6
        assert created.matching_algorithm == MatchingAlgorithm.FUZZY

    async def test_document_types_udpate(self, api_00: Paperless):
        """Test document_types update."""
        new_name = "Created Document Type Update"
        to_update = await api_00.document_types.one(6)
        to_update.name = new_name
        updated = await api_00.document_types.update(to_update)
        assert isinstance(updated, DocumentType)
        assert updated.name == new_name

    async def test_document_types_delete(self, api_00: Paperless):
        """Test document_types delete."""
        to_delete = await api_00.document_types.one(6)
        deleted = await api_00.document_types.delete(to_delete)
        assert deleted
        # must raise as we deleted 6
        with pytest.raises(HTTPNotFound):
            await api_00.document_types.one(6)
