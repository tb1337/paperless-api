"""Tests for pypaperless."""

from typing import Any

import aiohttp
from aiohttp.web_exceptions import HTTPNotFound
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from yarl import URL

from pypaperless import PaperlessSession
from pypaperless.exceptions import RequestException

from .const import PAPERLESS_TEST_URL
from .util.router import FakePaperlessAPI

# mypy: ignore-errors


class PaperlessSessionMock(PaperlessSession):
    """Mock PaperlessSession."""

    def __init__(
        self,
        base_url: str | URL,
        token: str,
        **kwargs: Any,
    ) -> None:
        """Initialize PaperlessSessionMock."""
        PaperlessSession.__init__(
            self,
            base_url,
            token,
            **kwargs,
        )
        self.client = TestClient(FakePaperlessAPI)
        self.version = "0.0.0"

    async def request(  # pylint: disable=too-many-arguments
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | aiohttp.FormData | None = None,
        form: dict[str, Any] | None = None,
        params: dict[str, str | int] | None = None,
        **kwargs: Any,
    ) -> "FakeClientResponse":
        """Mock PaperlessSession.request."""
        if not self.is_initialized:
            await self.initialize()

        kwargs.setdefault("headers", {})
        kwargs["headers"].update({"x-test-ver": self.version})

        # overwrite data with a form, when there is a form payload
        if isinstance(form, dict):
            data = self._process_form(form)

        # add base path
        url = f"{self._base_url}{path}" if not path.startswith("http") else path
        # check for trailing slash
        if URL(url).query_string == "":
            url = url.rstrip("/") + "/"

        try:
            async with AsyncClient(
                app=FakePaperlessAPI,
                base_url=PAPERLESS_TEST_URL,
            ) as client:
                res = await client.request(
                    method, url, json=json, data=data, params=params, **kwargs
                )
                return FakeClientResponse(res, self.version)
        except Exception as exc:
            raise RequestException(exc, (method, url, params), kwargs) from None


class FakeClientResponse:
    """A fake response object."""

    def __init__(self, res: Response, version: str):
        """Construct fake response."""
        self.res = res
        self.version = version

    @property
    def headers(self):
        """Headers."""
        return {**self.res.headers, "x-version": self.version}

    @property
    def status(self):
        """Status."""
        return self.res.status_code

    @property
    def url(self):
        """Url."""
        return f"{self.res.url}"

    @property
    def content_type(self):
        """Content type."""
        return self.res.headers.setdefault("content-type", "application/json")

    def raise_for_status(self):
        """Raise for status."""
        if self.status != 200:
            raise HTTPNotFound()

    async def json(self):
        """Json."""
        return self.res.json()

    async def text(self):
        """Text."""
        return self.res.content

    async def read(self):
        """Read."""
        return self.res.content
