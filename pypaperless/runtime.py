"""Provide the PaperlessRuntime class."""

from typing import Any

from .cache import PaperlessCache
from .transport import PaperlessTransport


class PaperlessRuntime:
    """Container that binds a transport and a cache for use by services.

    Constructed by :class:`~pypaperless.client.PaperlessClient` and passed to
    every service instance.  Services access HTTP via ``self._client.transport``
    and the in-memory cache via ``self._client.cache``.

    Unknown attribute lookups are transparently delegated to the
    :class:`~pypaperless.client.PaperlessClient` facade, which allows model
    convenience methods (e.g. ``document.delete()``) to dispatch through the
    service registry without an explicit back-reference.

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
        self.facade: Any = None

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes to the client facade for service dispatch."""
        if name.startswith("_"):
            raise AttributeError(name)
        facade = object.__getattribute__(self, "facade")
        if facade is None:
            raise AttributeError(name)
        return getattr(facade, name)
