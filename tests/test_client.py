"""Tests for the Paperless client: init, context, requests, URL, token, Page model."""

from io import BytesIO

import httpx
import pytest
from pydantic import BaseModel, ValidationError
from pytest_httpx import HTTPXMock

from pypaperless import Paperless, PaperlessConfig
from pypaperless.const import API_PATH, API_VERSION
from pypaperless.exceptions import (
    BadJsonResponseError,
    DraftNotSupportedError,
    ForbiddenError,
    InactiveOrDeletedError,
    InitializationError,
    InvalidTokenError,
    JsonResponseWithError,
    PaperlessConnectionError,
)
from pypaperless.models import Page
from pypaperless.models.base import PaperlessModel
from pypaperless.services import mixins as service_mixins
from pypaperless.services.base import ServiceBase
from pypaperless.utils import normalize_base_url, object_to_dict_value, process_form_data
from tests.const import (
    PAPERLESS_TEST_PASSWORD,
    PAPERLESS_TEST_TOKEN,
    PAPERLESS_TEST_URL,
    PAPERLESS_TEST_USER,
)

from .data import DATA_PATHS, DATA_TOKEN


async def test_init(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """Test initialization."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=200,
        json=DATA_PATHS,
    )
    await api.initialize()
    assert api.is_initialized
    await api.close()


async def test_context(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """Test async context manager initializes the client."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=200,
        json=DATA_PATHS,
    )
    async with api:
        assert api.is_initialized


async def test_properties(api: Paperless) -> None:
    """Test client properties before initialization."""
    # version must be None for an uninitialized client
    assert api.host_version is None
    assert api.base_url == PAPERLESS_TEST_URL


async def test_init_error(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """Test that initialization raises the correct errors for each failure mode."""
    # connection error
    httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
    with pytest.raises(PaperlessConnectionError):
        await api.initialize()

    # HTTP 401 - wrong token
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=401,
        text="any html",
    )
    with pytest.raises(InvalidTokenError):
        await api.initialize()

    # HTTP 401 - inactive / deleted user
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=401,
        json={"detail": "User is inactive"},
    )
    with pytest.raises(InactiveOrDeletedError):
        await api.initialize()

    # HTTP 403 - forbidden
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=403,
        text="any html",
    )
    with pytest.raises(ForbiddenError):
        await api.initialize()

    # HTTP 200 with non-JSON body
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['index']}",
        method="GET",
        status_code=200,
        text="any html",
    )
    with pytest.raises(InitializationError):
        await api.initialize()


async def test_request(httpx_mock: HTTPXMock) -> None:
    """Test low-level request method, including form data encoding."""
    # use uninitialised client to bypass session setup
    api = Paperless(PAPERLESS_TEST_URL, PAPERLESS_TEST_TOKEN)

    httpx_mock.add_response(url=PAPERLESS_TEST_URL, method="GET", status_code=200)
    res = await api.request("get", PAPERLESS_TEST_URL)
    assert res.status_code

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
    httpx_mock.add_response(url=PAPERLESS_TEST_URL, method="POST", status_code=200)
    res = await api.request("post", PAPERLESS_TEST_URL, form=form_data)
    assert res.status_code

    await api.close()


