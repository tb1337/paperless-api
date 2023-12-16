"""PyPaperless."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .api import (
    ConsumptionTemplatesEndpoint,
    CorrespondentsEndpoint,
    CustomFieldEndpoint,
    DocumentsEndpoint,
    DocumentTypesEndpoint,
    GroupsEndpoint,
    MailAccountsEndpoint,
    MailRulesEndpoint,
    SavedViewsEndpoint,
    ShareLinkEndpoint,
    StoragePathsEndpoint,
    TagsEndpoint,
    TasksEndpoint,
    UsersEndpoint,
)
from .errors import BadRequestException
from .models.shared import ResourceType


class Paperless:
    """Retrieves and manipulates data from and to paperless via REST."""

    def __init__(
        self,
        host: str,
        token: str,
        request_opts: dict[str, Any] | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        """
        Initialize the Paperless api instance.

        Parameters:
        * host: the hostname or IP-address of Paperless as string.
        * token: provide an api token created in Paperless Django settings.
        * session: provide an existing aiohttp ClientSession.
        """
        self._host = host
        self._token = token
        self._request_opts = request_opts
        self._session = session
        self._initialized = False

        self.logger = logging.getLogger(f"{__package__}[{host}]")
        # endpoints
        self._consumption_templates: ConsumptionTemplatesEndpoint | None = None
        self._correspondents: CorrespondentsEndpoint | None = None
        self._custom_fields: CustomFieldEndpoint | None = None
        self._documents: DocumentsEndpoint | None = None
        self._document_types: DocumentTypesEndpoint | None = None
        self._groups: GroupsEndpoint | None = None
        self._mail_accounts: MailAccountsEndpoint | None = None
        self._mail_rules: MailRulesEndpoint | None = None
        self._saved_views: SavedViewsEndpoint | None = None
        self._share_links: ShareLinkEndpoint | None = None
        self._storage_paths: StoragePathsEndpoint | None = None
        self._tags: TagsEndpoint | None = None
        self._tasks: TasksEndpoint | None = None
        self._users: UsersEndpoint | None = None

    @property
    def host(self) -> str | None:
        """Return the hostname of Paperless."""
        return self._host

    @property
    def consumption_templates(self) -> ConsumptionTemplatesEndpoint | None:
        """Gateway to consumption templates."""
        return self._consumption_templates

    @property
    def correspondents(self) -> CorrespondentsEndpoint | None:
        """Gateway to correspondents."""
        return self._correspondents

    @property
    def custom_fields(self) -> CustomFieldEndpoint | None:
        """Gateway to custom fields."""
        return self._custom_fields

    @property
    def documents(self) -> DocumentsEndpoint | None:
        """Gateway to document types."""
        return self._documents

    @property
    def document_types(self) -> DocumentTypesEndpoint | None:
        """Gateway to document types."""
        return self._document_types

    @property
    def groups(self) -> GroupsEndpoint | None:
        """Gateway to groups."""
        return self._groups

    @property
    def mail_accounts(self) -> MailAccountsEndpoint | None:
        """Gateway to mail accounts."""
        return self._mail_accounts

    @property
    def mail_rules(self) -> MailRulesEndpoint | None:
        """Gateway to mail rules."""
        return self._mail_rules

    @property
    def saved_views(self) -> SavedViewsEndpoint | None:
        """Gateway to saved views."""
        return self._saved_views

    @property
    def share_links(self) -> ShareLinkEndpoint | None:
        """Gateway to share links."""
        return self._share_links

    @property
    def storage_paths(self) -> StoragePathsEndpoint | None:
        """Gateway to storage paths."""
        return self._storage_paths

    @property
    def tags(self) -> TagsEndpoint | None:
        """Gateway to tags."""
        return self._tags

    @property
    def tasks(self) -> TasksEndpoint | None:
        """Gateway to tasks."""
        return self._tasks

    @property
    def users(self) -> UsersEndpoint | None:
        """Gateway to users."""
        return self._users

    async def initialize(self):
        """Initialize the connection to the api and fetch the endpoints."""
        result = await self.request("get", "")

        self._consumption_templates = ConsumptionTemplatesEndpoint(
            self, result.pop(ResourceType.CONSUMPTION_TEMPLATES)
        )
        self._correspondents = CorrespondentsEndpoint(self, result.pop(ResourceType.CORRESPONDENTS))
        self._custom_fields = CustomFieldEndpoint(self, result.pop(ResourceType.CUSTOM_FIELDS))
        self._documents = DocumentsEndpoint(self, result.pop(ResourceType.DOCUMENTS))
        self._document_types = DocumentTypesEndpoint(self, result.pop(ResourceType.DOCUMENT_TYPES))
        self._groups = GroupsEndpoint(self, result.pop(ResourceType.GROUPS))
        self._mail_accounts = MailAccountsEndpoint(self, result.pop(ResourceType.MAIL_ACCOUNTS))
        self._mail_rules = MailRulesEndpoint(self, result.pop(ResourceType.MAIL_RULES))
        self._saved_views = SavedViewsEndpoint(self, result.pop(ResourceType.SAVED_VIEWS))
        self._share_links = ShareLinkEndpoint(self, result.pop(ResourceType.SHARE_LINKS))
        self._storage_paths = StoragePathsEndpoint(self, result.pop(ResourceType.STORAGE_PATHS))
        self._tags = TagsEndpoint(self, result.pop(ResourceType.TAGS))
        self._tasks = TasksEndpoint(self, result.pop(ResourceType.TASKS))
        self._users = UsersEndpoint(self, result.pop(ResourceType.USERS))

        self._initialized = True
        self.logger.info("Paperless initialized. Unused endpoints: %s", ", ".join(result))

    async def close(self):
        """Clean up connection."""
        if self._session:
            await self._session.close()
        self.logger.info("Paperless closed.")

    async def request(self, method: str, endpoint: str, **kwargs):
        """Make request on the api and return response data."""
        if not isinstance(self._session, aiohttp.ClientSession):
            self._session = aiohttp.ClientSession()

        url = endpoint if endpoint.startswith("http") else f"http://{self.host}/api/{endpoint}"

        kwargs.update(self._request_opts)

        if "headers" not in kwargs:
            kwargs["headers"] = {}

        kwargs["headers"].update(
            {
                "accept": "application/json; version=2",
                "authorization": f"Token {self._token}",
            }
        )

        async with self._session.request(method, url, **kwargs) as res:
            self.logger.debug("Request %s (%d): %s", method, res.status, res.url)
            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            # no content
            if res.status == 204:
                return {}
            res.raise_for_status()
            if res.content_type == "application/json":
                return await res.json()
            return await res.read()

    async def __aenter__(self) -> Paperless:
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, exc_tb) -> bool | None:
        """Exit context manager."""
        await self.close()
        if exc:
            raise exc
        return exc_type
