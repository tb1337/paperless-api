"""SecurableMixin for PyPaperless models."""

from pydantic import BaseModel, Field


class PermissionSet(BaseModel):
    """Represent a Paperless permission set."""

    users: list[int] = Field(default_factory=list)
    groups: list[int] = Field(default_factory=list)


class PermissionTable(BaseModel):
    """Represent a Paperless permissions type."""

    view: PermissionSet = Field(default_factory=PermissionSet)
    change: PermissionSet = Field(default_factory=PermissionSet)


class SecurableMixin(BaseModel):
    """Provide permission fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
    permissions: PermissionTable | None = None

    @property
    def has_permissions(self) -> bool:
        """Return if the model data includes the permission field."""
        return self.permissions is not None


class SecurableDraftMixin(BaseModel):
    """Provide permission fields for PyPaperless draft models."""

    owner: int | None = None
    set_permissions: PermissionTable | None = None
