"""Provide `User` and 'Group' related models and helpers."""

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .mixins import helpers

if TYPE_CHECKING:
    from pypaperless import Paperless


class Group(PaperlessModel):
    """Represent a Paperless `Group`."""

    _api_path: ClassVar[str] = API_PATH["groups_single"]

    id: int
    name: str | None = None
    permissions: list[str] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `Group` instance."""
        super().__init__(api, data, **kwargs)

        object.__setattr__(self, "_api_path", self._api_path.format(pk=data.get("id")))


class User(PaperlessModel):
    """Represent a Paperless `User`."""

    _api_path: ClassVar[str] = API_PATH["users_single"]

    id: int
    username: str | None = None
    # exclude that from the dataclass
    # password: str | None = None  # noqa: ERA001
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    date_joined: datetime.datetime | None = None
    is_staff: bool | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    groups: list[int] | None = None
    user_permissions: list[str] | None = None
    inherited_permissions: list[str] | None = None
    is_mfa_enabled: bool | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any], **kwargs: Any) -> None:
        """Initialize a `User` instance."""
        super().__init__(api, data, **kwargs)

        object.__setattr__(self, "_api_path", self._api_path.format(pk=data.get("id")))


class GroupHelper(
    HelperBase,
    helpers.CallableMixin[Group],
    helpers.IterableMixin[Group],
):
    """Represent a factory for Paperless `Group` models."""

    _api_path = API_PATH["groups"]
    _resource = PaperlessResource.GROUPS

    _resource_cls = Group


class UserHelper(
    HelperBase,
    helpers.CallableMixin[User],
    helpers.IterableMixin[User],
):
    """Represent a factory for Paperless `User` models."""

    _api_path = API_PATH["users"]
    _resource = PaperlessResource.USERS

    _resource_cls = User
