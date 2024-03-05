"""Paperless common tests."""

from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum

import aiohttp
from aiohttp.http_exceptions import InvalidURLError
from aioresponses import aioresponses
import pytest

from pypaperless import Paperless
from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import (
    BadJsonResponse,
    DraftNotSupported,
    JsonResponseWithError,
    RequestException,
)
from pypaperless.models import Page
from pypaperless.models.base import HelperBase, PaperlessModel
from pypaperless.models.common import (
    CustomFieldType,
    MatchingAlgorithmType,
    ShareLinkFileVersionType,
    TaskStatusType,
    WorkflowActionType,
    WorkflowTriggerSourceType,
    WorkflowTriggerType,
)
from pypaperless.models.mixins import helpers
from pypaperless.models.utils import dict_value_to_object, object_to_dict_value
from tests.const import (
    PAPERLESS_TEST_PASSWORD,
    PAPERLESS_TEST_TOKEN,
    PAPERLESS_TEST_URL,
    PAPERLESS_TEST_USER,
)

from .data import PATCHWORK

# mypy: ignore-errors


class TestPaperless:
    """Paperless common test cases."""

    async def test_init(self, resp: aioresponses, api: Paperless) -> None:
        """Test init."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=200,
            payload=PATCHWORK["paths"],
        )
        await api.initialize()
        assert api.is_initialized
        await api.close()

    async def test_context(self, resp: aioresponses, api: Paperless) -> None:
        """Test context."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=200,
            payload=PATCHWORK["paths"],
        )
        async with api:
            assert api.is_initialized

    async def test_request(self, resp: aioresponses) -> None:
        """Test generate request."""
        # we need to use an unmocked PaperlessSession.request() method
        # simply don't initialize Paperless and everything will be fine
        api = Paperless(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_TOKEN,
        )

        # test ordinary 200
        resp.get(
            PAPERLESS_TEST_URL,
            status=200,
        )
        async with api.request("get", PAPERLESS_TEST_URL) as res:
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
        resp.post(
            PAPERLESS_TEST_URL,
            status=200,
        )
        async with api.request("post", PAPERLESS_TEST_URL, form=form_data) as res:
            assert res.status

        # test non-existing request
        resp.get(
            PAPERLESS_TEST_URL,
            exception=InvalidURLError,
        )
        with pytest.raises(RequestException):
            async with api.request("get", PAPERLESS_TEST_URL) as res:
                pass

        # session is still open
        await api.close()

    async def test_request_json(self, resp: aioresponses, api: Paperless) -> None:
        """Test requests."""
        # test 400 bad request with error payload
        resp.get(
            f"{PAPERLESS_TEST_URL}/400-json-error-payload",
            status=400,
            headers={"Content-Type": "application/json"},
            payload={"error": "sample message"},
        )
        with pytest.raises(JsonResponseWithError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/400-json-error-payload")

        # test 200 ok with wrong content type
        resp.get(
            f"{PAPERLESS_TEST_URL}/200-text-error-payload",
            status=200,
            headers={"Content-Type": "text/plain"},
            body='{"error": "sample message"}',
        )
        with pytest.raises(BadJsonResponse):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-text-error-payload")

        # test 200 ok with correct content type, but no json payload
        resp.get(
            f"{PAPERLESS_TEST_URL}/200-json-text-body",
            status=200,
            headers={"Content-Type": "application/json"},
            body="test 5 23 42 1337",
        )
        with pytest.raises(BadJsonResponse):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-json-text-body")

    async def test_create_url(self) -> None:
        """Test create url util."""
        create_url = Paperless._create_base_url  # pylint: disable=protected-access

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

    async def test_generate_api_token(self, resp: aioresponses, api: Paperless) -> None:
        """Test generate api token."""
        session = aiohttp.ClientSession()

        # test successful token creation
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=200,
            payload=PATCHWORK["token"],
        )
        token = await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
            session,
        )
        assert token == PAPERLESS_TEST_TOKEN

        # test token creation with wrong json answer
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=200,
            payload={"blah": "any string"},
        )
        with pytest.raises(BadJsonResponse):
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
                session,
            )

        # test error 400
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=400,
            payload={"non_field_errors": ["Unable to log in."]},
        )
        with pytest.raises(JsonResponseWithError):
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
                session,
            )

        # general exception
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=500,
            body="no json",
        )
        with pytest.raises(Exception):
            session.params = {
                "response_content": "no json",
                "status": "500",
            }
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
                session,
            )

    async def test_types(self) -> None:
        """Test types."""
        never_str = "!never_existing_type!"
        never_int = 99952342
        assert PaperlessResource(never_str) == PaperlessResource.UNKNOWN
        assert CustomFieldType(never_str) == CustomFieldType.UNKNOWN
        assert MatchingAlgorithmType(never_int) == MatchingAlgorithmType.UNKNOWN
        assert ShareLinkFileVersionType(never_str) == ShareLinkFileVersionType.UNKNOWN
        assert TaskStatusType(never_str) == TaskStatusType.UNKNOWN
        assert WorkflowActionType(never_int) == WorkflowActionType.UNKNOWN
        assert WorkflowTriggerType(never_int) == WorkflowTriggerType.UNKNOWN
        assert WorkflowTriggerSourceType(never_int) == WorkflowTriggerSourceType.UNKNOWN

    async def test_dataclass_conversion(self) -> None:
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
            meta: dict[str, str]

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
            "meta": {"hairs": "blonde", "eyes": "blue", "loves": "Python"},
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
        assert isinstance(back["meta"], dict)

    async def test_pages_object(self, api: Paperless) -> None:
        """Test pages."""

        @dataclass(init=False)
        class TestResource(PaperlessModel):
            """Test Resource."""

            id: int | None = None

        data = {
            "count": 0,
            "current_page": 1,
            "page_size": 25,
            "next": "any.url",
            "previous": None,
            "all": [],
            "results": [],
        }

        for i in range(1, 101):
            data["count"] += 1
            data["all"].append(i)
            data["results"].append({"id": i})

        page = Page.create_with_data(api, data=data, fetched=True)
        page._resource_cls = TestResource  # pylint: disable=protected-access

        assert isinstance(page, Page)
        assert page.current_count == 100
        for item in page:
            assert isinstance(item, TestResource)

        # check first page
        assert not page.has_previous_page
        assert page.has_next_page
        assert not page.is_last_page
        assert page.last_page == 4
        assert page.next_page == 2
        assert page.previous_page is None

        # check inner page
        page.previous = "any.url"
        page.current_page = 3

        assert page.previous_page is not None
        assert page.next_page is not None
        assert not page.is_last_page

        # check last page
        page.next = None
        page.current_page = 4

        assert page.next_page is None
        assert page.is_last_page

    async def test_draft_exc(self, api: Paperless) -> None:
        """Test draft not supported."""

        @dataclass(init=False)
        class TestResource(PaperlessModel):
            """Test Resource."""

        class TestHelper(HelperBase, helpers.DraftableMixin):
            """Test Helper."""

            _api_path = "any.url"
            _resource = "test"  # type: ignore
            # draft_cls - we "forgot" to set a draft class, which will raise an exception ...
            _resource_cls = TestResource

        helper = TestHelper(api)
        with pytest.raises(DraftNotSupported):
            # ... there it is
            helper.draft()  # noqa
