"""PyPaperless."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from io import BytesIO
from json.decoder import JSONDecodeError
from typing import Any, cast

import aiohttp
import aiohttp.web_exceptions
from yarl import URL

from . import helpers
from .const import API_PATH, API_VERSION, PaperlessResource
from .exceptions import (
    BadJsonResponseError,
    InitializationError,
    JsonResponseWithError,
    PaperlessConnectionError,
    PaperlessForbiddenError,
    PaperlessInactiveOrDeletedError,
    PaperlessInvalidTokenError,
)
from .models.base import HelperBase
from .models.common import PaperlessCache


class Paperless:
    """Retrieves and manipulates data from and to Paperless via REST."""

    _helpers_map: set[tuple[str, type[HelperBase]]] = {
        (PaperlessResource.CONFIG, helpers.ConfigHelper),
        (PaperlessResource.CORRESPONDENTS, helpers.CorrespondentHelper),
        (PaperlessResource.CUSTOM_FIELDS, helpers.CustomFieldHelper),
        (PaperlessResource.DOCUMENTS, helpers.DocumentHelper),
        (PaperlessResource.DOCUMENT_TYPES, helpers.DocumentTypeHelper),
        (PaperlessResource.GROUPS, helpers.GroupHelper),
        (PaperlessResource.MAIL_ACCOUNTS, helpers.MailAccountHelper),
        (PaperlessResource.MAIL_RULES, helpers.MailRuleHelper),
        (PaperlessResource.SAVED_VIEWS, helpers.SavedViewHelper),
        (PaperlessResource.SHARE_LINKS, helpers.ShareLinkHelper),
        (PaperlessResource.STATISTICS, helpers.StatisticHelper),
        (PaperlessResource.REMOTE_VERSION, helpers.RemoteVersionHelper),
        (PaperlessResource.STATUS, helpers.StatusHelper),
        (PaperlessResource.STORAGE_PATHS, helpers.StoragePathHelper),
        (PaperlessResource.TAGS, helpers.TagHelper),
        (PaperlessResource.TASKS, helpers.TaskHelper),
        (PaperlessResource.USERS, helpers.UserHelper),
        (PaperlessResource.WORKFLOWS, helpers.WorkflowHelper),
    }

    config: helpers.ConfigHelper
    correspondents: helpers.CorrespondentHelper
    custom_fields: helpers.CustomFieldHelper
    documents: helpers.DocumentHelper
    document_types: helpers.DocumentTypeHelper
    groups: helpers.GroupHelper
    mail_accounts: helpers.MailAccountHelper
    mail_rules: helpers.MailRuleHelper
    saved_views: helpers.SavedViewHelper
    share_links: helpers.ShareLinkHelper
    statistics: helpers.StatisticHelper
    remote_version: helpers.RemoteVersionHelper
    status: helpers.StatusHelper
    storage_paths: helpers.StoragePathHelper
    tags: helpers.TagHelper
    tasks: helpers.TaskHelper
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
        *,
        session: aiohttp.ClientSession | None = None,
        request_args: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a `Paperless` instance.

        You have to permit either a session, or an url / token pair.

        `url`: A hostname or IP-address as string, or yarl.URL object.
        `token`: An api token created in Paperless Django settings, or via the helper function.
        `session`: A custom `PaperlessSession` object, if existing.
        `request_args` are passed to each request method call as additional kwargs,
        ssl stuff for example. You should read the aiohttp docs to learn more about it.
        """
        self._base_url = self._create_base_url(url)
        self._cache = PaperlessCache()
        self._initialized = False
        self._local_resources: set[PaperlessResource] = set()
        self._remote_resources: set[PaperlessResource] = set()
        self._request_args = request_args or {}
        self._session = session
        self._token = token
        self._version: str | None = None

        self.logger = logging.getLogger(f"{__package__}")

    @property
    def base_url(self) -> str:
        """Return the base url of the Paperless api endpoint."""
        return str(self._base_url)

    @property
    def cache(self) -> PaperlessCache:
        """Return the cache object."""
        return self._cache

    @property
    def is_initialized(self) -> bool:
        """Return `True` if connection is initialized."""
        return self._initialized

    @property
    def host_version(self) -> str | None:
        """Return the version of the Paperless host."""
        return self._version

    @property
    def local_resources(self) -> set[PaperlessResource]:
        """Return a set of locally available resources."""
        return self._local_resources

    @property
    def remote_resources(self) -> set[PaperlessResource]:
        """Return a set of available resources of the Paperless host."""
        return self._remote_resources

    @staticmethod
    def _create_base_url(url: str | URL) -> URL:
        """Create URL from string or URL and prepare for further use."""
        # reverse compatibility, fall back to https
        if isinstance(url, str):
            if "://" not in url:
                url = f"https://{url}"
            url = url.rstrip("/")
        url = URL(url)

        # scheme check. fall back to https
        if url.scheme not in ("https", "http"):
            url = URL(url).with_scheme("https")

        return url

    @staticmethod
    def _process_form(data: dict[str, Any]) -> aiohttp.FormData:
        """Process form data and create a `aiohttp.FormData` object.

        Every field item gets converted to a string-like object.
        """
        form = aiohttp.FormData(quote_fields=False)

        def _add_form_value(name: str | None, value: Any) -> Any:
            if value is None:
                return
            params = {}
            if isinstance(value, dict):
                for dict_key, dict_value in value.items():
                    _add_form_value(dict_key, dict_value)
                return
            if isinstance(value, list | set):
                for list_value in value:
                    _add_form_value(name, list_value)
                return
            if isinstance(value, tuple):
                if len(value) == 2:
                    params["filename"] = f"{value[1]}"
                value = value[0]
            if name is not None:
                form.add_field(
                    name, BytesIO(value) if isinstance(value, bytes) else f"{value}", **params
                )

        _add_form_value(None, data)
        return form

    @staticmethod
    async def generate_api_token(
        url: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ) -> str:
        """Request Paperless to generate an api token for the given credentials.

        Warning: the request is plain and insecure. Don't use this in production
        environments or businesses.

        Warning: error handling is low for this method, as it is just a helper.

        Example:
        -------
        ```python
        token = Paperless.generate_api_token("example.com:8000", "api_user", "secret_password")

        paperless = Paperless("example.com:8000", token)
        # do something
        ```

        """
        external_session = session is not None
        session = session or aiohttp.ClientSession()
        try:
            url = url.rstrip("/")
            json = {
                "username": username,
                "password": password,
            }
            res = await session.request("post", f"{url}{API_PATH['token']}", json=json)
            data = await res.json()
            res.raise_for_status()
            return str(data["token"])
        except (JSONDecodeError, KeyError) as exc:
            message = "Token is missing in response."
            raise BadJsonResponseError(message) from exc
        except aiohttp.ClientResponseError as exc:
            raise JsonResponseWithError(payload={"error": data}) from exc
        finally:
            if not external_session:
                await session.close()

    async def close(self) -> None:
        """Clean up connection."""
        if self._session:
            await self._session.close()
        self.logger.info("Closed.")

    async def initialize(self) -> None:
        """Initialize the connection to DRF and fetch the endpoints."""

        async def _init_with_openapi_response() -> bool:
            """Connect to paperless and request the openapi schema."""
            try:
                async with self.request("get", API_PATH["api_schema"]) as res:
                    res.raise_for_status()
                    self._version = res.headers.get("x-version", None)
                    await res.read()
            except aiohttp.ClientError:
                return False

            return True

        async def _init_with_legacy_response() -> dict[str, str]:
            """Connect to paperless and request the entity dictionary (DRF)."""
            async with self.request("get", API_PATH["index"]) as res:
                try:
                    res.raise_for_status()
                    payload = await res.json()
                except (aiohttp.ClientResponseError, ValueError) as exc:
                    raise InitializationError from exc

                self._version = res.headers.get("x-version", None)
                return cast("dict[str, str]", payload)

        if await _init_with_openapi_response():
            self.logger.debug("OpenAPI spec detected.")
            self._remote_resources = {
                res
                for res in PaperlessResource
                if res
                not in {
                    PaperlessResource.UNKNOWN,
                    PaperlessResource.CONSUMPTION_TEMPLATES,
                }
            }
        else:
            payload = await _init_with_legacy_response()
            self._remote_resources = set(map(PaperlessResource, payload))

        # initialize helpers
        for attribute, helper in self._helpers_map:
            setattr(self, f"{attribute}", helper(self))

        unused = self._remote_resources.difference(self._local_resources)
        missing = self._local_resources.difference(self._remote_resources)

        if len(unused) > 0:
            self.logger.debug("Unused features: %s", ", ".join(unused))

        if len(missing) > 0:
            self.logger.warning(
                "Outdated version detected. Consider pulling the latest version of Paperless-ngx."
            )
            self.logger.warning("Support for Paperless-ngx <v2.15.0 will expire 07/01/2025.")

        self._initialized = True
        self.logger.info("Initialized.")

    @asynccontextmanager
    async def request(  # noqa: PLR0913 # pylint: disable=too-many-positional-arguments
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | aiohttp.FormData | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse]:
        """Send a request to the Paperless api and return the `aiohttp.ClientResponse`.

        This method provides a little interface for utilizing `aiohttp.FormData`.

        `method`: A http method: get, post, patch, put, delete, head, options
        `path`: A path to the endpoint or a string url.
        `json`: A dict containing the json data.
        `data`: A dict containing the data to send in the request body.
        `form`: A dict with form data, which gets converted to `aiohttp.FormData`
        and replaces `data`.
        `params`: A dict with query parameters.
        `kwargs`: Optional attributes for the `aiohttp.ClientSession.request` method.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()

        # add headers
        headers = {
            "Accept": f"application/json; version={API_VERSION}",
            "Authorization": f"Token {self._token}",
        }

        # Merge with any user-defined headers (optional)
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        # add request args
        kwargs.update(self._request_args)

        # overwrite data with a form, when there is a form payload
        if isinstance(form, dict):
            data = self._process_form(form)

        # add base path
        url = f"{self._base_url}{path}" if not path.startswith("http") else path

        try:
            res = await self._session.request(
                method=method,
                url=url,
                json=json,
                data=data,
                params=params,
                **kwargs,
            )
            self.logger.debug("%s (%d): %s", method.upper(), res.status, res.url)
        except aiohttp.ClientConnectionError as err:
            raise PaperlessConnectionError from err

        # error handling for 401 and 403 codes
        if res.status == 401:
            try:
                error_data = await res.json()
                detail = error_data.get("detail", "")
            except JSONDecodeError:
                detail = ""

            if "inactive" in detail.lower() or "deleted" in detail.lower():
                raise PaperlessInactiveOrDeletedError(res)

            raise PaperlessInvalidTokenError(res)

        if res.status == 403:
            raise PaperlessForbiddenError(res)

        yield res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        async with self.request(method, endpoint, **kwargs) as res:
            if res.content_type != "application/json":
                raise BadJsonResponseError(res)

            try:
                payload = await res.json()
            except ValueError:
                raise BadJsonResponseError(res) from None

            if res.status == 400:
                raise JsonResponseWithError(payload)

            res.raise_for_status()

        return payload
