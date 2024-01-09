"""Paperless basic tests."""


class TestPaperlessBasic:
    """Common Paperless test cases."""

    async def test_00_init(self, api_v0_0_0):
        """Initialize."""
        await api_v0_0_0.initialize()

    async def test_99_del(self, api_v0_0_0):
        """Close."""
        await api_v0_0_0.close()
