"""Provide `Correspondent`, `DocumentType`, `StoragePath` and `Tag` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, final

from pypaperless.const import API_PATH

from .base import HelperBase, PaperlessModel
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@final
@dataclass(init=False)
class MailAccount(
    PaperlessModel,
    models.PermissionFieldsMixin,
):  # pylint: disable=too-many-instance-attributes
    """Represent a Paperless `MailAccount`."""

    _api_path = API_PATH["mail_accounts_single"]

    id: int | None = None
    name: str | None = None
    imap_server: str | None = None
    imap_port: int | None = None
    imap_security: int | None = None
    username: str | None = None
    # exclude that from the dataclass
    # password: str | None = None
    character_set: str | None = None
    is_token: bool | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]):
        """Initialize a `MailAccount` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@final
class MailAccountHelper(
    HelperBase[MailAccount],
    helpers.CallableMixin[MailAccount],
    helpers.IterableMixin[MailAccount],
):
    """Represent a factory for Paperless `MailAccount` models."""

    _api_path = API_PATH["mail_accounts"]

    _resource = MailAccount
