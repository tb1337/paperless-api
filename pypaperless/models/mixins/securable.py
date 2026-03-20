"""SecurableModel for PyPaperless models."""

from pydantic import BaseModel, Field, model_validator


class _PermissionScope(BaseModel):
    """Internal: user and group IDs for a single permission action."""

    users: list[int] = Field(default_factory=list)
    groups: list[int] = Field(default_factory=list)


class Permissions(BaseModel):
    """Object-level permissions (view + change) for a Paperless resource.

    Can be constructed with flat keyword arguments::

        Permissions(view_users=[2, 3], change_users=[2], change_groups=[1])

    Or directly from the nested API structure (used internally during
    JSON deserialization)::

        Permissions(
            view={"users": [2, 3], "groups": []},
            change={"users": [2], "groups": []}
        )

    Access is always via the nested attributes::

        perms.view.users    # list[int]
        perms.change.groups # list[int]
    """

    view: _PermissionScope = Field(default_factory=_PermissionScope)
    change: _PermissionScope = Field(default_factory=_PermissionScope)

    @model_validator(mode="before")
    @classmethod
    def _accept_flat(cls, data: object) -> object:
        """Accept flat kwargs (view_users, change_groups, …) alongside the nested form."""
        if not isinstance(data, dict):
            return data
        flat_keys = {"view_users", "view_groups", "change_users", "change_groups"}
        if flat_keys.isdisjoint(data):
            return data
        return {
            "view": {
                "users": data.get("view_users", []),
                "groups": data.get("view_groups", []),
            },
            "change": {
                "users": data.get("change_users", []),
                "groups": data.get("change_groups", []),
            },
        }


class SecurableModel(BaseModel):
    """Provide permission fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
    permissions: Permissions | None = None

    @property
    def has_permissions(self) -> bool:
        """Return if the model data includes the permission field."""
        return self.permissions is not None


class SecurableDraftModel(BaseModel):
    """Provide permission fields for PyPaperless draft models."""

    owner: int | None = None
    set_permissions: Permissions | None = None
