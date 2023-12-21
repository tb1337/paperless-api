"""Model for mail rule resource."""

from dataclasses import dataclass

from .base import PaperlessModel


@dataclass(kw_only=True)
class MailRule(PaperlessModel):  # pylint: disable=too-many-instance-attributes
    """Represent a mail rule resource on the Paperless api."""

    id: int | None = None
    name: str | None = None
    account: int | None = None
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
    owner: int | None = None
    user_can_change: bool | None = None
