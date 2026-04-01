"""Provide `MailAccount` related models."""

import datetime
from typing import ClassVar

from pypaperless.const import EndpointPath
from pypaperless.models import mixins
from pypaperless.models.base import PaperlessModel


class MailAccount(PaperlessModel, mixins.SecurableModel):
    """Represent a Paperless `MailAccount`."""

    _api_path: ClassVar[str] = EndpointPath.MAIL_ACCOUNTS_SINGLE

    id: int | None = None
    name: str | None = None
    imap_server: str | None = None
    imap_port: int | None = None
    imap_security: int | None = None
    username: str | None = None
    # password:intentionally excluded
    character_set: str | None = None
    is_token: bool | None = None
    account_type: int | None = None
    expiration: datetime.datetime | None = None
