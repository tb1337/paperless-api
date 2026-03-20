"""Mixins for PyPaperless services."""

from .callable import CallableService
from .creatable import CreatableService
from .deletable import DeletableService
from .iterable import IterableService
from .securable import SecurableService
from .updatable import UpdatableService

__all__ = (
    "CallableService",
    "CreatableService",
    "DeletableService",
    "IterableService",
    "SecurableService",
    "UpdatableService",
)
