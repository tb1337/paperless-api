"""Mixins for PyPaperless services."""

from .callable import CallableMixin
from .draftable import DraftableMixin
from .iterable import IterableMixin
from .securable import SecurableMixin

__all__ = (
    "CallableMixin",
    "DraftableMixin",
    "IterableMixin",
    "SecurableMixin",
)
