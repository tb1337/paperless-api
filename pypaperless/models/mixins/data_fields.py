"""MatchingFieldsMixin for PyPaperless models."""

from enum import Enum

from pydantic import BaseModel


class EnumWithMissingFallback(Enum):
    """Mixin for Enum classes that fall back to UNKNOWN for unrecognised values."""

    @classmethod
    def _missing_(cls, *_: object) -> "EnumWithMissingFallback":
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MatchingAlgorithm(EnumWithMissingFallback):
    """Represent a subtype of `Correspondent`, `DocumentType`, `StoragePath` and `Tag`."""

    NONE = 0
    ANY = 1
    ALL = 2
    LITERAL = 3
    REGEX = 4
    FUZZY = 5
    AUTO = 6
    UNKNOWN = -1


class MatchingFieldsMixin(BaseModel):
    """Provide shared matching fields for PyPaperless models."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithm | None = None
    is_insensitive: bool | None = None
