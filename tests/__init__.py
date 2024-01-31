"""Tests for pypaperless."""

from dataclasses import dataclass
from typing import Any

import aiohttp
from aiohttp.web_exceptions import HTTPNotFound
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from yarl import URL

from pypaperless import PaperlessSession, helpers
from pypaperless.const import PaperlessResource
from pypaperless.exceptions import RequestException
from pypaperless.models import (
    Correspondent,
    CorrespondentDraft,
    CustomField,
    CustomFieldDraft,
    Document,
    DocumentDraft,
    DocumentType,
    DocumentTypeDraft,
    Group,
    MailAccount,
    MailRule,
    SavedView,
    ShareLink,
    ShareLinkDraft,
    StoragePath,
    StoragePathDraft,
    Tag,
    TagDraft,
    Task,
    User,
    Workflow,
)
from pypaperless.models.common import (
    CustomFieldType,
    MatchingAlgorithmType,
    ShareLinkFileVersionType,
)

from .const import PAPERLESS_TEST_URL
from .util.router import FakePaperlessAPI

# mypy: ignore-errors


@dataclass
class ResourceTestMapping:
    """Mapping for test cases."""

    resource: str
    helper_cls: type
    model_cls: type
    draft_cls: type | None = None
    draft_defaults: dict[str, Any] | None = None


CORRESPONDENT_MAP = ResourceTestMapping(
    PaperlessResource.CORRESPONDENTS,
    helpers.CorrespondentHelper,
    Correspondent,
    CorrespondentDraft,
    {
        "name": "New Correspondent",
        "match": "",
        "matching_algorithm": MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)
CUSTOM_FIELD_MAP = ResourceTestMapping(
    PaperlessResource.CUSTOM_FIELDS,
    helpers.CustomFieldHelper,
    CustomField,
    CustomFieldDraft,
    {
        "name": "New Custom Field",
        "data_type": CustomFieldType.BOOLEAN,
    },
)
DOCUMENT_MAP = ResourceTestMapping(
    PaperlessResource.DOCUMENTS,
    helpers.DocumentHelper,
    Document,
    DocumentDraft,
    {
        "document": b"...example...content...",
        "tags": [1, 2, 3],
        "correspondent": 1,
        "document_type": 1,
        "storage_path": 1,
        "title": "New Document",
        "created": None,
        "archive_serial_number": 1,
    },
)
DOCUMENT_TYPE_MAP = ResourceTestMapping(
    PaperlessResource.DOCUMENT_TYPES,
    helpers.DocumentTypeHelper,
    DocumentType,
    DocumentTypeDraft,
    {
        "name": "New Document Type",
        "match": "",
        "matching_algorithm": MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)
GROUP_MAP = ResourceTestMapping(
    PaperlessResource.GROUPS,
    helpers.GroupHelper,
    Group,
)
MAIL_ACCOUNT_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_ACCOUNTS,
    helpers.MailAccountHelper,
    MailAccount,
)
MAIL_RULE_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_RULES,
    helpers.MailRuleHelper,
    MailRule,
)
SAVED_VIEW_MAP = ResourceTestMapping(
    PaperlessResource.SAVED_VIEWS,
    helpers.SavedViewHelper,
    SavedView,
)
SHARE_LINK_MAP = ResourceTestMapping(
    PaperlessResource.SHARE_LINKS,
    helpers.ShareLinkHelper,
    ShareLink,
    ShareLinkDraft,
    {
        "expiration": None,
        "document": 1,
        "file_version": ShareLinkFileVersionType.ORIGINAL,
    },
)
STORAGE_PATH_MAP = ResourceTestMapping(
    PaperlessResource.STORAGE_PATHS,
    helpers.StoragePathHelper,
    StoragePath,
    StoragePathDraft,
    {
        "name": "New Storage Path",
        "path": "path/to/test",
        "match": "",
        "matching_algorithm": MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)
TAG_MAP = ResourceTestMapping(
    PaperlessResource.TAGS,
    helpers.TagHelper,
    Tag,
    TagDraft,
    {
        "name": "New Tag",
        "color": "#012345",
        "text_color": "#987654",
        "is_inbox_tag": False,
        "match": "",
        "matching_algorithm": MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)
TASK_MAP = ResourceTestMapping(
    PaperlessResource.TASKS,
    helpers.TaskHelper,
    Task,
)
USER_MAP = ResourceTestMapping(
    PaperlessResource.USERS,
    helpers.UserHelper,
    User,
)

WORKFLOW_MAP = ResourceTestMapping(
    PaperlessResource.WORKFLOWS,
    helpers.WorkflowHelper,
    Workflow,
)


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

        # we fake form data to json payload as we don't want to mess with FastAPI forms
        if isinstance(form, dict):
            payload = {}
            for key, value in form.items():
                if value is None:
                    continue
                if isinstance(value, bytes):
                    value = value.decode()  # noqa PLW2901
                payload[key] = value
            json = payload

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


@dataclass(kw_only=True)
class FakeContentDisposition:
    """A fake content disposition object."""

    filename: str | None = None
    type: str | None = None


class FakeClientResponse:
    """A fake response object."""

    def __init__(self, res: Response, version: str):
        """Construct fake response."""
        self.res = res
        self.version = version

    @property
    def content_disposition(self):
        """Content disposition."""
        if "content-disposition" in self.res.headers:
            dispo, filename = tuple(self.res.headers["content-disposition"].split(";"))
            return FakeContentDisposition(type=dispo, filename=filename)
        return None

    @property
    def content_type(self):
        """Content type."""
        return self.res.headers.setdefault("content-type", "application/json")

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
