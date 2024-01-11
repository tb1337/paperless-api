"""Tests for pypaperless."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from aiohttp.web_exceptions import HTTPNotFound
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response

from pypaperless import Paperless

from .const import PAPERLESS_TEST_URL
from .util.router import FakePaperlessAPI


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
        self.client = TestClient(FakePaperlessAPI)

    @asynccontextmanager
    async def generate_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> AsyncGenerator["FakeClientResponse", None]:
        """Create a client response object for further use."""
        path = path.rstrip("/") + "/"  # check and add trailing slash

        kwargs.setdefault("headers", {})
        kwargs["headers"].update(
            {
                "accept": "application/json; version=2",
                "authorization": f"Token {self._token}",
                "x-test-ver": self.version,
            }
        )

        # we fake form data to json payload as we don't want to mess with FastAPI forms
        if "form" in kwargs:
            json = {}
            for item in kwargs.pop("form"):
                if item[0] == "tags":
                    json.setdefault("tags", [])
                    json["tags"].append(item[1])
                else:
                    json[item[0]] = item[1].decode() if isinstance(item[1], bytes) else item[1]
            kwargs["json"] = json

        # finally, request
        async with AsyncClient(
            app=FakePaperlessAPI,
            base_url=PAPERLESS_TEST_URL,
        ) as ac:
            res = await ac.request(method, path, **kwargs)
            yield FakeClientResponse(res, self.version)  # wrap httpx response


class FakeClientResponse:
    """A fake response object."""

    def __init__(self, res: Response, version):
        """Construct fake response."""
        self.res = res
        self.version = version

    @property
    def headers(self):
        """Headers."""
        return {**self.res.headers, **{"x-version": self.version}}

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

    async def read(self):
        """Read."""
        return self.res.content
