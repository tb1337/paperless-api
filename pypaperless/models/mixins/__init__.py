"""Mixins for PyPaperless models."""

from .creatable import CreatableMixin
from .data_fields import MatchingFieldsMixin
from .deletable import DeletableMixin
from .saveable import SaveableMixin
from .securable import SecurableDraftMixin, SecurableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CreatableMixin",
    "DeletableMixin",
    "MatchingFieldsMixin",
    "SaveableMixin",
    "SecurableDraftMixin",
    "SecurableMixin",
    "UpdatableMixin",
)
