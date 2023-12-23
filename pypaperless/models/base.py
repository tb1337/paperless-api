"""Base models."""

from dataclasses import dataclass

from .shared import MatchingAlgorithm


class PaperlessModel:  # pylint: disable=too-few-public-methods
    """Base class that represents a Paperless model."""


class PaperlessPost(PaperlessModel):  # pylint: disable=too-few-public-methods
    """Base class that represents a Paperless POST model."""


@dataclass(kw_only=True)
class PaperlessModelMatchingMixin:
    """Mixin that adds matching attributes to a model."""

    match: str | None = None
    matching_algorithm: MatchingAlgorithm | None = None
    is_insensitive: bool | None = None

    def __post_init__(self) -> None:
        """Set default values when missing. Only on `POST`."""
        if not isinstance(self, PaperlessPost):
            return

        if not self.match:
            self.match = ""
        if not self.matching_algorithm:
            self.matching_algorithm = MatchingAlgorithm.NONE
        if not self.is_insensitive:
            self.is_insensitive = True
