"""Provide the shared base for document-scoped sub-services."""

from typing import TYPE_CHECKING, cast

from pypaperless.exceptions import PrimaryKeyRequiredError
from pypaperless.services.base import ResourceService

if TYPE_CHECKING:
    from pypaperless.runtime import PaperlessRuntime


class DocumentScopedServiceBase(ResourceService):
    """Base class for sub-services scoped to a specific document.

    Manages the optional `attached_to` document pk and provides
    `_get_document_pk` to resolve the effective pk at call time.
    """

    def __init__(self, runtime: "PaperlessRuntime", attached_to: int | None = None) -> None:
        """Initialize with an optional attached document pk."""
        super().__init__(runtime)

        self._attached_to = attached_to

    def _get_document_pk(self, pk: int | None = None) -> int:
        """Return the attached document pk, or the parameter."""
        if not any((self._attached_to, pk)):
            message = f"Accessing {type(self).__name__} data without a primary key."
            raise PrimaryKeyRequiredError(message)
        return cast("int", self._attached_to or pk)
