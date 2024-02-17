"""Mixins for PyPaperless models."""

from .creatable import CreatableMixin
from .data_fields import MatchingFieldsMixin  # , PermissionFieldsMixin
from .deletable import DeletableMixin
from .securable import SecurableDraftMixin, SecurableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CreatableMixin",
    "DeletableMixin",
    "MatchingFieldsMixin",
    # "PermissionFieldsMixin",
    "UpdatableMixin",
    "SecurableMixin",
    "SecurableDraftMixin",
)
