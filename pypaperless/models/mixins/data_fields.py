"""MatchingFieldsMixin for PyPaperless models."""

from enum import Enum
from typing import Self

from pydantic import BaseModel


class MatchingAlgorithm(Enum):
    """Text-matching algorithm used by `Correspondent`, `DocumentType`, `StoragePath`, and `Tag`."""

    NONE = 0
    ANY = 1
    ALL = 2
    LITERAL = 3
    REGEX = 4
    FUZZY = 5
    AUTO = 6
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MatchingFieldsMixin(BaseModel):
    """Provide shared matching fields for PyPaperless models."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithm | None = None
    is_insensitive: bool | None = None
