"""Paperless class."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
from awesomeversion import AwesomeVersion
from yarl import URL

from .const import (
    API_PATH,
    PAPERLESS_V1_8_0,
    PAPERLESS_V1_17_0,
    PAPERLESS_V2_0_0,
    PAPERLESS_V2_3_0,
    PaperlessFeature,
)
from .errors import BadRequestException, DataNotExpectedException
from .models import helpers


class Paperless:  # pylint: disable=too-many-instance-attributes
    """Retrieves and manipulates data from and to Paperless via REST."""

    async def __aenter__(self) -> "Paperless":
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, exc_tb: Any) -> Any | None:
        """Exit context manager."""
        await self.close()
        if exc:
            raise exc
        return exc_type

    def __init__(
        self,
        url: str | URL,
        token: str,
        request_opts: dict[str, Any] | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        """Initialize a `Paperless` instance.

        `url`: A hostname or IP-address as string, or yarl.URL object.
        `token`: An api token created in Paperless Django settings, or via the helper function.
        `request_opts`: Optional request options for the `aiohttp.ClientSession.request` method.
        `session`: An existing `aiohttp.ClientSession` if existing.
        """
        self._base_url = self.create_url_from_input(url)
        self._token = token
        self._request_opts = request_opts
        self._session = session
        self._initialized = False
        self.logger = logging.getLogger(f"{__package__}[{self.base_url.host}]")

        self.features: PaperlessFeature = PaperlessFeature(0)

        # apis
        self.documents = helpers.DocumentHelper(self)

    @property
    def base_url(self) -> URL:
        """Return the base url of Paperless."""
        return self._base_url

    @property
    def is_initialized(self) -> bool:
        """Return `True` if connection is initialized."""
        return self._initialized

    @staticmethod
    def create_url_from_input(url: str | URL) -> URL:
        """Create URL from string or URL and prepare for further use."""
        # reverse compatibility, fall back to https
        if isinstance(url, str) and "://" not in url:
            url = f"https://{url}".rstrip("/")
        url = URL(url)

        # scheme check. fall back to https
        if url.scheme not in ("https", "http"):
            url = URL(url).with_scheme("https")

        return url

    async def close(self) -> None:
        """Clean up connection."""
        if self._session:
            await self._session.close()
        self.logger.info("Closed.")

    async def initialize(self) -> None:
        """Initialize the connection to DRF and fetch the endpoints."""
        self.logger.info("Fetching api endpoints.")

        async with self.generate_request("get", API_PATH["index"]) as res:
            version = AwesomeVersion(
                res.headers.get("x-version") if "x-version" in res.headers else "0.0.0"
            )

            if version >= PAPERLESS_V1_8_0:
                self.features |= PaperlessFeature.CONTROLLER_STORAGE_PATHS
            if version >= PAPERLESS_V1_17_0:
                self.features |= PaperlessFeature.FEATURE_DOCUMENT_NOTES
            if version >= PAPERLESS_V2_0_0:
                self.features |= (
                    PaperlessFeature.CONTROLLER_SHARE_LINKS
                    | PaperlessFeature.CONTROLLER_CONSUMPTION_TEMPLATES
                    | PaperlessFeature.CONTROLLER_CUSTOM_FIELDS
                )
            if version >= PAPERLESS_V2_3_0:
                self.features |= (
                    PaperlessFeature.CONTROLLER_CONFIGS | PaperlessFeature.CONTROLLER_WORKFLOWS
                )
                self.features ^= PaperlessFeature.CONTROLLER_CONSUMPTION_TEMPLATES

            paths = await res.json()

        self._initialized = True

        if len(paths) > 0:
            self.logger.debug("Unused paths: %s", ", ".join(paths))
        self.logger.info("Initialized.")

    @asynccontextmanager
    async def generate_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse, None]:
        """Create a client response object for further use."""
        if not isinstance(self._session, aiohttp.ClientSession):
            self._session = aiohttp.ClientSession()

        if isinstance(self._request_opts, dict):
            kwargs.update(self._request_opts)

        kwargs.setdefault("headers", {})
        kwargs["headers"].update(
            {
                "accept": "application/json; version=2",
                "authorization": f"Token {self._token}",
            }
        )

        # convert form to FormData, if dict
        if "form" in kwargs:
            payload = kwargs.pop("form")
            if not isinstance(payload, dict):
                raise TypeError()
            form = aiohttp.FormData()

            # we just convert data, no nesting dicts
            for key, value in payload.items():
                if value is None:
                    continue
                if isinstance(value, str | bytes):
                    form.add_field(key, value)
                elif isinstance(value, list):
                    for list_value in value:
                        form.add_field(key, f"{list_value}")
                else:
                    form.add_field(key, f"{value}")

            kwargs["data"] = form

        # check for trailing slash if needed
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        if URL(url).query_string == "":
            url = url.rstrip("/") + "/"

        # request data
        async with self._session.request(method, url, **kwargs) as res:
            yield res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        async with self.generate_request(method, endpoint, **kwargs) as res:
            self.logger.debug("Json-Request %s (%d): %s", method.upper(), res.status, res.url)

            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            # no content, in most cases on DELETE method
            if res.status == 204:
                return {}
            res.raise_for_status()

            if res.content_type != "application/json":
                raise DataNotExpectedException(f"Content-type is not json! {res.content_type}")

            return await res.json()

    async def request_file(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> bytes:
        """Make a request to the api and return response as bytes."""
        async with self.generate_request(method, endpoint, **kwargs) as res:
            self.logger.debug("File-Request %s (%d): %s", method.upper(), res.status, res.url)

            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            res.raise_for_status()

            return await res.read()
