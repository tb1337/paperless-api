"""Model for user resource."""

from dataclasses import dataclass
from datetime import datetime

from .base import PaperlessModel


@dataclass(kw_only=True)
class User(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a user resource on the Paperless api."""

    id: int | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    date_joined: datetime | None = None
    is_staff: bool | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    groups: list[int] | None = None
    user_permissions: list[str] | None = None
    inherited_permissions: list[str] | None = None
