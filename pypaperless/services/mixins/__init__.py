"""Mixins for PyPaperless services."""

from .callable import CallableMixin
from .creatable import CreatableMixin
from .deletable import DeletableMixin
from .iterable import IterableMixin
from .securable import SecurableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CallableMixin",
    "CreatableMixin",
    "DeletableMixin",
    "IterableMixin",
    "SecurableMixin",
    "UpdatableMixin",
)
