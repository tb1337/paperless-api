"""Paperless common tests."""

from dataclasses import dataclass, fields
from datetime import date, datetime
from enum import Enum
from typing import TypedDict

import aiohttp
import pytest
from aioresponses import aioresponses

from pypaperless import Paperless
from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.exceptions import (
    BadJsonResponseError,
    DraftNotSupportedError,
    InitializationError,
    JsonResponseWithError,
    PaperlessConnectionError,
    PaperlessForbiddenError,
    PaperlessInactiveOrDeletedError,
    PaperlessInvalidTokenError,
)
from pypaperless.models import Page
from pypaperless.models.base import HelperBase, PaperlessModel
from pypaperless.models.common import (
    CustomFieldDateValue,
    CustomFieldSelectValue,
    CustomFieldType,
    MatchingAlgorithmType,
    ShareLinkFileVersionType,
    StatusType,
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
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=200,
            payload=PATCHWORK["paths"],
        )
        await api.initialize()
        assert api.is_initialized
        await api.close()

    async def test_context(self, resp: aioresponses, api: Paperless) -> None:
        """Test context."""
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=500,
            payload=PATCHWORK["paths"],
        )
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=200,
            payload=PATCHWORK["paths"],
        )
        async with api:
            assert api.is_initialized

    async def test_properties(self, api: Paperless) -> None:
        """Test properties."""
        # version must be None in this case, as we test against
        # an uninitialized Paperless object
        assert api.host_version is None

        assert api.base_url == PAPERLESS_TEST_URL
        assert isinstance(api.local_resources, set)
        assert isinstance(api.remote_resources, set)

    async def test_helper_avail_00(self, api_00: Paperless) -> None:
        """Test availability of helpers against specific api version."""
        assert not api_00.custom_fields.is_available
        assert not api_00.workflows.is_available

    async def test_helper_avail_latest(self, api_latest: Paperless) -> None:
        """Test availability of helpers against specific api version."""
        assert api_latest.custom_fields.is_available
        assert api_latest.workflows.is_available

    async def test_init_error(self, resp: aioresponses, api: Paperless) -> None:
        """Test initialization error."""
        # simulate connection due no configuration error
        with pytest.raises(PaperlessConnectionError):
            await api.initialize()

        # http status error
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=500,
            payload=PATCHWORK["paths"],
        )
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=401,
            body="any html",
        )
        with pytest.raises(PaperlessInvalidTokenError):
            await api.initialize()

        # http 401 - inactive or deleted user
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=500,
            payload=PATCHWORK["paths"],
        )
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=401,
            payload={"detail": "User is inactive"},
        )
        with pytest.raises(PaperlessInactiveOrDeletedError):
            await api.initialize()

        # http status forbidden
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=500,
            payload=PATCHWORK["paths"],
        )
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=403,
            body="any html",
        )
        with pytest.raises(PaperlessForbiddenError):
            await api.initialize()

        # http ok, wrong payload
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['api_schema']}",
            status=500,
            payload=PATCHWORK["paths"],
        )
        resp.get(
            f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            status=200,
            body="any html",
        )
        with pytest.raises(InitializationError):
            await api.initialize()

    @pytest.mark.parametrize(
        "exception_cls",
        [
            PaperlessConnectionError,
            PaperlessInvalidTokenError,
            PaperlessInactiveOrDeletedError,
            PaperlessForbiddenError,
        ],
    )
    async def test_errors_are_backwards_compatible(self, exception_cls: type) -> None:
        """Test, if new errors are backwards compatible."""
        assert issubclass(exception_cls, InitializationError)

    async def test_jsonresponsewitherror(self) -> None:
        """Test JsonResponseWithError."""
        try:
            payload = "sample string"
            raise JsonResponseWithError(payload)  # noqa: TRY301
        except JsonResponseWithError as exc:
            assert exc.args[0] == "Paperless [error]: sample string"  # noqa: PT017

        try:
            payload = {"failure": "something failed"}
            raise JsonResponseWithError(payload)  # noqa: TRY301
        except JsonResponseWithError as exc:
            assert exc.args[0] == "Paperless [failure]: something failed"  # noqa: PT017

        try:
            payload = {"error": ["that", "should", "have", "been", "never", "happened"]}
            raise JsonResponseWithError(payload)  # noqa: TRY301
        except JsonResponseWithError as exc:
            assert exc.args[0] == "Paperless [error]: that"  # noqa: PT017

        try:
            payload = [{"some": [[{"weird": {"error": ["occurred"]}}]]}]
            raise JsonResponseWithError(payload)  # noqa: TRY301
        except JsonResponseWithError as exc:
            assert exc.args[0] == "Paperless [some -> weird -> error]: occurred"  # noqa: PT017

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
        with pytest.raises(BadJsonResponseError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-text-error-payload")

        # test 200 ok with correct content type, but no json payload
        resp.get(
            f"{PAPERLESS_TEST_URL}/200-json-text-body",
            status=200,
            headers={"Content-Type": "application/json"},
            body="test 5 23 42 1337",
        )
        with pytest.raises(BadJsonResponseError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-json-text-body")

    async def test_create_url(self) -> None:
        """Test create url util."""
        create_url = Paperless._create_base_url  # pylint: disable=protected-access

        # test default ssl
        url = create_url("hostname")
        assert f"{url.host}" == "hostname"
        assert int(url.port) == 443

        # test enforce http
        url = create_url("http://hostname")
        assert int(url.port) == 80

        # test non-http scheme
        url = create_url("ftp://hostname")
        assert f"{url.scheme}" == "https"

        # should be https even on just setting a port number
        url = create_url("hostname:80")
        assert f"{url.scheme}" == "https"

        # test api/api url
        url = create_url("hostname/api/api/")
        assert f"{url}" == "https://hostname/api/api"

        # test slashes
        url = create_url("hostname/api/endpoint///")
        assert f"{url}" == "https://hostname/api/endpoint"

    async def test_generate_api_token(self, resp: aioresponses, api: Paperless) -> None:
        """Test generate api token."""
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
        )
        assert token == PAPERLESS_TEST_TOKEN

        # test token creation with wrong json answer
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=200,
            payload={"blah": "any string"},
        )
        with pytest.raises(BadJsonResponseError):
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
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
            )

        # general exception
        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            exception=ValueError,
        )
        with pytest.raises(ValueError):  # noqa: PT011
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
            )

    async def test_generate_api_token_with_session(
        self, resp: aioresponses, api: Paperless
    ) -> None:
        """Test generate api token with custom session."""
        session = aiohttp.ClientSession()

        resp.post(
            f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            status=200,
            payload=PATCHWORK["token"],
        )
        token = await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
            session=session,
        )
        assert token == PAPERLESS_TEST_TOKEN

    async def test_types(self) -> None:
        """Test types."""
        never_str = "!never_existing_type!"
        never_int = 99952342
        assert PaperlessResource(never_str) == PaperlessResource.UNKNOWN
        assert CustomFieldType(never_str) == CustomFieldType.UNKNOWN
        assert MatchingAlgorithmType(never_int) == MatchingAlgorithmType.UNKNOWN
        assert ShareLinkFileVersionType(never_str) == ShareLinkFileVersionType.UNKNOWN
        assert StatusType(never_str) == StatusType.UNKNOWN
        assert TaskStatusType(never_str) == TaskStatusType.UNKNOWN
        assert WorkflowActionType(never_int) == WorkflowActionType.UNKNOWN
        assert WorkflowTriggerType(never_int) == WorkflowTriggerType.UNKNOWN
        assert WorkflowTriggerSourceType(never_int) == WorkflowTriggerSourceType.UNKNOWN

    async def test_custom_field_value_types(self) -> None:
        """Test custom field value types."""
        # check date transformation
        test = CustomFieldDateValue(value="1900-01-02T02:03:04")
        assert isinstance(test.value, datetime)

        # check label properties
        test = CustomFieldSelectValue(
            value="id2",
            extra_data={
                "select_options": [
                    {"id": "id1", "label": "label1"},
                    {"id": "id2", "label": "label2"},
                ]
            },
        )
        assert isinstance(test.labels, list)
        assert test.label == "label2"

        # test fail
        test.extra_data = None
        assert test.label is None

    async def test_dataclass_conversion(self) -> None:  # pylint: disable=too-many-statements
        """Test dataclass utils."""

        class SomeStatus(Enum):
            """Test enum."""

            ACTIVE = 1
            INACTIVE = 2
            UNKNOWN = -1

            @classmethod
            def _missing_(cls: "SomeStatus", *_: object) -> "SomeStatus":
                """Set default."""
                return cls.UNKNOWN

        class SomeNestedExtraData(TypedDict):
            """Test nested TypedDict."""

            ustr: str | None
            uany: int | str | bool | None

        class SomeExtraData(TypedDict):
            """Test TypedDict."""

            a_str: str
            a_dict: dict[str, str]
            a_list: list[str]
            a_typeddict: SomeNestedExtraData

        @dataclass
        class SomeFriend:
            """Test class."""

            name: str
            age: int

            @classmethod
            def from_dict(cls, data: dict) -> "SomeFriend":
                """Test from_dict stuff."""
                return cls(name=str(data.get("name")), age=int(data.get("age")))

        @dataclass
        class SomePerson:
            """Test class."""

            name: str
            age: int
            height: float
            height2: float
            birth: date
            last_login: datetime
            friends: list[SomeFriend] | None
            deleted: datetime | None
            is_deleted: bool
            status: SomeStatus
            file: bytes
            meta: dict[str, str]
            extra_data: SomeExtraData

        raw_data = {
            "name": "Lee Tobi, Sajangnim",
            "age": 38,
            "height": 1.76,
            "height2": 2,
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
            "extra_data": {
                "a_str": "test",
                "a_dict": {
                    "key1": "val1",
                    "key2": "val2",
                },
                "a_list": ["a", "b", "c"],
                "a_typeddict": {"ustr": "hello", "uany": 1},
            },
        }

        data = {
            field.name: dict_value_to_object(
                f"_Person.{__name__}.{field.name}",
                raw_data.get(field.name),
                field.type,
                field.default,
            )
            for field in fields(SomePerson)
        }
        res = SomePerson(**data)

        assert isinstance(res.name, str)
        assert isinstance(res.age, int)
        assert isinstance(res.height, float)
        assert isinstance(res.height2, float)
        assert isinstance(res.birth, date)
        assert isinstance(res.last_login, datetime)
        assert isinstance(res.friends, list)
        assert isinstance(res.friends[0], SomeFriend)
        assert isinstance(res.friends[0].age, int)
        assert isinstance(res.friends[1].age, int)
        assert res.deleted is None
        assert res.is_deleted is False
        assert isinstance(res.status, SomeStatus)
        assert isinstance(res.file, bytes)
        assert isinstance(res.extra_data, dict)
        assert isinstance(res.extra_data["a_typeddict"], dict)

        # back conversion
        back = {field.name: object_to_dict_value(getattr(res, field.name)) for field in fields(res)}

        assert isinstance(back["friends"][0]["age"], int)  # was str in the source dict
        assert isinstance(back["meta"], dict)
        assert isinstance(back["extra_data"], dict)
        assert isinstance(back["extra_data"]["a_list"], list)

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
            _resource = "test"
            # draft_cls - we "forgot" to set a draft class, which will raise
            _resource_cls = TestResource

        helper = TestHelper(api)
        with pytest.raises(DraftNotSupportedError):
            # ... there it is
            helper.draft()
