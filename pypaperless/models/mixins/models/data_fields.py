"""PermissionFieldsMixin for PyPaperless models."""

from dataclasses import dataclass

from pypaperless.models.common import MatchingAlgorithmType


@dataclass
class MatchingFieldsMixin:
    """Provide shared matching fields for PyPaperless models."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithmType | None = None
    is_insensitive: bool | None = None


@dataclass
class PermissionFieldsMixin:
    """Provide shared owner fields for PyPaperless models."""

    owner: int | None = None
    user_can_change: bool | None = None
