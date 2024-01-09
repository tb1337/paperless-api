"""Tests for pypaperless."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from pypaperless import Paperless

from .const import PAPERLESS_TEST_URL
from .data.v0_0_0 import V0_0_0_PATHS

API_DATA = {
    "0.0.0": {
        "PATHS": V0_0_0_PATHS,
    },
    "1.8.0": {
        "PATHS": V0_0_0_PATHS,
    },
}

API_PATHS = {
    "get": {
        "": "PATHS",
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
        self.api = api
        path = path.replace(PAPERLESS_TEST_URL, "").rstrip("/")

        endpoint = API_PATHS[method].setdefault(path, None)
        if endpoint:
            version = self.api.version if self.api.version in API_DATA else "0.0.0"
            self.data = API_DATA[version][endpoint].copy()
        else:
            self.data = {}

    @property
    def headers(self):
        """Headers."""
        return {
            "x-version": self.api.version,
        }

    async def json(self):
        """Json."""
        return self.data
