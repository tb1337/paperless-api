"""Tests for pypaperless."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from aiohttp.web_exceptions import HTTPNotFound

from pypaperless import Paperless

from .const import PAPERLESS_TEST_URL
from .data.v0_0_0 import V0_0_0_GET_CORRESPONDENTS, V0_0_0_GET_PATHS

API_DATA = {
    "0.0.0": {
        "GET_PATHS": V0_0_0_GET_PATHS,
        "GET_CORRESPONDENTS": V0_0_0_GET_CORRESPONDENTS,
    },
    "1.8.0": {
        "GET_PATHS": V0_0_0_GET_PATHS,
    },
}

API_PATHS = {
    "get": {
        "": "GET_PATHS",
        "correspondents": "GET_CORRESPONDENTS",
    },
}


class PaperlessMock(Paperless):
    """Mock Paperless."""

    def __init__(
        self,
        url,
        token,
        request_opts=None,
        session=None,
    ):
        """Construct MockPaperless."""
        Paperless.__init__(
            self,
            url,
            token,
            request_opts,
            session,
        )

        self.version = "0.0.0"

    @asynccontextmanager
    async def generate_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> AsyncGenerator["FakeClientResponse", None]:
        """Create a client response object for further use."""
        path = path.rstrip("/") + "/"  # check and add trailing slash

        if isinstance(self._request_opts, dict):
            kwargs.update(self._request_opts)

        kwargs.setdefault("headers", {})
        kwargs["headers"].update(
            {
                "accept": "application/json; version=2",
                "authorization": f"Token {self._token}",
            }
        )

        yield FakeClientResponse(self, method, path)


class FakeClientResponse:
    """A fake response object."""

    def __init__(self, api, method, path: str):
        """Construct fake response."""
        self._api = api
        self._url = path
        path = path.replace(PAPERLESS_TEST_URL, "").rstrip("/").lstrip("/api/")
        self._pathname = path

        endpoint = API_PATHS[method].setdefault(self._pathname, None)
        if endpoint:
            version = self._api.version if self._api.version in API_DATA else "0.0.0"
            self._data = API_DATA[version][endpoint].copy()
        else:
            self._data = None

    @property
    def headers(self):
        """Headers."""
        return {
            "x-version": self._api.version,
        }

    @property
    def status(self):
        """Status."""
        if not self._data:
            return 404
        return 200

    @property
    def url(self):
        """Url."""
        return self._url

    @property
    def content_type(self):
        """Content type."""
        if isinstance(self._data, dict | tuple | list):
            return "application/json"
        return "text"

    def raise_for_status(self):
        """Raise for status."""
        if self.status != 200:
            raise HTTPNotFound()

    async def json(self):
        """Json."""
        return self._data