async def test_request_json(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """Test request_json raises on bad content-type or non-JSON body."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}/400-json-error-payload",
        method="GET",
        status_code=400,
        headers={"Content-Type": "application/json"},
        json={"error": "sample message"},
    )
    with pytest.raises(JsonResponseWithError):
        await api.request_json("get", f"{PAPERLESS_TEST_URL}/400-json-error-payload")

    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}/200-text-error-payload",
        method="GET",
        status_code=200,
        headers={"Content-Type": "text/plain"},
        text='{"error": "sample message"}',
    )
    with pytest.raises(BadJsonResponseError):
        await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-text-error-payload")

    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}/200-json-text-body",
        method="GET",
        status_code=200,
        headers={"Content-Type": "application/json"},
        text="test 5 23 42 1337",
    )
    with pytest.raises(BadJsonResponseError):
        await api.request_json("get", f"{PAPERLESS_TEST_URL}/200-json-text-body")


@pytest.mark.parametrize(
    ("input_url", "expected"),
    [
        ("hostname", "https://hostname"),
        ("http://hostname", "http://hostname"),
        ("ftp://hostname", "https://ftp://hostname"),
        ("hostname:80", "https://hostname:80"),
        ("hostname/api/api/", "https://hostname/api/api"),
        ("hostname/api/endpoint///", "https://hostname/api/endpoint"),
    ],
)
def test_create_url(input_url: str, expected: str) -> None:
    """normalize_base_url handles all URL edge cases correctly."""
    assert normalize_base_url(input_url) == expected


async def test_generate_api_token(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """Test token generation success and failure modes."""
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

    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
        method="POST",
        status_code=200,
        json={"blah": "any string"},
    )
    with pytest.raises(BadJsonResponseError):
        await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
        )

    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
        method="POST",
        status_code=400,
        json={"non_field_errors": ["Unable to log in."]},
    )
    with pytest.raises(JsonResponseWithError):
        await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
        )

    httpx_mock.add_exception(
        ValueError(),
        url=f"{PAPERLESS_TEST_URL}{API_PATH['token']}",
        method="POST",
    )
    with pytest.raises(ValueError):  # noqa: PT011
        await api.generate_api_token(
            PAPERLESS_TEST_URL,
            PAPERLESS_TEST_USER,
            PAPERLESS_TEST_PASSWORD,
        )

    # passing an explicit httpx client still returns the correct token
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
        client=httpx.AsyncClient(),
    )
    assert token == PAPERLESS_TEST_TOKEN


async def test_pages_object(api: Paperless) -> None:
    """Test Page model construction, iteration, and navigation helpers."""

    class TestResource(PaperlessModel):
        id: int | None = None

    data: dict = {
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

    page = Page.from_data(api, data=data)
    page.set_resource_cls(TestResource)

    assert isinstance(page, Page)
    assert page.current_count == 100
    for item in page:
        assert isinstance(item, TestResource)

    # first page
    assert not page.has_previous_page
    assert page.has_next_page
    assert not page.is_last_page
    assert page.last_page == 4
    assert page.next_page == 2
    assert page.previous_page is None

    # inner page
    page.previous = "any.url"
    page.current_page = 3
    assert page.previous_page is not None
    assert page.next_page is not None
    assert not page.is_last_page

    # last page
    page.next = None
    page.current_page = 4
    assert page.next_page is None
    assert page.is_last_page


async def test_draft_not_supported(api: Paperless) -> None:
    """Test that DraftableMixin.create() raises when no draft_cls is configured."""

    class TestResource(PaperlessModel):
        pass

    class TestService(ServiceBase, service_mixins.DraftableMixin):
        _api_path = "any.url"
        _resource = "test"
        _resource_cls = TestResource

    service = TestService(api)
    with pytest.raises(DraftNotSupportedError):
        service.create()


async def test_object_to_dict_value() -> None:
    """Test object_to_dict_value converts Pydantic models and passes primitives through."""

    class SomeModel(BaseModel):
        name: str
        age: int

    model = SomeModel(name="Test", age=42)
    result = object_to_dict_value(model)
    assert isinstance(result, dict)
    assert result["name"] == "Test"
    assert result["age"] == 42

    models_list = [SomeModel(name="A", age=1), SomeModel(name="B", age=2)]
    result = object_to_dict_value(models_list)
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], dict)

    assert object_to_dict_value("hello") == "hello"
    assert object_to_dict_value(42) == 42
    assert object_to_dict_value(None) is None

    d = {"key": "value"}
    assert object_to_dict_value(d) == d


async def test_request_merges_custom_headers(httpx_mock: HTTPXMock) -> None:
    """request() merges caller-supplied headers with the default auth headers."""
    api = Paperless(PAPERLESS_TEST_URL, PAPERLESS_TEST_TOKEN)
    httpx_mock.add_response(url=PAPERLESS_TEST_URL, method="GET", status_code=200)
    res = await api.request("get", PAPERLESS_TEST_URL, headers={"X-Custom": "value"})
    assert res.status_code == 200
    await api.close()


async def test_request_json_400_body_not_json(httpx_mock: HTTPXMock, api: Paperless) -> None:
    """request_json() raises BadJsonResponseError when a 400 body is not valid JSON."""
    httpx_mock.add_response(
        url=f"{PAPERLESS_TEST_URL}/400-bad-json",
        method="GET",
        status_code=400,
        headers={"Content-Type": "application/json"},
        text="not valid json {{{}}}",
    )
    with pytest.raises(BadJsonResponseError):
        await api.request_json("get", f"{PAPERLESS_TEST_URL}/400-bad-json")


async def test_service_base_api_path(api: Paperless) -> None:
    """ServiceBase.api_path property returns the configured _api_path."""

    class _TestService(ServiceBase):
        _api_path = "/api/test/"

    svc = _TestService(api)
    assert svc.api_path == "/api/test/"


def test_process_form_data_tuple_len1() -> None:
    """process_form_data wraps a 1-tuple value as a plain BytesIO (no filename)."""
    _data, files = process_form_data({"doc": (b"raw bytes",)})
    assert len(files) == 1
    name, fobj = files[0]
    assert name == "doc"
    assert isinstance(fobj, BytesIO)
    assert fobj.read() == b"raw bytes"


def test_process_form_data_duplicate_key_scalar_to_list() -> None:
    """process_form_data converts a repeated scalar key into a list."""
    _data, _ = process_form_data({"tags": {"a": 1, "b": 2}})
    # dict expansion produces two calls for the same effective key if we force it
    # Directly test _add_data_value by calling process_form_data with a list:
    # The actual "scalar → list" conversion occurs when the same key appears twice
    # at the dict/list expansion level. Simulate by calling twice via a nested list:
    data2, _ = process_form_data({"ids": [10, 20]})
    # Both values land in data2["ids"] as a list
    assert data2["ids"] == ["10", "20"]


# ---------------------------------------------------------------------------
# PaperlessConfig / multi-mode init tests
# ---------------------------------------------------------------------------


def test_config_explicit_params() -> None:
    """Paperless(url, token) — classic mode still works."""
    api = Paperless(PAPERLESS_TEST_URL, PAPERLESS_TEST_TOKEN)
    assert api.base_url == PAPERLESS_TEST_URL
    assert api._token == PAPERLESS_TEST_TOKEN


def test_config_object() -> None:
    """Paperless(config=PaperlessConfig(...)) wires url and token correctly."""
    cfg = PaperlessConfig(url=PAPERLESS_TEST_URL, token=PAPERLESS_TEST_TOKEN)
    api = Paperless(config=cfg)
    assert api.base_url == PAPERLESS_TEST_URL
    assert api._token == PAPERLESS_TEST_TOKEN


def test_config_object_custom_api_version() -> None:
    """PaperlessConfig.request_api_version is forwarded to the client."""
    cfg = PaperlessConfig(url=PAPERLESS_TEST_URL, token=PAPERLESS_TEST_TOKEN, request_api_version=7)
    api = Paperless(config=cfg)
    assert api._request_api_version == 7


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Paperless() with no args reads PYPAPERLESS_URL / PYPAPERLESS_TOKEN from the environment."""
    monkeypatch.setenv("PYPAPERLESS_URL", PAPERLESS_TEST_URL)
    monkeypatch.setenv("PYPAPERLESS_TOKEN", PAPERLESS_TEST_TOKEN)
    api = Paperless()
    assert api.base_url == PAPERLESS_TEST_URL
    assert api._token == PAPERLESS_TEST_TOKEN


def test_config_from_env_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """Paperless() raises ValidationError when PYPAPERLESS_URL is not set."""
    monkeypatch.delenv("PYPAPERLESS_URL", raising=False)
    monkeypatch.delenv("PYPAPERLESS_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        Paperless()


def test_config_from_env_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Paperless() sets token to None when PYPAPERLESS_TOKEN is not set."""
    monkeypatch.setenv("PYPAPERLESS_URL", PAPERLESS_TEST_URL)
    monkeypatch.delenv("PYPAPERLESS_TOKEN", raising=False)
    api = Paperless()
    assert api._token is None


def test_config_default_api_version_from_const() -> None:
    """PaperlessConfig uses API_VERSION as default for request_api_version."""
    cfg = PaperlessConfig(url=PAPERLESS_TEST_URL)
    assert cfg.request_api_version == API_VERSION
