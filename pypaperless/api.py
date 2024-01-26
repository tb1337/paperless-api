"""PyPaperless."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
from yarl import URL

from . import helpers
from .const import API_PATH, PaperlessResource
from .exceptions import BadJsonResponse, JsonResponseWithError
from .sessions import PaperlessSession


class Paperless:  # pylint: disable=too-many-instance-attributes
    """Retrieves and manipulates data from and to Paperless via REST."""

    _class_map: set[tuple[str, type]] = {
        (PaperlessResource.CORRESPONDENTS, helpers.CorrespondentHelper),
        (PaperlessResource.CUSTOM_FIELDS, helpers.CustomFieldHelper),
        (PaperlessResource.DOCUMENTS, helpers.DocumentHelper),
        (PaperlessResource.DOCUMENT_TYPES, helpers.DocumentTypeHelper),
        (PaperlessResource.GROUPS, helpers.GroupHelper),
        (PaperlessResource.MAIL_ACCOUNTS, helpers.MailAccountHelper),
        (PaperlessResource.MAIL_RULES, helpers.MailRuleHelper),
        (PaperlessResource.SAVED_VIEWS, helpers.SavedViewHelper),
        (PaperlessResource.SHARE_LINKS, helpers.ShareLinkHelper),
        (PaperlessResource.STORAGE_PATHS, helpers.StoragePathHelper),
        (PaperlessResource.TAGS, helpers.TagHelper),
        (PaperlessResource.USERS, helpers.UserHelper),
        (PaperlessResource.WORKFLOWS, helpers.WorkflowHelper),
    }

    correspondents: helpers.CorrespondentHelper
    custom_fields: helpers.CustomFieldHelper
    documents: helpers.DocumentHelper
    document_types: helpers.DocumentTypeHelper
    groups: helpers.GroupHelper
    mail_accounts: helpers.MailAccountHelper
    mail_rules: helpers.MailRuleHelper
    saved_views: helpers.SavedViewHelper
    share_links: helpers.ShareLinkHelper
    storage_paths: helpers.StoragePathHelper
    tags: helpers.TagHelper
    users: helpers.UserHelper
    workflows: helpers.WorkflowHelper

    async def __aenter__(self) -> "Paperless":
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, *_: object) -> None:
        """Exit context manager."""
        await self.close()

    def __init__(
        self,
        url: str | URL,
        token: str,
        session: PaperlessSession | None = None,
    ):
        """Initialize a `Paperless` instance.

        `url`: A hostname or IP-address as string, or yarl.URL object.
        `token`: An api token created in Paperless Django settings, or via the helper function.
        `request_opts`: Optional request options for the `aiohttp.ClientSession.request` method.
        `session`: An existing `aiohttp.ClientSession` if existing.
        """
        self._paths: set[PaperlessResource] = set()
        self._initialized = False
        self._session = session or PaperlessSession(url, token)
        self._version: str | None = None

        self.logger = logging.getLogger(f"{__package__}[{self._session}]")

    @property
    def is_initialized(self) -> bool:
        """Return `True` if connection is initialized."""
        return self._initialized

    @property
    def host_version(self) -> str | None:
        """Return the version object of the Paperless host."""
        return self._version

    async def close(self) -> None:
        """Clean up connection."""
        if self._session:
            await self._session.close()
        self.logger.info("Closed.")

    async def initialize(self) -> None:
        """Initialize the connection to DRF and fetch the endpoints."""
        async with self.request("get", API_PATH["index"]) as res:
            self._version = res.headers.get("x-version", None)
            paths = set(map(PaperlessResource, await res.json()))

        for endpoint, cls in self._class_map:
            setattr(self, f"{endpoint}", cls(self))

        unused = paths.difference(self._paths)
        missing = self._paths.difference(paths)

        if len(unused) > 0:
            self.logger.debug("Unused features: %s", ", ".join(unused))

        if len(missing) > 0:
            self.logger.warning("Outdated version detected: v%s", self._version)
            self.logger.warning("Missing features: %s", ", ".join(missing))
            self.logger.warning("Consider pulling the latest version of Paperless-ngx.")

        self.logger.info("Initialized.")

        self._initialized = True

    @asynccontextmanager
    async def request(  ## pylint: disable=too-many-arguments
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | aiohttp.FormData | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse, None]:
        """Perform a request."""
        res = await self._session.request(
            method,
            path,
            json=json,
            data=data,
            form=form,
            params=params,
            **kwargs,
        )
        self.logger.debug("%s (%d): %s", method.upper(), res.status, res.url)
        yield res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        async with self.request(method, endpoint, **kwargs) as res:
            try:
                payload = await res.json()
            except ValueError as exc:
                raise BadJsonResponse(res) from exc

        if res.status == 400:
            raise JsonResponseWithError(payload)
        res.raise_for_status()

        return payload

    async def request_file(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> bytes:
        """Make a request to the api and return response as bytes."""
        async with self.request(method, endpoint, **kwargs) as res:
            return await res.read()