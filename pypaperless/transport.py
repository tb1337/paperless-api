"""Provide the HTTP transport layer for PyPaperless."""

from json import JSONDecodeError
from typing import Any

import httpx

from .const import API_PATH, API_VERSION
from .exceptions import (
    BadJsonResponseError,
    ForbiddenError,
    InactiveOrDeletedError,
    InvalidTokenError,
    JsonResponseWithError,
    PaperlessConnectionError,
)
from .utils import normalize_base_url, process_form_data


class PaperlessTransport:
    """Handle all HTTP communication with a Paperless-ngx instance.

    Constructed by :class:`~pypaperless.client.PaperlessClient` and passed to
    :class:`~pypaperless.runtime.PaperlessRuntime`.  Not intended for direct
    instantiation by library consumers.

    Args:
        base_url: Hostname, IP-address, or full URL string.
        token:    API token, or ``None`` for anonymous access.
        client:   Optional :class:`httpx.AsyncClient` to reuse.

    Example::

        transport = PaperlessTransport("localhost:8000", "mytoken")
        response = await transport.request("get", "/api/documents/")

    """

    def __init__(
        self,
        base_url: str,
        token: str | None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize a :class:`PaperlessTransport` instance."""
        self._base_url = normalize_base_url(base_url)
        self._token = token
        self._httpx_client = client

    @property
    def base_url(self) -> str:
        """Return the base URL of the Paperless API endpoint."""
        return self._base_url

    async def close(self) -> None:
        """Close the underlying :class:`httpx.AsyncClient`, if open."""
        if self._httpx_client:
            await self._httpx_client.aclose()

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

        Example::

            res = await transport.request("get", "/api/documents/", params={"page": 1})

        """
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient()

        headers: dict[str, str] = {
            "Accept": f"application/json; version={API_VERSION}",
        }
        if self._token:
            headers["Authorization"] = f"Token {self._token}"

        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        files = None
        if isinstance(form, dict):
            data, files = process_form_data(form)

        url = f"{self._base_url}{path}" if not path.startswith("http") else path

        try:
            res = await self._httpx_client.request(
                method=method.upper(),
                url=url,
                json=json,
                data=data,
                files=files,
                params=params,
                **kwargs,
            )
        except httpx.ConnectError as err:
            raise PaperlessConnectionError from err

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
        """Make a request to the API and return the parsed JSON payload.

        Args:
            method:   HTTP method string.
            endpoint: API path relative to the base URL.
            **kwargs: Forwarded to :meth:`request`.

        Example::

            data = await transport.request_json("get", "/api/documents/42/")

        """
        res = await self.request(method, endpoint, **kwargs)

        if "application/json" not in res.headers.get("content-type", ""):
            res.raise_for_status()
            raise BadJsonResponseError(res)

        try:
            payload = res.json()
        except ValueError:
            raise BadJsonResponseError(res) from None

        if res.status_code == 400:
            raise JsonResponseWithError(payload)

        res.raise_for_status()
        return payload


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

        token = await generate_api_token("example.com:8000", "api_user", "secret")
        async with PaperlessClient("example.com:8000", token) as paperless:
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
