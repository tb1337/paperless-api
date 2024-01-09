"""Paperless basic tests."""

from pypaperless import Paperless
from pypaperless.controllers import CorrespondentsController


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
        assert api_00.storage_paths is None
        assert api_00.consumption_templates is None
        assert api_00.custom_fields is None
        assert api_00.share_links is None
        assert api_00.workflows is None
        assert api_00.workflow_actions is None
        assert api_00.workflow_triggers is None

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
        # test list
        items = await api_00.correspondents.list()
        assert isinstance(items, list)
        assert len(items) > 0
        for item in items:
            assert isinstance(item, int)
