"""Mixins for PyPaperless models."""

from .creatable import CreatableModel
from .data_fields import MatchingFieldsModel
from .deletable import DeletableModel
from .saveable import SaveableModel
from .securable import SecurableDraftModel, SecurableModel
from .updatable import UpdatableModel

__all__ = (
    "CreatableModel",
    "DeletableModel",
    "MatchingFieldsModel",
    "SaveableModel",
    "SecurableDraftModel",
    "SecurableModel",
    "UpdatableModel",
)
