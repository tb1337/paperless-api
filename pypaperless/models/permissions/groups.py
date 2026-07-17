"""Provide `Group` related models."""

from typing import ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models.base import IdentifiedModel


class Group(IdentifiedModel):
    """Represent a Paperless `Group`."""

    _api_path: ClassVar[str] = EndpointPath.GROUPS_SINGLE

    name: str | None = None
    permissions: list[str] | None = None
