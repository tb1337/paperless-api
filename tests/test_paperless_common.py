"""Paperless common tests."""


import pytest

from pypaperless import Paperless
from pypaperless.errors import BadRequestException, ControllerConfusion, DataNotExpectedException
from tests.const import PAPERLESS_TEST_REQ_OPTS, PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL


class TestPaperless:
    """Paperless v1.8.0 test cases."""

    async def test_init(self, api: Paperless):
        """Test init."""
        await api.initialize()
        assert api.is_initialized
        await api.close()

    async def test_context(self, api: Paperless):
        """Test context."""
        async with api:
            assert api.is_initialized

    async def test_confusion(self, api: Paperless):
        """Test confusion."""
        # it is a very specific case and shouldn't ever happen
        # set a version which doesn't exist in the router patchwork
        api.version = "999.99.99"
        # on that version PyPaperless expects a WorkflowsController (999 > 2.3.0)
        # but the router will fall back to version 0.0.0 data
        # this will result in an exception, or ControllerConfusion
        with pytest.raises(ControllerConfusion):
            async with api:
                # boom
                pass

    async def test_requests(self, api: Paperless):
        """Test requests."""
        # request_json
        with pytest.raises(BadRequestException):
            await api.request_json("get", "/_bad_request/")
        with pytest.raises(DataNotExpectedException):
            await api.request_json("get", "/_no_json/")
        # request_file
        with pytest.raises(BadRequestException):
            await api.request_file("get", "/_bad_request/")

    async def test_generate_request(self):
        """Test generate request."""
        # we need to use an unmocked generate_request() method
        # simply don't initialize Paperless and everything will be fine
        api = Paperless(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_TOKEN,
            request_opts=PAPERLESS_TEST_REQ_OPTS,
        )

        async with api.generate_request("get", "https://example.org") as res:
            assert res.status

        # last but not least, we test sending a form to test the converter
        form_data = {
            "string": "Hello Bytes!",
            "bytes": b"Hello String!",
            "int": 23,
            "float": 13.37,
            "list": [1, 1, 2, 3, 5, 8, 13],
            "dict": {"str": "str", "int": 2},
        }
        async with api.generate_request("post", "https://example.org", form=form_data) as res:
            assert res.status
