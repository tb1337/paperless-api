"""Mixins for PyPaperless models."""

from .creatable import CreatableMixin
from .deletable import DeletableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CreatableMixin",
    "DeletableMixin",
    "UpdatableMixin",
)
