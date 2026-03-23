"""Provide the PaperlessClient class."""

import logging
from functools import cached_property

import httpx

from . import services
from .cache import PaperlessCache
from .const import API_VERSION
from .exceptions import InitializationError
from .runtime import PaperlessRuntime
from .settings import PaperlessSettings
from .transport import PaperlessTransport


class PaperlessClient:
    """Async client for the Paperless-ngx REST API.

    The primary entry point for interacting with a Paperless-ngx instance.
    Use as an async context manager (recommended), or call
    :meth:`initialize` and :meth:`close` manually.

    The preferred way to construct a client is directly::

        async with PaperlessClient("localhost:8000", "your-token") as paperless:
            doc = await paperless.documents(42)
            print(doc.title)

    For config-object or environment-variable based initialization use the
    factory class methods :meth:`from_config` and :meth:`from_env`.

    """

    async def __aenter__(self) -> "PaperlessClient":
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
    ) -> None:
        """Initialize a :class:`PaperlessClient` instance.

        Args:
            url:    A hostname, IP-address, or full URL string.
            token:  An API token from Paperless Django admin or via
                    :func:`~pypaperless.transport.generate_api_token`.
            client: A custom :class:`httpx.AsyncClient` to use for requests.

        Example::

            paperless = PaperlessClient("localhost:8000", "your-token")
            await paperless.initialize()
            doc = await paperless.documents(42)
            await paperless.close()

        """
        transport = PaperlessTransport(url, token, client)
        cache = PaperlessCache()

        self._runtime = PaperlessRuntime(transport, cache)
        self._runtime.facade = self

        self._initialized = False
        self._api_version = API_VERSION
        self._version: str | None = None

        self.logger = logging.getLogger(f"{__package__}")

    @classmethod
    def from_config(
        cls,
        config: PaperlessSettings,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> "PaperlessClient":
        """Create a :class:`PaperlessClient` from a :class:`.PaperlessSettings`.

        Args:
            config: A :class:`~pypaperless.settings.PaperlessSettings` instance.
            client: A custom :class:`httpx.AsyncClient` to use for requests.

        Example::

            cfg = PaperlessSettings(url="localhost:8000", token="your-token")
            async with PaperlessClient.from_config(cfg) as paperless:
                ...

        """
        return cls(
            config.url,
            config.token,
            client=client,
        )

    @classmethod
    def from_env(
        cls,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> "PaperlessClient":
        """Create a :class:`PaperlessClient` from environment variables.

        Reads ``PYPAPERLESS_URL`` and ``PYPAPERLESS_TOKEN`` from the environment.

        Args:
            client: A custom :class:`httpx.AsyncClient` to use for requests.

        Example::

            # export PYPAPERLESS_URL=https://paperless.example.com
            # export PYPAPERLESS_TOKEN=mytoken
            async with PaperlessClient.from_env() as paperless:
                ...

        """
        return cls.from_config(PaperlessSettings(), client=client)

    @property
    def base_url(self) -> str:
        """Return the base URL of the Paperless API endpoint."""
        return self._runtime.transport.base_url

    @property
    def is_initialized(self) -> bool:
        """Return ``True`` if the connection has been initialized."""
        return self._initialized

    @property
    def host_api_version(self) -> int:
        """Return the API version reported by the Paperless host."""
        return self._api_version

    @property
    def host_version(self) -> str | None:
        """Return the application version reported by the Paperless host."""
        return self._version

    @property
    def runtime(self) -> PaperlessRuntime:
        """Return the :class:`~pypaperless.runtime.PaperlessRuntime` shared with services."""
        return self._runtime

    async def close(self) -> None:
        """Clean up the connection."""
        await self._runtime.transport.close()
        self.logger.info("Closed.")

    async def initialize(self) -> None:
        """Initialize and validate the connection to Paperless.

        Called automatically by :meth:`__aenter__`.  Required when **not**
        using the async context manager::

            paperless = PaperlessClient("localhost:8000", "your-token")
            await paperless.initialize()
            # … use paperless …
            await paperless.close()

        """
        try:
            info = await self._runtime.transport.probe()
        except InitializationError:
            raise
        except Exception as exc:
            raise InitializationError from exc
        self._api_version = info.api_version
        self._version = info.version

        self._initialized = True
        self.logger.info("Initialized.")

    @cached_property
    def bulk_edit_objects(self) -> services.BulkEditObjectsService:
        """Return the :class:`~pypaperless.services.BulkEditObjectsService`."""
        return services.BulkEditObjectsService(self._runtime)

    @cached_property
    def config(self) -> services.ConfigService:
        """Return the :class:`~pypaperless.services.ConfigService`."""
        return services.ConfigService(self._runtime)

    @cached_property
    def correspondents(self) -> services.CorrespondentService:
        """Return the :class:`~pypaperless.services.CorrespondentService`."""
        return services.CorrespondentService(self._runtime)

    @cached_property
    def custom_fields(self) -> services.CustomFieldService:
        """Return the :class:`~pypaperless.services.CustomFieldService`."""
        return services.CustomFieldService(self._runtime)

    @cached_property
    def documents(self) -> services.DocumentService:
        """Return the :class:`~pypaperless.services.DocumentService`."""
        return services.DocumentService(self._runtime)

    @cached_property
    def document_types(self) -> services.DocumentTypeService:
        """Return the :class:`~pypaperless.services.DocumentTypeService`."""
        return services.DocumentTypeService(self._runtime)

    @cached_property
    def groups(self) -> services.GroupService:
        """Return the :class:`~pypaperless.services.GroupService`."""
        return services.GroupService(self._runtime)

    @cached_property
    def mail_accounts(self) -> services.MailAccountService:
        """Return the :class:`~pypaperless.services.MailAccountService`."""
        return services.MailAccountService(self._runtime)

    @cached_property
    def mail_rules(self) -> services.MailRuleService:
        """Return the :class:`~pypaperless.services.MailRuleService`."""
        return services.MailRuleService(self._runtime)

    @cached_property
    def processed_mail(self) -> services.ProcessedMailService:
        """Return the :class:`~pypaperless.services.ProcessedMailService`."""
        return services.ProcessedMailService(self._runtime)

    @cached_property
    def profile(self) -> services.ProfileService:
        """Return the :class:`~pypaperless.services.ProfileService`."""
        return services.ProfileService(self._runtime)

    @cached_property
    def saved_views(self) -> services.SavedViewService:
        """Return the :class:`~pypaperless.services.SavedViewService`."""
        return services.SavedViewService(self._runtime)

    @cached_property
    def search(self) -> services.SearchService:
        """Return the :class:`~pypaperless.services.SearchService`."""
        return services.SearchService(self._runtime)

    @cached_property
    def share_links(self) -> services.ShareLinkService:
        """Return the :class:`~pypaperless.services.ShareLinkService`."""
        return services.ShareLinkService(self._runtime)

    @cached_property
    def statistics(self) -> services.StatisticService:
        """Return the :class:`~pypaperless.services.StatisticService`."""
        return services.StatisticService(self._runtime)

    @cached_property
    def remote_version(self) -> services.RemoteVersionService:
        """Return the :class:`~pypaperless.services.RemoteVersionService`."""
        return services.RemoteVersionService(self._runtime)

    @cached_property
    def status(self) -> services.StatusService:
        """Return the :class:`~pypaperless.services.StatusService`."""
        return services.StatusService(self._runtime)

    @cached_property
    def storage_paths(self) -> services.StoragePathService:
        """Return the :class:`~pypaperless.services.StoragePathService`."""
        return services.StoragePathService(self._runtime)

    @cached_property
    def tags(self) -> services.TagService:
        """Return the :class:`~pypaperless.services.TagService`."""
        return services.TagService(self._runtime)

    @cached_property
    def tasks(self) -> services.TaskService:
        """Return the :class:`~pypaperless.services.TaskService`."""
        return services.TaskService(self._runtime)

    @cached_property
    def trash(self) -> services.TrashService:
        """Return the :class:`~pypaperless.services.TrashService`."""
        return services.TrashService(self._runtime)

    @cached_property
    def users(self) -> services.UserService:
        """Return the :class:`~pypaperless.services.UserService`."""
        return services.UserService(self._runtime)

    @cached_property
    def workflows(self) -> services.WorkflowService:
        """Return the :class:`~pypaperless.services.WorkflowService`."""
        return services.WorkflowService(self._runtime)
