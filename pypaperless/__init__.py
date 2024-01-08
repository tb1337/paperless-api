"""PyPaperless."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import aiohttp
from yarl import URL

from .controllers import (
    ConsumptionTemplatesController,
    CorrespondentsController,
    CustomFieldsController,
    DocumentsController,
    DocumentTypesController,
    GroupsController,
    MailAccountsController,
    MailRulesController,
    SavedViewsController,
    ShareLinksController,
    StoragePathsController,
    TagsController,
    TasksController,
    UsersController,
)
from .errors import BadRequestException, DataNotExpectedException
from .models.shared import ResourceType
from .util import create_url_from_input


class Paperless:  # pylint: disable=too-many-instance-attributes
    """Retrieves and manipulates data from and to paperless via REST."""

    def __init__(
        self,
        url: str | URL,
        token: str,
        request_opts: dict[str, Any] | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        """
        Initialize the Paperless api instance.

        Parameters:
        * host: the hostname or IP-address of Paperless as string, or yarl.URL object.
        * token: provide an api token created in Paperless Django settings.
        * session: provide an existing aiohttp ClientSession.
        """
        self._url = create_url_from_input(url)
        self._token = token
        self._request_opts = request_opts
        self._session = session
        self._initialized = False
        self.logger = logging.getLogger(f"{__package__}[{self._url.host}]")

        # endpoints
        self._consumption_templates: ConsumptionTemplatesController | None = None
        self._correspondents: CorrespondentsController | None = None
        self._custom_fields: CustomFieldsController | None = None
        self._documents: DocumentsController | None = None
        self._document_types: DocumentTypesController | None = None
        self._groups: GroupsController | None = None
        self._mail_accounts: MailAccountsController | None = None
        self._mail_rules: MailRulesController | None = None
        self._saved_views: SavedViewsController | None = None
        self._share_links: ShareLinksController | None = None
        self._storage_paths: StoragePathsController | None = None
        self._tags: TagsController | None = None
        self._tasks: TasksController | None = None
        self._users: UsersController | None = None

    @property
    def url(self) -> URL:
        """Return the url of Paperless."""
        return self._url

    @property
    def is_initialized(self) -> bool:
        """Return if connection is initialized."""
        return self._initialized

    @property
    def consumption_templates(self) -> ConsumptionTemplatesController | None:
        """Gateway to consumption templates."""
        return self._consumption_templates

    @property
    def correspondents(self) -> CorrespondentsController | None:
        """Gateway to correspondents."""
        return self._correspondents

    @property
    def custom_fields(self) -> CustomFieldsController | None:
        """Gateway to custom fields."""
        return self._custom_fields

    @property
    def documents(self) -> DocumentsController | None:
        """Gateway to document types."""
        return self._documents

    @property
    def document_types(self) -> DocumentTypesController | None:
        """Gateway to document types."""
        return self._document_types

    @property
    def groups(self) -> GroupsController | None:
        """Gateway to groups."""
        return self._groups

    @property
    def mail_accounts(self) -> MailAccountsController | None:
        """Gateway to mail accounts."""
        return self._mail_accounts

    @property
    def mail_rules(self) -> MailRulesController | None:
        """Gateway to mail rules."""
        return self._mail_rules

    @property
    def saved_views(self) -> SavedViewsController | None:
        """Gateway to saved views."""
        return self._saved_views

    @property
    def share_links(self) -> ShareLinksController | None:
        """Gateway to share links."""
        return self._share_links

    @property
    def storage_paths(self) -> StoragePathsController | None:
        """Gateway to storage paths."""
        return self._storage_paths

    @property
    def tags(self) -> TagsController | None:
        """Gateway to tags."""
        return self._tags

    @property
    def tasks(self) -> TasksController | None:
        """Gateway to tasks."""
        return self._tasks

    @property
    def users(self) -> UsersController | None:
        """Gateway to users."""
        return self._users

    async def initialize(self) -> None:
        """Initialize the connection to the api and fetch the endpoints."""
        self.logger.info("Fetching api endpoints.")

        res = await self.request_json("get", f"{self._url}")

        self._consumption_templates = ConsumptionTemplatesController(
            self, res.pop(ResourceType.CONSUMPTION_TEMPLATES)
        )
        self._correspondents = CorrespondentsController(self, res.pop(ResourceType.CORRESPONDENTS))
        self._custom_fields = CustomFieldsController(self, res.pop(ResourceType.CUSTOM_FIELDS))
        self._documents = DocumentsController(self, res.pop(ResourceType.DOCUMENTS))
        self._document_types = DocumentTypesController(self, res.pop(ResourceType.DOCUMENT_TYPES))
        self._groups = GroupsController(self, res.pop(ResourceType.GROUPS))
        self._mail_accounts = MailAccountsController(self, res.pop(ResourceType.MAIL_ACCOUNTS))
        self._mail_rules = MailRulesController(self, res.pop(ResourceType.MAIL_RULES))
        self._saved_views = SavedViewsController(self, res.pop(ResourceType.SAVED_VIEWS))
        self._share_links = ShareLinksController(self, res.pop(ResourceType.SHARE_LINKS))
        self._storage_paths = StoragePathsController(self, res.pop(ResourceType.STORAGE_PATHS))
        self._tags = TagsController(self, res.pop(ResourceType.TAGS))
        self._tasks = TasksController(self, res.pop(ResourceType.TASKS))
        self._users = UsersController(self, res.pop(ResourceType.USERS))

        self._initialized = True

        if len(res) > 0:
            self.logger.debug("Unused endpoints: %s", ", ".join(res))
        self.logger.info("Initialized.")

    async def close(self) -> None:
        """Clean up connection."""
        if self._session:
            await self._session.close()
        self.logger.info("Closed.")

    @asynccontextmanager
    async def generate_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> AsyncGenerator[aiohttp.ClientResponse, None]:
        """Create a client response object for further use."""
        if not isinstance(self._session, aiohttp.ClientSession):
            self._session = aiohttp.ClientSession()

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

        async with self._session.request(method, path, **kwargs) as res:
            yield res

    async def request_json(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """Make a request to the api and parse response json to dict."""
        async with self.generate_request(method, endpoint, **kwargs) as res:
            self.logger.debug("Json-Request %s (%d): %s", method.upper(), res.status, res.url)

            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            # no content, in most cases on DELETE method
            if res.status == 204:
                return {}
            res.raise_for_status()

            if res.content_type != "application/json":
                raise DataNotExpectedException(f"Content-type is not json! {res.content_type}")

            return await res.json()

    async def request_file(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> bytes:
        """Make a request to the api and return response as bytes."""
        async with self.generate_request(method, endpoint, **kwargs) as res:
            self.logger.debug("File-Request %s (%d): %s", method.upper(), res.status, res.url)

            # bad request
            if res.status == 400:
                raise BadRequestException(f"{await res.text()}")
            res.raise_for_status()

            return await res.read()

    async def __aenter__(self) -> "Paperless":
        """Return context manager."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, exc_tb: Any) -> Any | None:
        """Exit context manager."""
        await self.close()
        if exc:
            raise exc
        return exc_type
