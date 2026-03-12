"""Provide `Group` and `User` services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.permissions import Group, User

from . import mixins
from .base import ServiceBase


class GroupService(
    ServiceBase,
    mixins.CallableMixin[Group],
    mixins.IterableMixin[Group],
):
    """Represent a factory for Paperless `Group` models."""

    _api_path = API_PATH["groups"]
    _resource = PaperlessResource.GROUPS

    _resource_cls = Group


class UserService(
    ServiceBase,
    mixins.CallableMixin[User],
    mixins.IterableMixin[User],
):
    """Represent a factory for Paperless `User` models."""

    _api_path = API_PATH["users"]
    _resource = PaperlessResource.USERS

    _resource_cls = User
