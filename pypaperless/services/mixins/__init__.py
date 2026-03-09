"""Mixins for PyPaperless services."""

from .callable import CallableMixin
from .deletable import DeletableMixin
from .draftable import DraftableMixin
from .iterable import IterableMixin
from .securable import SecurableMixin
from .updatable import UpdatableMixin

__all__ = (
    "CallableMixin",
    "DeletableMixin",
    "DraftableMixin",
    "IterableMixin",
    "SecurableMixin",
    "UpdatableMixin",
)
