"""Base endpoints for Paperless resources."""

import math
from collections.abc import Generator
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from pypaperless.models.base import PaperlessPost
from pypaperless.models.shared import ResourceType
from pypaperless.util import dataclass_from_dict, dataclass_to_dict

if TYPE_CHECKING:
    from pypaperless import Paperless

RT = TypeVar("RT")


class PaginatedResult(NamedTuple, Generic[RT]):
    """Store a paginated result from any endpoint."""

    current_page: int
    next_page: int | None
    last_page: int
    items: list[RT]


class BaseEndpoint(Generic[RT]):
    """Represent a read-only Paperless endpoint."""

    endpoint_type: ResourceType | None = None
    endpoint_cls: RT | None = None

    request_page_size: int = 50

    def __init__(self, paperless: "Paperless", endpoint: str) -> None:
        """Initialize endpoint."""
        self._paperless = paperless
        self._endpoint = endpoint
        self._logger = paperless.logger.getChild(self.endpoint_type)

    @property
    def endpoint(self):
        """Return the endpoint url."""
        return self._endpoint.rstrip("/")

    async def list(self) -> list[int]:
        """Return a list of all entity ids, if applicable."""
        res = await self._paperless.request_json("get", self.endpoint)
        if "all" in res:
            return res["all"]

        self._logger.debug("List result is empty.")
        return []

    async def get(
        self,
        **kwargs: dict[str, Any],
    ) -> PaginatedResult[RT]:
        """
        Request api pages as list.

        Set a `page` parameter to request any desired page in results.
        If `page` is omitted, page 1 will be requested.

        Example:
            paperless.endpoint.get(): Results in requesting page 1
            paperless.endpoint.get(`page`=2): Page 2 will be requested
        """
        if "page" not in kwargs:
            kwargs["page"] = 1
        if "page_size" not in kwargs:
            kwargs["page_size"] = self.request_page_size

        res = await self._paperless.request_json("get", self.endpoint, params=kwargs)
        return PaginatedResult(
            kwargs["page"],
            kwargs["page"] + 1 if res["next"] else None,
            math.ceil(res["count"] / kwargs["page_size"]),
            [dataclass_from_dict(self.endpoint_cls, item) for item in res["results"]],
        )

    async def iterate(self, **kwargs: dict[str, Any]) -> Generator[RT, None, None]:
        """Iterate pages and yield every entity."""
        page = 1
        while page:
            kwargs["page"] = page
            res = await self.get(**kwargs)
            page = res.next_page
            for item in res.items:
                yield item

    async def one(self, idx: int) -> RT:
        """Request exactly one entity by id."""
        url = f"{self.endpoint}/{idx}"
        res = await self._paperless.request_json("get", url)
        return dataclass_from_dict(self.endpoint_cls, res)


class BaseEndpointCrudMixin:
    """Mixin that adds CRUD features to endpoints."""

    async def create(self: BaseEndpoint, obj: PaperlessPost) -> RT:
        """Create a new entity. Raise on failure."""
        res = await self._paperless.request_json(
            "post",
            self.endpoint,
            json=dataclass_to_dict(obj),
        )
        return dataclass_from_dict(self.endpoint_cls, res)

    async def update(self: BaseEndpoint, obj: RT) -> RT:
        """Update an existing entity. Raise on failure."""
        url = f"{self.endpoint}/{obj.id}"
        res = await self._paperless.request_json(
            "put", url, json=dataclass_to_dict(obj, skip_none=False)
        )
        return dataclass_from_dict(self.endpoint_cls, res)

    async def delete(self: BaseEndpoint, obj: RT) -> bool:
        """Delete an existing entity. Raise on failure."""
        url = f"{self.endpoint}/{obj.id}"
        await self._paperless.request_json("delete", url)
        return True


class BaseService:  # pylint: disable=too-few-public-methods
    """Handle requests for sub-endpoints or special tasks."""

    def __init__(self, ep: BaseEndpoint) -> None:
        """Initialize document notes service."""
        self._paperless = ep._paperless
        self._logger = ep._logger
        self.endpoint = ep.endpoint
