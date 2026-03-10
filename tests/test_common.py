"""Paperless common tests."""

import re
from datetime import date

import httpx
import pytest
from pydantic import BaseModel
from pytest_httpx import HTTPXMock

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
from pypaperless.models import CustomField, Page
from pypaperless.models.base import PaperlessModel
from pypaperless.models.common import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldDateValue,
    CustomFieldExtraData,
    CustomFieldIntegerValue,
    CustomFieldMonetaryValue,
    CustomFieldSelectValue,
    CustomFieldType,
    MatchingAlgorithmType,
    ShareLinkFileVersionType,
    StatusType,
    TaskStatusType,
    TaskType,
    WorkflowActionType,
    WorkflowTriggerScheduleDateFieldType,
    WorkflowTriggerSourceType,
    WorkflowTriggerType,
)
from pypaperless.models.utils import object_to_dict_value
from pypaperless.services import mixins as service_mixins
from pypaperless.services.base import ServiceBase
from tests.const import (
    PAPERLESS_TEST_PASSWORD,
    PAPERLESS_TEST_TOKEN,
    PAPERLESS_TEST_URL,
    PAPERLESS_TEST_USER,
)

from .data import DATA_CUSTOM_FIELDS, DATA_PATHS, DATA_TOKEN

# mypy: ignore-errors


