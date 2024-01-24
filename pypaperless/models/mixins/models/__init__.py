"""Mixins for PyPaperless models."""

from .creatable import CreatableMixin
from .data_fields import PermissionFieldsMixin
from .deletable import DeletableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CreatableMixin",
    "DeletableMixin",
    "PermissionFieldsMixin",
    "UpdatableMixin",
)
