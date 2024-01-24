"""Paperless class."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
from yarl import URL

from . import helpers
from .const import API_PATH, PaperlessEndpoints
from .errors import BadRequestException, DataNotExpectedException


class Paperless:  # pylint: disable=too-many-instance-attributes
    """Retrieves and manipulates data from and to Paperless via REST."""

    _class_map: set[tuple[str, type]] = {
        (PaperlessEndpoints.CUSTOM_FIELDS, helpers.CustomFieldHelper),
        (PaperlessEndpoints.DOCUMENTS, helpers.DocumentHelper),
        (PaperlessEndpoints.GROUPS, helpers.GroupHelper),
        (PaperlessEndpoints.MAIL_ACCOUNTS, helpers.MailAccountHelper),
        (PaperlessEndpoints.MAIL_RULES, helpers.MailRuleHelper),
        (PaperlessEndpoints.SAVED_VIEWS, helpers.SavedViewHelper),
        (PaperlessEndpoints.SHARE_LINKS, helpers.ShareLinkHelper),
        (PaperlessEndpoints.USERS, helpers.UserHelper),
    }

    custom_fields: helpers.CustomFieldHelper
    documents: helpers.DocumentHelper
    groups: helpers.GroupHelper
    mail_accounts: helpers.MailAccountHelper
    mail_rules: helpers.MailRuleHelper
    saved_views: helpers.SavedViewHelper
    share_links: helpers.ShareLinkHelper
    users: helpers.UserHelper

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
        self._initialized = False
        self._request_opts = request_opts
        self._session = session
        self._token = token
        self._version: str | None = None

        self.logger = logging.getLogger(f"{__package__}[{self.base_url.host}]")

    @property
    def base_url(self) -> URL:
        """Return the base url of Paperless."""
        return self._base_url

    @property
    def is_initialized(self) -> bool:
        """Return `True` if connection is initialized."""
        return self._initialized

    @property
    def host_version(self) -> str | None:
        """Return the version object of the Paperless host."""
        return self._version

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
        self.logger.debug("Fetching features...")

        async with self.generate_request("get", API_PATH["index"]) as res:
            self._version = res.headers.get("x-version", None)
            paths = await res.json()

        missing = []
        for endpoint, cls in self._class_map:
            try:
                paths.pop(endpoint)  # check if endpoint exists
            except KeyError:
                missing.append(endpoint)
            finally:
                setattr(self, f"{endpoint}", cls(self))

        if len(paths) > 0:
            self.logger.debug("Unused: %s", ", ".join(paths))

        if len(missing) > 0:
            self.logger.warning("Outdated version detected: v%s", self._version)
            self.logger.warning("Missing features: %s", ", ".join(missing))
            self.logger.warning("Consider pulling the latest version of Paperless-ngx.")

        self.logger.info("Initialized.")
        self._initialized = True

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
            self.logger.debug("HTTP %s -> %d: %s", method.upper(), res.status, res.url)
            yield res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        async with self.generate_request(method, endpoint, **kwargs) as res:
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
            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            res.raise_for_status()

            return await res.read()
