"""PyPaperless."""

import json
import logging
from io import BytesIO
from typing import Any, Protocol

import httpx

from . import services
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
from .models.base import ServiceBase
from .models.common import PaperlessCache


class PaperlessProtocol(Protocol):
    """Protocol for `Paperless` instances."""

    config: services.ConfigService
    correspondents: services.CorrespondentService
    custom_fields: services.CustomFieldService
    documents: services.DocumentService
    document_types: services.DocumentTypeService
    groups: services.GroupService
    mail_accounts: services.MailAccountService
    mail_rules: services.MailRuleService
    processed_mail: services.ProcessedMailService
    saved_views: services.SavedViewService
    share_links: services.ShareLinkService
    statistics: services.StatisticService
    remote_version: services.RemoteVersionService
    status: services.StatusService
    storage_paths: services.StoragePathService
    tags: services.TagService
    tasks: services.TaskService
    users: services.UserService
    workflows: services.WorkflowService


class Paperless(PaperlessProtocol):
    """Retrieves and manipulates data from and to Paperless via REST."""

    _service_map: dict[str, type[ServiceBase]] = {
        PaperlessResource.CONFIG: services.ConfigService,
        PaperlessResource.CORRESPONDENTS: services.CorrespondentService,
        PaperlessResource.CUSTOM_FIELDS: services.CustomFieldService,
        PaperlessResource.DOCUMENTS: services.DocumentService,
        PaperlessResource.DOCUMENT_TYPES: services.DocumentTypeService,
        PaperlessResource.GROUPS: services.GroupService,
        PaperlessResource.MAIL_ACCOUNTS: services.MailAccountService,
        PaperlessResource.MAIL_RULES: services.MailRuleService,
        PaperlessResource.PROCESSED_MAIL: services.ProcessedMailService,
        PaperlessResource.SAVED_VIEWS: services.SavedViewService,
        PaperlessResource.SHARE_LINKS: services.ShareLinkService,
        PaperlessResource.STATISTICS: services.StatisticService,
        PaperlessResource.REMOTE_VERSION: services.RemoteVersionService,
        PaperlessResource.STATUS: services.StatusService,
        PaperlessResource.STORAGE_PATHS: services.StoragePathService,
        PaperlessResource.TAGS: services.TagService,
        PaperlessResource.TASKS: services.TaskService,
        PaperlessResource.USERS: services.UserService,
        PaperlessResource.WORKFLOWS: services.WorkflowService,
    }

    async def __aenter__(self) -> "Paperless":
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, *_: object) -> None:
        """Exit context manager."""
        await self.close()

    def __init__(
        self,
        url: str,
        token: str | None = None,
        *,
        client: httpx.AsyncClient | None = None,
        request_args: dict[str, Any] | None = None,
        request_api_version: int | None = None,
    ) -> None:
        """Initialize a `Paperless` instance.

        You have to permit either a client, or an url / token pair.

        `url`: A hostname or IP-address as string.
        `token`: An api token created in Paperless Django settings, or via the helper function.
        `client`: A custom `httpx.AsyncClient` object, if existing.
        `request_args` are passed to each request method call as additional kwargs.
        """
        self._base_url = self._create_base_url(url)
        self._cache = PaperlessCache()
        self._initialized = False
        self._request_api_version = request_api_version or API_VERSION
        self._request_args = request_args or {}
        self._client = client
        self._token = token

        self._api_version = API_VERSION
        self._version: str | None = None

        self.logger = logging.getLogger(f"{__package__}")

    @property
    def base_url(self) -> str:
        """Return the base url of the Paperless api endpoint."""
        return self._base_url

    @property
    def cache(self) -> PaperlessCache:
        """Return the cache object."""
        return self._cache

    @property
    def is_initialized(self) -> bool:
        """Return `True` if connection is initialized."""
        return self._initialized

    @property
    def host_api_version(self) -> int:
        """Return the api version of the Paperless host."""
        return self._api_version

    @property
    def host_version(self) -> str | None:
        """Return the version of the Paperless host."""
        return self._version

    @staticmethod
    def _create_base_url(url: str) -> str:
        """Create URL from string and prepare for further use."""
        url = url.rstrip("/")
        if "://" not in url:
            url = f"https://{url}"
        if not url.startswith(("https://", "http://")):
            url = f"https://{url}"
        return url

    @staticmethod
    def _process_form(data: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, Any]]]:
        """Process form data and create httpx-compatible data/files tuples.

        Returns a tuple of (data_fields, file_fields) for httpx.
        """
        data_fields: dict[str, Any] = {}
        file_fields: list[tuple[str, Any]] = []

        def _add_form_value(name: str | None, value: Any) -> None:
            if value is None:
                return
            if isinstance(value, dict):
                for dict_key, dict_value in value.items():
                    _add_form_value(dict_key, dict_value)
                return
            if isinstance(value, list | set):
                for list_value in value:
                    _add_form_value(name, list_value)
                return
            if isinstance(value, tuple) and name is not None:
                if len(value) == 2:
                    file_fields.append((name, (f"{value[1]}", BytesIO(value[0]))))
                else:
                    file_fields.append((name, BytesIO(value[0])))
                return
            if isinstance(value, bytes) and name is not None:
                file_fields.append((name, BytesIO(value)))
                return
            if name is not None:
                if name in data_fields:
                    existing = data_fields[name]
                    if isinstance(existing, list):
                        existing.append(f"{value}")
                    else:
                        data_fields[name] = [existing, f"{value}"]
                else:
                    data_fields[name] = f"{value}"

        _add_form_value(None, data)
        return data_fields, file_fields

    @staticmethod
    async def generate_api_token(
        url: str,
        username: str,
        password: str,
        client: httpx.AsyncClient | None = None,
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
        external_client = client is not None
        client = client or httpx.AsyncClient()
        try:
            url = url.rstrip("/")
            json_data = {
                "username": username,
                "password": password,
            }
            res = await client.post(f"{url}{API_PATH['token']}", json=json_data)
            data = res.json()
            res.raise_for_status()
            return str(data["token"])
        except (json.JSONDecodeError, KeyError) as exc:
            message = "Token is missing in response."
            raise BadJsonResponseError(message) from exc
        except httpx.HTTPStatusError as exc:
            raise JsonResponseWithError(payload={"error": data}) from exc
        finally:
            if not external_client:
                await client.aclose()

    async def close(self) -> None:
        """Clean up connection."""
        if self._client:
            await self._client.aclose()
        self.logger.info("Closed.")

    async def initialize(self) -> None:
        """Initialize and test the connection to DRF."""
        res = await self.request("get", API_PATH["index"])
        try:
            res.raise_for_status()
            self._api_version = self._request_api_version or int(
                res.headers.get("x-api-version", API_VERSION)
            )
            self._version = res.headers.get("x-version", None)
            res.json()
        except (httpx.HTTPStatusError, ValueError) as exc:
            raise InitializationError from exc

        # initialize services
        for attr, service_cls in self._service_map.items():
            setattr(self, attr, service_cls(self))

        self._initialized = True
        self.logger.info("Initialized.")

    async def request(  # noqa: PLR0913 # pylint: disable=too-many-positional-arguments
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a request to the Paperless api and return the `httpx.Response`.

        This method provides a little interface for utilizing multipart form data.

        `method`: A http method: get, post, patch, put, delete, head, options
        `path`: A path to the endpoint or a string url.
        `json`: A dict containing the json data.
        `data`: A dict containing the data to send in the request body.
        `form`: A dict with form data, which gets converted to multipart form data.
        `params`: A dict with query parameters.
        `kwargs`: Optional attributes for the `httpx.AsyncClient.request` method.
        """
        if self._client is None:
            self._client = httpx.AsyncClient()

        # add headers
        headers: dict[str, str] = {
            "Accept": f"application/json; version={self._request_api_version}",
        }
        if self._token:
            headers["Authorization"] = f"Token {self._token}"

        # Merge with any user-defined headers (optional)
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        # add request args
        kwargs.update(self._request_args)

        # overwrite data with form data when there is a form payload
        files = None
        if isinstance(form, dict):
            data, files = self._process_form(form)

        # add base path
        url = f"{self._base_url}{path}" if not path.startswith("http") else path

        try:
            res = await self._client.request(
                method=method.upper(),
                url=url,
                json=json,
                data=data,
                files=files,
                params=params,
                **kwargs,
            )
            self.logger.debug("%s (%d): %s", method.upper(), res.status_code, res.url)
        except httpx.ConnectError as err:
            raise PaperlessConnectionError from err

        # error handling for 401 and 403 codes
        if res.status_code == 401:
            try:
                error_data = res.json()
                detail = error_data.get("detail", "")
            except ValueError:
                detail = ""

            if "inactive" in detail.lower() or "deleted" in detail.lower():
                raise PaperlessInactiveOrDeletedError(res)

            raise PaperlessInvalidTokenError(res)

        if res.status_code == 403:
            raise PaperlessForbiddenError(res)

        return res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        res = await self.request(method, endpoint, **kwargs)

        content_type = res.headers.get("content-type", "")

        if res.status_code == 400 and "application/json" in content_type:
            try:
                payload = res.json()
            except ValueError:
                raise BadJsonResponseError(res) from None
            raise JsonResponseWithError(payload)

        res.raise_for_status()

        if "application/json" not in content_type:
            raise BadJsonResponseError(res)

        try:
            payload = res.json()
        except ValueError:
            raise BadJsonResponseError(res) from None

        return payload
