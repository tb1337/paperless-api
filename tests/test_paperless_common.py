"""Paperless common tests."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

import pytest

from pypaperless import Paperless
from pypaperless.errors import BadRequestException, ControllerConfusion, DataNotExpectedException
from pypaperless.util import (
    create_url_from_input,
    dataclass_from_dict,
    dataclass_to_dict,
    update_dataclass,
)
from tests.const import PAPERLESS_TEST_REQ_OPTS, PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL


class TestPaperless:
    """Paperless common test cases."""

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

    async def test_create_url(self):
        """Test create url util."""
        # test default ssl
        url = create_url_from_input("hostname")
        assert url.host == "hostname"
        assert url.port == 443

        # test if api-path is added
        assert url.name == "api"

        # test full url string
        assert f"{url}" == "https://hostname/api"

        # test enforce http
        url = create_url_from_input("http://hostname")
        assert url.port == 80

        # test non-http scheme
        url = create_url_from_input("ftp://hostname")
        assert url.scheme == "https"

        # should be https even on just setting a port number
        url = create_url_from_input("hostname:80")
        assert url.scheme == "https"

        # test api/api url
        url = create_url_from_input("hostname/api/api/")
        assert f"{url}" == "https://hostname/api/api"

        # test with path and check if "api" is added
        url = create_url_from_input("hostname/path/to/paperless")
        assert f"{url}" == "https://hostname/path/to/paperless/api"

    async def test_dataclass_conversion(self):
        """Test dataclass utils."""

        class _Status(Enum):
            """Test enum."""

            ACTIVE = 1
            INACTIVE = 2
            UNKNOWN = -1

            @classmethod
            def _missing_(cls: type, value: object):  # noqa ARG003
                """Set default."""
                return cls.UNKNOWN

        @dataclass
        class _Friend:
            """Test class."""

            name: str
            age: int

        @dataclass
        class _Person:
            """Test class."""

            name: str
            age: int
            height: float
            birth: date
            last_login: datetime
            friends: list[_Friend] | None
            deleted: datetime | None
            is_deleted: bool
            status: _Status
            file: bytes

        raw_data = {
            "name": "Lee Tobi, Sajangnim",
            "age": 38,
            "height": 1.76,
            "birth": "1986-05-23",
            "last_login": "2023-08-08T06:06:35.495972Z",
            "is_deleted": False,
            "friends": [
                {
                    "name": "Erika",
                    "age": "50",  # this should be int, check "back conversion" at bottom
                },
                {
                    "name": "Reinhard",
                    "age": 40,
                },
            ],
            "status": 1,
            "file": b"5-23-42-666-0815-1337",
        }

        res = dataclass_from_dict(_Person, raw_data)

        assert isinstance(res.name, str)
        assert isinstance(res.age, int)
        assert isinstance(res.height, float)
        assert isinstance(res.birth, date)
        assert isinstance(res.last_login, datetime)
        assert isinstance(res.friends, list)
        assert isinstance(res.friends[0], _Friend)
        assert isinstance(res.friends[0].age, int)
        assert isinstance(res.friends[1].age, int)
        assert res.deleted is None
        assert res.is_deleted is False
        assert isinstance(res.status, _Status)
        assert isinstance(res.file, bytes)

        update_dataclass(
            res,
            {
                "deleted": datetime.now(),
                "is_deleted": True,
            },
        )

        assert isinstance(res.deleted, datetime)
        assert res.is_deleted

        assert res.status == _Status.ACTIVE
        update_dataclass(res, {"status": 100})
        assert isinstance(res.status, _Status)
        assert res.status == _Status.UNKNOWN

        # back conversion
        back = dataclass_to_dict(res)

        assert isinstance(back["friends"][0]["age"], int)  # was str in the source dict
