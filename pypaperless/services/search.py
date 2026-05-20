"""Provide `Search` service."""

from pypaperless.builders import SearchQuery
from pypaperless.const import EndpointPath
from pypaperless.models.search import SearchResult

from .base import ResourceService


class SearchService(ResourceService):
    """Represent a factory for Paperless global search results."""

    _api_path = EndpointPath.SEARCH

    _resource_cls = SearchResult

    async def __call__(
        self,
        query: str | SearchQuery,
        *,
        db_only: bool | None = None,
    ) -> SearchResult:
        """Perform a global search and return a ``SearchResult``.

        Args:
            query:   The search query — a plain Whoosh string or a
                     :class:`~pypaperless.builders.search.SearchQuery` builder object.
            db_only: When ``True``, only the database is searched (no
                     full-text index).  Defaults to ``None`` (server decides).

        Example::

            # Plain string
            result = await paperless.search("invoice")

            # Builder
            from pypaperless.models.types import SearchQuery
            q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
            result = await paperless.search(q)

        """
        params: dict[str, str | bool] = {"query": str(query)}
        if db_only is not None:
            params["db_only"] = db_only
        res = await self._runtime.transport.get(self._api_path, params=params)
        return self._resource_cls.from_data(self._runtime, res)
