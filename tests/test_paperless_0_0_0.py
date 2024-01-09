"""Paperless basic tests."""

from pypaperless import Paperless


class TestPaperlessV1x0x0:
    """Common Paperless test cases."""

    async def test_init(self, api_00: Paperless):
        """Test init."""
        assert api_00._url
        assert api_00._token
        assert api_00._request_opts
        assert not api_00._session
        assert api_00._initialized is True
        assert api_00.logger.debug("Test successful.") is None

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
