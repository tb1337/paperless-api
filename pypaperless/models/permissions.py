"""Provide `User` and 'Group' related models."""

import datetime
from typing import ClassVar

from pypaperless.const import API_PATH

from .base import PaperlessModel


class Group(PaperlessModel):
    """Represent a Paperless `Group`."""

    _api_path: ClassVar[str] = API_PATH["groups_single"]

    id: int
    name: str | None = None
    permissions: list[str] | None = None


class User(PaperlessModel):
    """Represent a Paperless `User`."""

    _api_path: ClassVar[str] = API_PATH["users_single"]

    id: int
    username: str | None = None
    # password: intentionally excluded
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
