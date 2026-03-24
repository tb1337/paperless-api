"""Provide the PaperlessRuntime class."""

from .cache import PaperlessCache
from .const import API_VERSION
from .transport import PaperlessTransport


class PaperlessRuntime:
    """Container that binds a transport and a cache for use by services.

    Constructed by :class:`~pypaperless.client.PaperlessClient` and passed to
    every service instance.  Services access HTTP via ``self._runtime.transport``
    and the in-memory cache via ``self._runtime.cache``.

    Args:
        transport: The :class:`~pypaperless.transport.PaperlessTransport` instance.
        cache:     The :class:`~pypaperless.cache.PaperlessCache` instance.

    Example::

        runtime = PaperlessRuntime(transport, cache)
        await runtime.transport.get("/api/documents/")

    """

    def __init__(self, transport: PaperlessTransport, cache: PaperlessCache) -> None:
        """Initialize a :class:`PaperlessRuntime` instance."""
        self.transport = transport
        self.cache = cache
        self.api_version: int = API_VERSION
