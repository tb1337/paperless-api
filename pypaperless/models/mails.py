"""Provide `MailRule` related models and helpers."""

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .mixins import helpers, models

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class MailAccount(
    PaperlessModel,
    models.SecurableMixin,
):
    """Represent a Paperless `MailAccount`."""

    _api_path = API_PATH["mail_accounts_single"]

    id: int | None = None
    name: str | None = None
    imap_server: str | None = None
    imap_port: int | None = None
    imap_security: int | None = None
    username: str | None = None
    # exclude that from the dataclass
    # password: str | None = None  # noqa: ERA001
    character_set: str | None = None
    is_token: bool | None = None
    account_type: int | None = None
    expiration: datetime.datetime | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `MailAccount` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


@dataclass(init=False)
class MailRule(
    PaperlessModel,
    models.SecurableMixin,
):
    """Represent a Paperless `MailRule`."""

    _api_path = API_PATH["mail_rules_single"]

    id: int | None = None
    name: str | None = None
    account: int | None = None
    enabled: bool | None = None
    folder: str | None = None
    filter_from: str | None = None
    filter_to: str | None = None
    filter_subject: str | None = None
    filter_body: str | None = None
    filter_attachment_filename_include: str | None = None
    filter_attachment_filename_exclude: str | None = None
    maximum_age: int | None = None
    action: int | None = None
    action_parameter: str | None = None
    assign_title_from: int | None = None
    assign_tags: list[int] | None = None
    assign_correspondent_from: int | None = None
    assign_correspondent: int | None = None
    assign_document_type: int | None = None
    assign_owner_from_rule: bool | None = None
    order: int | None = None
    attachment_type: int | None = None
    consumption_scope: int | None = None
    pdf_layout: int | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `MailRule` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


class MailAccountHelper(
    HelperBase[MailAccount],
    helpers.CallableMixin[MailAccount],
    helpers.IterableMixin[MailAccount],
    helpers.SecurableMixin,
):
    """Represent a factory for Paperless `MailAccount` models."""

    _api_path = API_PATH["mail_accounts"]
    _resource = PaperlessResource.MAIL_ACCOUNTS

    _resource_cls = MailAccount


class MailRuleHelper(
    HelperBase[MailRule],
    helpers.CallableMixin[MailRule],
    helpers.IterableMixin[MailRule],
    helpers.SecurableMixin,
):
    """Represent a factory for Paperless `MailRule` models."""

    _api_path = API_PATH["mail_rules"]
    _resource = PaperlessResource.MAIL_RULES

    _resource_cls = MailRule
