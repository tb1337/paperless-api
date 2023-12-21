"""Model for mail account resource."""

from dataclasses import dataclass

from .base import PaperlessModel


@dataclass(kw_only=True)
class MailAccount(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a mail account resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    imap_server: str | None = None
    imap_port: int | None = None
    imap_security: int | None = None
    username: str | None = None
    password: str | None = None
    character_set: str | None = None
    is_token: bool | None = None
    owner: int | None = None
    user_can_change: bool | None = None
