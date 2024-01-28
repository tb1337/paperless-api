"""PyPaperless sessions."""

from typing import Any

import aiohttp
from yarl import URL

from .exceptions import RequestException


class PaperlessSession:
    """Provide an interface to http requests."""

    _session: aiohttp.ClientSession

    def __init__(
        self,
        base_url: str | URL,
        token: str,
        **kwargs: Any,
    ) -> None:
        """Initialize a `PaperlessSession` instance.

        Accepts custom `aiohttp.ClientSession` instances as well.
        """
        self._initialized = False
        self._request_args = kwargs
        self._token = token
        self._base_url = self._create_base_url(base_url)

    def __str__(self) -> str:
        """Return `base_url` host as string."""
        return f"{self._base_url.host}"

    @property
    def is_initialized(self) -> bool:
        """Is init."""
        return self._initialized

    @staticmethod
    def _create_base_url(url: str | URL) -> URL:
        """Create URL from string or URL and prepare for further use."""
        # reverse compatibility, fall back to https
        if isinstance(url, str) and "://" not in url:
            url = f"https://{url}".rstrip("/")
        url = URL(url)

        # scheme check. fall back to https
        if url.scheme not in ("https", "http"):
            url = URL(url).with_scheme("https")

        return url

    def _process_form(
        self,
        data: dict[str, Any],
    ) -> aiohttp.FormData:
        """Process form data and create a `aiohttp.FormData` object.

        Every field item gets converted to a string-like object.
        """
        form = aiohttp.FormData()

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
                form.add_field(name, f"{value}", **params)

        _add_form_value(None, data)
        return form

    async def close(self) -> None:
        """Clean up connection."""
        if self.is_initialized:
            await self._session.close()

    async def initialize(self) -> None:
        """Initialize session."""
        self._session = aiohttp.ClientSession()
        self._session.headers.update(
            {
                "Accept": "application/json; version=2",
                "Authorization": f"Token {self._token}",
            }
        )
        self._initialized = True

    async def request(  # pylint: disable=too-many-arguments
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | aiohttp.FormData | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, str | int] | None = None,
        **kwargs: Any,
    ) -> aiohttp.ClientResponse:
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
        if not self.is_initialized:
            await self.initialize()

        kwargs.update(self._request_args)

        # overwrite data with a form, when there is a form payload
        if isinstance(form, dict):
            data = self._process_form(form)

        # add base path
        url = f"{self._base_url}{path}" if not path.startswith("http") else path
        # check for trailing slash
        if URL(url).query_string == "":
            url = url.rstrip("/") + "/"

        try:
            return await self._session.request(
                method=method,
                url=url,
                data=data,
                json=json,
                params=params,
                **kwargs,
            )
        except Exception as exc:
            raise RequestException(exc, (method, url, params), kwargs) from None
