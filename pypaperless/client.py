"""PyPaperless."""

import logging
from json import JSONDecodeError
from typing import Any

import httpx

from . import services
from .const import API_PATH, API_VERSION
from .exceptions import (
    BadJsonResponseError,
    InitializationError,
    JsonResponseWithError,
    PaperlessConnectionError,
    PaperlessForbiddenError,
    PaperlessInactiveOrDeletedError,
    PaperlessInvalidTokenError,
)
from .utils import normalize_base_url, process_form_data


class Paperless:
    """Retrieves and manipulates data from and to Paperless via REST."""

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
        request_api_version: int | None = None,
    ) -> None:
        """Initialize a `Paperless` instance.

        You have to permit either a client, or an url / token pair.

        `url`: A hostname or IP-address as string.
        `token`: An api token created in Paperless Django settings, or via the helper function.
        `client`: A custom `httpx.AsyncClient` object, if existing.
        """
        self._base_url = normalize_base_url(url)
        self._client = client
        self._initialized = False
        self._request_api_version = request_api_version or API_VERSION
        self._token = token

        self._api_version = API_VERSION
        self._version: str | None = None

        # PyPaperless services
        self.cache = services.CacheService(self)

        # API services
        self.config = services.ConfigService(self)
        self.correspondents = services.CorrespondentService(self)
        self.custom_fields = services.CustomFieldService(self)
        self.documents = services.DocumentService(self)
        self.document_types = services.DocumentTypeService(self)
        self.groups = services.GroupService(self)
        self.mail_accounts = services.MailAccountService(self)
        self.mail_rules = services.MailRuleService(self)
        self.processed_mail = services.ProcessedMailService(self)
        self.saved_views = services.SavedViewService(self)
        self.share_links = services.ShareLinkService(self)
        self.statistics = services.StatisticService(self)
        self.remote_version = services.RemoteVersionService(self)
        self.status = services.StatusService(self)
        self.storage_paths = services.StoragePathService(self)
        self.tags = services.TagService(self)
        self.tasks = services.TaskService(self)
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
