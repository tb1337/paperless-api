"""Provide `DocumentNote` related models."""

import datetime
from typing import ClassVar, cast

from pypaperless.const import API_PATH
from pypaperless.models import mixins
from pypaperless.models.base import PaperlessModel


class DocumentNote(PaperlessModel):
    """Represent a Paperless `DocumentNote`."""

    _api_path: ClassVar[str] = API_PATH["documents_notes"]
    _pk_field: ClassVar[str] = "document"

    id: int | None = None
    note: str | None = None
    created: datetime.datetime | None = None
    document: int | None = None
    user: int | None = None

    async def delete(self) -> bool:
        """Shortcut for ``paperless.documents.notes.delete(self)``."""
        return cast("bool", await self._client.documents.notes.delete(self))


class DocumentNoteDraft(PaperlessModel, mixins.CreatableModel):
    """Represent a new Paperless `DocumentNote`, which is not stored in Paperless."""

    _api_path: ClassVar[str] = API_PATH["documents_notes"]
    _pk_field: ClassVar[str] = "document"

    _create_required_fields: ClassVar[set[str]] = {"note", "document"}

    note: str | None = None
    document: int | None = None

    async def save(self) -> tuple[int, int]:
        """Shortcut for ``paperless.documents.notes.save(self)``."""
        return cast("tuple[int, int]", await self._client.documents.notes.save(self))
