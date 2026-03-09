"""SecurableMixin for PyPaperless models."""

from pydantic import BaseModel

from pypaperless.models.common import PermissionTableType


class SecurableMixin(BaseModel):
    """Provide permission fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
    permissions: PermissionTableType | None = None

    @property
    def has_permissions(self) -> bool:
        """Return if the model data includes the permission field."""
        return self.permissions is not None


class SecurableDraftMixin(BaseModel):
    """Provide permission fields for PyPaperless draft models."""

    owner: int | None = None
    set_permissions: PermissionTableType | None = None
