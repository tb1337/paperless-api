"""Provide `MailRule` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH
from pypaperless.models import mixins
from pypaperless.models.base import PaperlessModel


class MailRule(PaperlessModel, mixins.SecurableMixin):
    """Represent a Paperless `MailRule`."""

    _api_path: ClassVar[str] = API_PATH["mail_rules_single"]

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
