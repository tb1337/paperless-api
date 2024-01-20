"""Provide the `Documents` class."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import PaperlessModel
from .mixins import UpdatableMixin

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class Document(PaperlessModel, UpdatableMixin):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `Document`."""

    _api_path = API_PATH["documents_single"]
    _rw_props = ""

    id: int
    correspondent: int | None = None
    document_type: int | None = None
    storage_path: int | None = None
    title: str | None = None
    content: str | None = None
    tags: list[int] | None = None
    created: datetime.datetime | None = None
    created_date: datetime.date | None = None
    modified: datetime.datetime | None = None
    added: datetime.datetime | None = None
    archive_serial_number: int | None = None
    original_file_name: str | None = None
    archived_file_name: str | None = None
    owner: int | None = None
    user_can_change: bool | None = None
    notes: list[dict[str, Any]] | None = None
    custom_fields: list[dict[str, Any]] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Documents` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))
