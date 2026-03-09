"""MatchingFieldsMixin for PyPaperless models."""

from pydantic import BaseModel

from pypaperless.models.common import MatchingAlgorithmType


class MatchingFieldsMixin(BaseModel):
    """Provide shared matching fields for PyPaperless models."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithmType | None = None
    is_insensitive: bool | None = None
