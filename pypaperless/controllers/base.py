"""
Base controller for Paperless resources.

A controller is meant to handle requests to the Paperless api and their responses.
It is responsible for transforming data into its expected format, f.e. from json to dataclass.

The base controller implements basic get/iterate methods.
A derived controller can inherit from the base controller or specific features or both.
"""

import math
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from pypaperless.models.base import PaperlessPost
from pypaperless.util import dataclass_from_dict, dataclass_to_dict

if TYPE_CHECKING:
    from pypaperless import Paperless


ResourceT = TypeVar("ResourceT")


class ResultPage(NamedTuple, Generic[ResourceT]):
    """Represent a result page from an api call."""

    items: list[ResourceT]
    current_page: int
    next_page: int | None
    last_page: int


class BaseController(Generic[ResourceT]):
    """Represent the base controller."""

    _page_size: int = 50

    resource: ResourceT

    def __init__(self, paperless: "Paperless", path: str) -> None:
        """Initialize controller."""
        self._request_json = paperless.request_json
        self._request_file = paperless.request_file
        self._logger = paperless.logger.getChild(self.__class__.__name__)

        self.path = path.rstrip("/")

    async def get(
        self,
        page: int = 1,
        **kwargs: Any,
    ) -> ResultPage[ResourceT]:
        """Retrieve a specific page from resource api."""
        if page > 1:
            kwargs["page"] = page
        if "page_size" not in kwargs:
            kwargs["page_size"] = self._page_size

        res = await self._request_json("get", self.path, params=kwargs)
        return ResultPage(
            [dataclass_from_dict(self.resource, item) for item in res["results"]],
            kwargs["page"],
            kwargs["page"] + 1 if res["next"] else None,
            math.ceil(res["count"] / kwargs["page_size"]),
        )

    async def iterate(
        self,
        **kwargs: Any,
    ) -> AsyncGenerator[ResourceT, None]:
        """Iterate pages and yield every item."""
        next_page: int | None = 1
        while next_page:
            res = await self.get(next_page, **kwargs)
            next_page = res.next_page
            for item in res.items:
                yield item


class ControllerOneFeature(BaseController[ResourceT]):
    """Extend a controller with a default `one` method."""

    async def one(self, pk: int) -> ResourceT:
        """Return exactly one item by its pk."""
        url = f"{self.path}/{pk}"
        res = await self._request_json("get", url)
        data: ResourceT = dataclass_from_dict(self.resource, res)
        return data


class ControllerListFeature(BaseController[ResourceT]):
    """Extend a controller with a default `list` method."""

    async def list(self) -> list[int]:
        """Return a list of all item pks."""
        res = await self._request_json("get", self.path)
        if "all" in res:
            data: list[int] = res["all"]
            return data

        self._logger.debug("List result is empty.")
        return []


class ControllerCreateFeature(BaseController[ResourceT]):
    """Extend a controller with a default `create` method."""

    async def create(self, obj: PaperlessPost) -> ResourceT:
        """Create a new item on the Paperless api. Raise on failure."""
        res = await self._request_json(
            "post",
            self.path,
            json=dataclass_to_dict(obj),
        )
        data: ResourceT = dataclass_from_dict(self.resource, res)
        return data


class ControllerUpdateFeature(BaseController[ResourceT]):
    """Extend a controller with a default `update' method."""

    async def update(self, obj: ResourceT) -> ResourceT:
        """Update an existing item on the Paperless api. Raise on failure."""
        url = f"{self.path}/{obj.id}"
        res = await self._request_json(
            "put",
            url,
            json=dataclass_to_dict(obj, skip_none=False),
        )
        data: ResourceT = dataclass_from_dict(self.resource, res)
        return data


class ControllerDeleteFeature(BaseController[ResourceT]):
    """Extend a controller with a default `delete` method."""

    async def delete(self, obj: ResourceT) -> bool:
        """Delete an existing item from the Paperless api. Raise on failure."""
        url = f"{self.path}/{obj.id}"
        try:
            await self._request_json("delete", url)
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            raise exc


# class AController(BaseController[type[ModelA]]):
#     """Controller A."""

#     resource = ModelA


# class BController(
#     ControllerListFeature[type[ModelB]],
#     ControllerOneFeature[type[ModelB]],
# ):
#     "Controller B."
#     resource = ModelB


# class CController(ControllerListFeature[type[ModelC]]):
#     "Controller C."
#     resource = ModelC
