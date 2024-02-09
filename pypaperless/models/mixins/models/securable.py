"""SecurableMixin for PyPaperless models."""

from dataclasses import dataclass

from pypaperless.models.common import PermissionTableType


@dataclass(kw_only=True)
class SecurableMixin:
    """Provide permission fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
    permissions: PermissionTableType | None = None

    @property
    def has_permissions(self) -> bool:
        """Return if the model data includes the permission field."""
        return self.permissions is not None


@dataclass(kw_only=True)
class SecurableDraftMixin:
    """Provide permission fields for PyPaperless draft models."""

    owner: int | None = None
    set_permissions: PermissionTableType | None = None
