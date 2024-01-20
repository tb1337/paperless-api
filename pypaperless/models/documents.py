"""Provide the `Documents` class."""

import datetime
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import PaperlessModel
from .mixins import UpdatableMixin

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
# @dataclass(init=False)
class Document(PaperlessModel, UpdatableMixin):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `Document`."""

    _api_path = API_PATH["documents_single"]

    # id: int
    # correspondent: int | None = None
    # document_type: int | None = None
    # storage_path: int | None = None
    # title: str | None = None
    # content: str | None = None
    # tags: list[int] | None = None
    # created: datetime.datetime | None = None
    # created_date: datetime.date | None = None
    # modified: datetime.datetime | None = None
    # added: datetime.datetime | None = None
    # archive_serial_number: int | None = None
    # original_file_name: str | None = None
    # archived_file_name: str | None = None
    # owner: int | None = None
    # user_can_change: bool | None = None
    # notes: list[dict[str, Any]] | None = None
    # custom_fields: list[dict[str, Any]] | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `Documents` instance."""
        super().__init__(api, data)

    @property
    def api_path(self) -> str:
        """Return the api path."""
        return self._api_path.format(pk=self.id)

    @property
    def id(self) -> int:
        """Represent data field."""
        return self._data["id"]

    @property
    def correspondent(self) -> int:
        """Represent data field."""
        return self._data["correspondent"]

    @property
    def document_type(self) -> int:
        """Represent data field."""
        return self._data["document_type"]

    @property
    def storage_path(self) -> int:
        """Represent data field."""
        return self._data["storage_path"]

    @property
    def title(self) -> str | None:
        """Represent data field."""
        # return self._data["title"]
        value: str | None = self._data.get("title", None)
        return value

    @title.setter
    def title(self, value: str) -> None:
        """Represent data field."""
        self._data.setdefault("title", value)

    @property
    def content(self) -> str:
        """Represent data field."""
        return self._data["content"]

    @property
    def tags(self) -> list[int]:
        """Represent data field."""
        return self._data["tags"]

    @property
    def created(self) -> datetime.datetime:
        """Represent data field."""
        return self._data["created"]

    @property
    def created_date(self) -> datetime.date:
        """Represent data field."""
        return self._data["created_date"]

    @property
    def modified(self) -> datetime.datetime:
        """Represent data field."""
        return self._data["modified"]

    @property
    def added(self) -> datetime.datetime:
        """Represent data field."""
        return self._data["added"]

    @property
    def archive_serial_number(self) -> int:
        """Represent data field."""
        return self._data["archive_serial_number"]

    @property
    def original_file_name(self) -> str:
        """Represent data field."""
        return self._data["original_file_name"]

    @property
    def archived_file_name(self) -> str:
        """Represent data field."""
        return self._data["archived_file_name"]

    @property
    def owner(self) -> int:
        """Represent data field."""
        return self._data["owner"]

    @property
    def user_can_change(self) -> bool:
        """Represent data field."""
        return self._data["user_can_change"]