class TestPaperless:
    """Paperless common test cases."""

    async def test_init(self, httpx_mock: HTTPXMock, api: Paperless) -> None:
        """Test init."""
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=200,
            json=DATA_PATHS,
        )
        await api.initialize()
        assert api.is_initialized
        await api.close()

    async def test_context(self, httpx_mock: HTTPXMock, api: Paperless) -> None:
        """Test context."""
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=200,
            json=DATA_PATHS,
        )
        async with api:
            assert api.is_initialized

    async def test_properties(self, api: Paperless) -> None:
        """Test properties."""
        # version must be None in this case, as we test against
        # an uninitialized Paperless object
        assert api.host_version is None
        assert api.base_url == PAPERLESS_TEST_URL

    async def test_init_error(self, httpx_mock: HTTPXMock, api: Paperless) -> None:
        """Test initialization error."""
        # simulate connection error
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
        with pytest.raises(PaperlessConnectionError):
            await api.initialize()

        # http status error
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=401,
            text="any html",
        )
        with pytest.raises(PaperlessInvalidTokenError):
            await api.initialize()

        # http 401 - inactive or deleted user
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=401,
            json={"detail": "User is inactive"},
        )
        with pytest.raises(PaperlessInactiveOrDeletedError):
            await api.initialize()

        # http status forbidden
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=403,
            text="any html",
        )
        with pytest.raises(PaperlessForbiddenError):
            await api.initialize()

        # http ok, wrong payload
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
            method="GET",
            status_code=200,
            text="any html",
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

    async def test_request(self, httpx_mock: HTTPXMock) -> None:
        """Test generate request."""
        # we need to use an unmocked PaperlessSession.request() method
        # simply don't initialize Paperless and everything will be fine
        api = Paperless(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_TOKEN,
        )

        # test ordinary 200
        httpx_mock.add_response(
            url=PAPERLESS_TEST_URL,
            method="GET",
            status_code=200,
        )
        res = await api.request("get", PAPERLESS_TEST_URL)
        assert res.status_code

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
        httpx_mock.add_response(
            url=PAPERLESS_TEST_URL,
            method="POST",
            status_code=200,
        )
        res = await api.request("post", PAPERLESS_TEST_URL, form=form_data)
        assert res.status_code

        # session is still open
        await api.close()

    async def test_request_json(self, httpx_mock: HTTPXMock, api: Paperless) -> None:
        """Test requests."""
        # test 400 bad request with error payload
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}/400-json-error-payload",
            method="GET",
            status_code=400,
            headers={"Content-Type": "application/json"},
            json={"error": "sample message"},
        )
        with pytest.raises(JsonResponseWithError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/400-json-error-payload")

        # test 200 ok with wrong content type
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}/200-text-error-payload",
            method="GET",
            status_code=200,
            headers={"Content-Type": "text/plain"},
            text='{"error": "sample message"}',
        )
        with pytest.raises(BadJsonResponseError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-text-error-payload")

        # test 200 ok with correct content type, but no json payload
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}/200-json-text-body",
            method="GET",
            status_code=200,
            headers={"Content-Type": "application/json"},
            text="test 5 23 42 1337",
        )
        with pytest.raises(BadJsonResponseError):
            await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-json-text-body")

    async def test_create_url(self) -> None:
        """Test create url util."""
        create_url = Paperless._create_base_url  # pylint: disable=protected-access

        # test default ssl
        url = create_url("hostname")
        assert url == "https://hostname"

        # test enforce http
        url = create_url("http://hostname")
        assert url == "http://hostname"

        # test non-http scheme
        url = create_url("ftp://hostname")
        assert url.startswith("https://")

        # should be https even on just setting a port number
        url = create_url("hostname:80")
        assert url.startswith("https://")

        # test api/api url
        url = create_url("hostname/api/api/")
        assert url == "https://hostname/api/api"

        # test slashes
        url = create_url("hostname/api/endpoint///")
        assert url == "https://hostname/api/endpoint"

    async def test_generate_api_token(self, httpx_mock: HTTPXMock, api: Paperless) -> None:
        """Test generate api token."""
        # test successful token creation
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            method="POST",
            status_code=200,
            json=DATA_TOKEN,
        )
        token = await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
        )
        assert token == PAPERLESS_TEST_TOKEN

        # test token creation with wrong json answer
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            method="POST",
            status_code=200,
            json={"blah": "any string"},
        )
        with pytest.raises(BadJsonResponseError):
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
            )

        # test error 400
        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            method="POST",
            status_code=400,
            json={"non_field_errors": ["Unable to log in."]},
        )
        with pytest.raises(JsonResponseWithError):
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
            )

        # general exception
        httpx_mock.add_exception(
            ValueError(),
            url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            method="POST",
        )
        with pytest.raises(ValueError):  # noqa: PT011
            token = await api.generate_api_token(
                PAPERLESS_TEST_URL,
                PAPERLESS_TEST_USER,
                PAPERLESS_TEST_PASSWORD,
            )

    async def test_generate_api_token_with_client(
        self, httpx_mock: HTTPXMock, api: Paperless
    ) -> None:
        """Test generate api token with custom client."""
        client = httpx.AsyncClient()

        httpx_mock.add_response(
            url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
            method="POST",
            status_code=200,
            json=DATA_TOKEN,
        )
        token = await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
            client=client,
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
        assert TaskType(never_str) == TaskType.UNKNOWN
        assert TaskStatusType(never_str) == TaskStatusType.UNKNOWN
        assert WorkflowActionType(never_int) == WorkflowActionType.UNKNOWN
        assert WorkflowTriggerType(never_int) == WorkflowTriggerType.UNKNOWN
        assert (
            WorkflowTriggerScheduleDateFieldType(never_str)
            == WorkflowTriggerScheduleDateFieldType.UNKNOWN
        )
        assert WorkflowTriggerSourceType(never_int) == WorkflowTriggerSourceType.UNKNOWN

    async def test_custom_field_draft_value_wo_cache(self, paperless: Paperless) -> None:
        """Test draft custom field value without cache."""
        custom_field = CustomField.create_with_data(
            paperless,
            data={"id": 1337, "name": "Test", "data_type": CustomFieldType.INTEGER},
        )
        field_value = custom_field.draft_value(1337)
        for value_type in CUSTOM_FIELD_TYPE_VALUE_MAP.values():
            assert not isinstance(field_value, value_type)

    async def test_custom_field_draft_value_wslash_cache(
        self, httpx_mock: HTTPXMock, paperless: Paperless
    ) -> None:
        """Test draft custom field value with cache."""
        # set custom fields cache
        httpx_mock.add_response(
            url=re.compile(
                r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['custom_fields']}") + r"\?.*$"
            ),
            method="GET",
            status_code=200,
            json=DATA_CUSTOM_FIELDS,
        )
        paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

        custom_field = CustomField.create_with_data(
            client=paperless,
            data=DATA_CUSTOM_FIELDS["results"][5],
        )
        field_value = custom_field.draft_value(1337, expected_type=CustomFieldIntegerValue)
        assert isinstance(field_value, CustomFieldIntegerValue)

    async def test_custom_field_date_value(self) -> None:
        """Test `CustomFieldDateValue`."""
        test = CustomFieldDateValue(value="1900-01-02")
        assert isinstance(test.value, date)
        test = CustomFieldDateValue(value="1900-01-02T03:04:05.133337Z")
        assert isinstance(test.value, date)

    async def test_custom_field_monetary_value(self) -> None:
        """Test `CustomFieldMonetaryValue`."""
        field = CustomFieldMonetaryValue(value="EUR1337.00")
        assert field.currency == "EUR"
        assert field.amount == 1337

        field.amount = 123.45678
        assert field.amount == 123.46  # round

        field.extra_data = CustomFieldExtraData(default_currency="USD")
        assert field.value == "EUR123.46"

        field.value = "123.45"  # no currency
        assert field.currency == "USD"

        field.extra_data = CustomFieldExtraData()
        assert field.currency == ""

        field.currency = "EUR"
        assert field.value == "EUR123.45"

        field.currency = ""
        assert field.value == "123.45"

        field.value = None
        assert field.amount is None

    async def test_custom_field_select_value(self) -> None:
        """Test custom field value types."""
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

    async def test_object_to_dict_value(self) -> None:
        """Test object_to_dict_value utility."""

        class SomeModel(BaseModel):
            """Some model."""

            name: str
            age: int

        # test pydantic model conversion
        model = SomeModel(name="Test", age=42)
        result = object_to_dict_value(model)
        assert isinstance(result, dict)
        assert result["name"] == "Test"
        assert result["age"] == 42

        # test list of models
        models = [SomeModel(name="A", age=1), SomeModel(name="B", age=2)]
        result = object_to_dict_value(models)
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], dict)

        # test primitive values pass through
        assert object_to_dict_value("hello") == "hello"
        assert object_to_dict_value(42) == 42
        assert object_to_dict_value(None) is None

        # test dict values
        d = {"key": "value"}
        result = object_to_dict_value(d)
        assert result == d

    async def test_pages_object(self, api: Paperless) -> None:
        """Test pages."""

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

        page = Page.create_with_data(api, data=data)
        page.set_resource_cls(TestResource)

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

        class TestResource(PaperlessModel):
            """Test Resource."""

        class TestService(ServiceBase, service_mixins.DraftableMixin):
            """Test Service."""

            _api_path = "any.url"
            _resource = "test"
            # draft_cls - we "forgot" to set a draft class, which will raise
            _resource_cls = TestResource

        service = TestService(api)
        with pytest.raises(DraftNotSupportedError):
            # ... there it is
            service.draft()
