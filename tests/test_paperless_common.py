"""Paperless common tests."""

from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum

import pytest

from pypaperless import Paperless, PaperlessSession
from pypaperless.exceptions import BadJsonResponse, JsonResponseWithError, RequestException
from pypaperless.models.common import (
    CustomFieldType,
    MatchingAlgorithmType,
    ShareLinkFileVersionType,
    TaskStatusType,
    WorkflowActionType,
    WorkflowTriggerSourceType,
    WorkflowTriggerType,
)
from pypaperless.models.utils import dict_value_to_object, object_to_dict_value
from tests.const import PAPERLESS_TEST_TOKEN, PAPERLESS_TEST_URL

from . import PaperlessSessionMock

# mypy: ignore-errors
# pylint: disable=protected-access


class TestPaperless:
    """Paperless common test cases."""

    async def test_init(self, api_obj: Paperless):
        """Test init."""
        await api_obj.initialize()
        assert api_obj.is_initialized
        await api_obj.close()

    async def test_context(self, api_obj: Paperless):
        """Test context."""
        async with api_obj:
            assert api_obj.is_initialized

    async def test_request(self):
        """Test generate request."""
        # we need to use an unmocked PaperlessSession.request() method
        # simply don't initialize Paperless and everything will be fine
        api = Paperless(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_TOKEN,
        )

        async with api.request("get", "https://example.org") as res:
            assert res.status

        # last but not least, we test sending a form to test the converter
        form_data = {
            "none_field": None,
            "str_field": "Hello Bytes!",
            "bytes_field": b"Hello String!",
            "tuple_field": (b"Document Content", "filename.pdf"),
            "int_field": 23,
            "float_field": 13.37,
            "int_list": [1, 1, 2, 3, 5, 8, 13],
            "dict_field": {"dict_str_field": "str", "dict_int_field": 2},
        }
        async with api.request("post", "https://example.org", form=form_data) as res:
            assert res.status

        # test non-existing request
        with pytest.raises(RequestException):
            async with api.request("get", "does-not-exist.example") as res:
                pass

        # session is still open
        await api.close()

    async def test_request_json(self, api_obj: Paperless):
        """Test requests."""
        # test 400 bad request with error payload
        with pytest.raises(JsonResponseWithError):
            await api_obj.request_json(
                "get",
                "/test/http/400/",
                params={
                    "response_content": '{"error":"sample message"}',
                    "content_type": "application/json",
                },
            )

        # test 200 ok with wrong content type
        with pytest.raises(BadJsonResponse):
            await api_obj.request_json(
                "get",
                "/test/http/200/",
                params={
                    "response_content": '{"error":"sample message"}',
                    "content_type": "text/plain",
                },
            )

        # test 200 ok with correct content type, but no json payload
        with pytest.raises(BadJsonResponse):
            await api_obj.request_json(
                "get",
                "/test/http/200/",
                params={
                    "response_content": "test 1337 5 23 42 1337",
                    "content_type": "application/json",
                },
            )

    async def test_create_url(self):
        """Test create url util."""
        create_url = PaperlessSession._create_base_url

        # test default ssl
        url = create_url("hostname")
        assert url.host == "hostname"
        assert url.port == 443

        # test enforce http
        url = create_url("http://hostname")
        assert url.port == 80

        # test non-http scheme
        url = create_url("ftp://hostname")
        assert url.scheme == "https"

        # should be https even on just setting a port number
        url = create_url("hostname:80")
        assert url.scheme == "https"

        # test api/api url
        url = create_url("hostname/api/api/")
        assert f"{url}" == "https://hostname/api/api"

    async def test_generate_api_token(self, api_obj: Paperless):
        """Test generate api token."""
        test_token = "abcdef1234567890"

        session = PaperlessSessionMock(PAPERLESS_TEST_URL, "")

        # test successful token creation
        session.params = {
            "response_content": f'{{"token":"{test_token}"}}',
        }
        token = await api_obj.generate_api_token(
            PAPERLESS_TEST_URL, "test-user", "not-so-secret-password", session
        )
        assert token == test_token

        # test token creation with wrong json answer
        with pytest.raises(BadJsonResponse):
            session.params = {
                "response_content": '{"bla":"any string"}',
            }
            token = await api_obj.generate_api_token(
                PAPERLESS_TEST_URL, "test-user", "not-so-secret-password", session
            )

        # test error 400
        with pytest.raises(JsonResponseWithError):
            session.params = {
                "response_content": '{"non_field_errors":["Unable to log in."]}',
                "status": "400",
            }
            token = await api_obj.generate_api_token(
                PAPERLESS_TEST_URL, "test-user", "not-so-secret-password", session
            )

        # general exception
        with pytest.raises(Exception):
            session.params = {
                "response_content": "no json",
                "status": "500",
            }
            token = await api_obj.generate_api_token(
                PAPERLESS_TEST_URL, "test-user", "not-so-secret-password", session
            )

    async def test_types(self):
        """Test types."""
        never_str = "!never_existing_type!"
        never_int = 99952342
        assert CustomFieldType(never_str) == CustomFieldType.UNKNOWN
        assert MatchingAlgorithmType(never_int) == MatchingAlgorithmType.UNKNOWN
        assert ShareLinkFileVersionType(never_str) == ShareLinkFileVersionType.UNKNOWN
        assert TaskStatusType(never_str) == TaskStatusType.UNKNOWN
        assert WorkflowActionType(never_int) == WorkflowActionType.UNKNOWN
        assert WorkflowTriggerType(never_int) == WorkflowTriggerType.UNKNOWN
        assert WorkflowTriggerSourceType(never_int) == WorkflowTriggerSourceType.UNKNOWN

    async def test_dataclass_conversion(self):
        """Test dataclass utils."""

        class _Status(Enum):
            """Test enum."""

            ACTIVE = 1
            INACTIVE = 2
            UNKNOWN = -1

            @classmethod
            def _missing_(cls: type, *_: object):
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

        data = {
            field.name: dict_value_to_object(
                f"_Person.{__name__}.{field.name}",
                raw_data.get(field.name),
                field.type,
                field.default,
            )
            for field in fields(_Person)
        }
        res = _Person(**data)

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

        # back conversion
        back = {field.name: object_to_dict_value(getattr(res, field.name)) for field in fields(res)}

        assert isinstance(back["friends"][0]["age"], int)  # was str in the source dict
