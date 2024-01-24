"""PermissionFieldsMixin for PyPaperless models."""

from dataclasses import dataclass


@dataclass
class PermissionFieldsMixin:
    """Provide shared owner fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
