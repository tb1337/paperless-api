"""PyPaperless."""

import logging
from json import JSONDecodeError
from typing import Any, overload

import httpx

from . import services
from .const import API_PATH, API_VERSION
from .exceptions import (
    BadJsonResponseError,
    ForbiddenError,
    InactiveOrDeletedError,
    InitializationError,
    InvalidTokenError,
    JsonResponseWithError,
    PaperlessConnectionError,
)
from .settings import PaperlessConfig
from .utils import normalize_base_url, process_form_data


class Paperless:
    """Async client for the Paperless-ngx REST API.

    Use as an async context manager (recommended), or call
    :meth:`initialize` and :meth:`close` manually::

        async with Paperless("localhost:8000", "your-token") as paperless:
            doc = await paperless.documents(42)
            print(doc.title)

    """

    async def __aenter__(self) -> "Paperless":
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, *_: object) -> None:
        """Exit context manager."""
        await self.close()

    @overload
    def __init__(
        self,
        url: str,
        token: str | None = ...,
        *,
        client: httpx.AsyncClient | None = ...,
        request_api_version: int | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        config: PaperlessConfig,
        client: httpx.AsyncClient | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        client: httpx.AsyncClient | None = ...,
    ) -> None: ...

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        *,
        config: PaperlessConfig | None = None,
        client: httpx.AsyncClient | None = None,
        request_api_version: int | None = None,
    ) -> None:
        """Initialize a :class:`Paperless` instance.

        Three configuration modes are supported.

        Explicit URL and token::

            paperless = Paperless("localhost:8000", "your-token")

        Config object via :class:`~pypaperless.settings.PaperlessConfig`::

            cfg = PaperlessConfig(url="localhost:8000", token="your-token")
            paperless = Paperless(config=cfg)

        Environment variables — set ``PYPAPERLESS_URL`` and optionally
        ``PYPAPERLESS_TOKEN`` / ``PYPAPERLESS_REQUEST_API_VERSION``::

            paperless = Paperless()

        Args:
            url:                  A hostname, IP-address, or full URL string.
            token:                An API token from Paperless Django admin or via
                                  :meth:`generate_api_token`.
            config:               A :class:`~pypaperless.settings.PaperlessConfig`
                                  with all connection parameters.
            client:               A custom :class:`httpx.AsyncClient` to use for
                                  requests.
            request_api_version:  Override the API version header sent with each
                                  request.

        """
        if config is not None:
            _url = config.url
            _token = config.token
            _request_api_version = config.request_api_version
        elif url is not None:
            _url = url
            _token = token
            _request_api_version = request_api_version or API_VERSION
        else:
            # No args supplied — read everything from environment variables.
            _cfg = PaperlessConfig()
            _url = _cfg.url
            _token = _cfg.token
            _request_api_version = _cfg.request_api_version

        self._base_url = normalize_base_url(_url)
        self._client = client
        self._initialized = False
        self._request_api_version = _request_api_version
        self._token = _token

        self._api_version = API_VERSION
        self._version: str | None = None

        # PyPaperless services
        self.cache = services.CacheService(self)

        # API services
        self.bulk_edit_objects = services.BulkEditObjectsService(self)
        self.config = services.ConfigService(self)
        self.correspondents = services.CorrespondentService(self)
        self.custom_fields = services.CustomFieldService(self)
        self.documents = services.DocumentService(self)
        self.document_types = services.DocumentTypeService(self)
        self.groups = services.GroupService(self)
        self.mail_accounts = services.MailAccountService(self)
        self.mail_rules = services.MailRuleService(self)
        self.processed_mail = services.ProcessedMailService(self)
        self.profile = services.ProfileService(self)
        self.saved_views = services.SavedViewService(self)
        self.search = services.SearchService(self)
        self.share_links = services.ShareLinkService(self)
        self.statistics = services.StatisticService(self)
        self.remote_version = services.RemoteVersionService(self)
        self.status = services.StatusService(self)
        self.storage_paths = services.StoragePathService(self)
        self.tags = services.TagService(self)
        self.tasks = services.TaskService(self)
        self.trash = services.TrashService(self)
        self.users = services.UserService(self)
        self.workflows = services.WorkflowService(self)

        self.logger = logging.getLogger(f"{__package__}")

    @property
    def base_url(self) -> str:
        """Return the base url of the Paperless api endpoint."""
        return self._base_url

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
    async def generate_api_token(
        url: str,
        username: str,
        password: str,
        client: httpx.AsyncClient | None = None,
    ) -> str:
        """Request Paperless to generate an API token for the given credentials.

        .. warning::

            The token request is sent as plain HTTP — do not use this in
            production or on untrusted networks.

        Args:
            url:      Hostname, IP-address, or full URL of the Paperless instance.
            username: Paperless user name.
            password: Paperless user password.
            client:   Optional :class:`httpx.AsyncClient` to reuse.  A new client
                      is created and closed automatically when not provided.

        Example::

            token = await Paperless.generate_api_token(
                "example.com:8000", "api_user", "secret"
            )
            async with Paperless("example.com:8000", token) as paperless:
                ...

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
        except (JSONDecodeError, KeyError) as exc:
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
        """Initialize and validate the connection to Paperless.

        Called automatically by :meth:`__aenter__`.  Required when **not**
        using the async context manager::

            paperless = Paperless("localhost:8000", "your-token")
            await paperless.initialize()
            # … use paperless …
            await paperless.close()

        """
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

        self._initialized = True
        self.logger.info("Initialized.")

    async def request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Send a request to the Paperless API and return the raw :class:`httpx.Response`.

        Args:
            method: HTTP method string: ``"get"``, ``"post"``, ``"patch"``,
                    ``"put"``, ``"delete"``, ``"head"``, or ``"options"``.
            path:   API path relative to the base URL, or an absolute URL string.
            json:   Dict to send as JSON request body.
            data:   Dict to send as form-encoded body.
            form:   Dict converted to multipart form data (overrides *data*).
            params: Dict of query string parameters.
            **kwargs: Forwarded to :meth:`httpx.AsyncClient.request`.

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

        # overwrite data with form data when there is a form payload
        files = None
        if isinstance(form, dict):
            data, files = process_form_data(form)

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
                raise InactiveOrDeletedError(res)

            raise InvalidTokenError(res)

        if res.status_code == 403:
            raise ForbiddenError(res)

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
