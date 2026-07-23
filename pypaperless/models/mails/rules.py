"""Provide `MailRule` related models."""

from enum import IntEnum
from typing import ClassVar, Self

from pypaperless.const import EndpointPath
from pypaperless.models import mixins
from pypaperless.models.base import IdentifiedModel


class MailRuleAction(IntEnum):
    """Represent a subtype of `MailRule`."""

    DELETE = 1
    MOVE = 2
    MARK_READ = 3
    FLAG = 4
    TAG = 5
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRuleTitleSource(IntEnum):
    """Represent a subtype of `MailRule`."""

    FROM_SUBJECT = 1
    FROM_FILENAME = 2
    NONE = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRuleCorrespondentSource(IntEnum):
    """Represent a subtype of `MailRule`."""

    FROM_NOTHING = 1
    FROM_EMAIL = 2
    FROM_NAME = 3
    FROM_CUSTOM = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRuleAttachmentType(IntEnum):
    """Represent a subtype of `MailRule`."""

    ATTACHMENTS_ONLY = 1
    EVERYTHING = 2
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRuleConsumptionScope(IntEnum):
    """Represent a subtype of `MailRule`."""

    ATTACHMENTS_ONLY = 1
    EML_ONLY = 2
    EVERYTHING = 3
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRulePdfLayout(IntEnum):
    """Represent a subtype of `MailRule`."""

    DEFAULT = 0
    TEXT_HTML = 1
    HTML_TEXT = 2
    HTML_ONLY = 3
    TEXT_ONLY = 4
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class MailRule(IdentifiedModel, mixins.SecurableModel):
    """Represent a Paperless `MailRule`."""

    _api_path: ClassVar[str] = EndpointPath.MAIL_RULES_SINGLE

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
    action: MailRuleAction | None = None
    action_parameter: str | None = None
    assign_title_from: MailRuleTitleSource | None = None
    assign_tags: list[int] | None = None
    assign_correspondent_from: MailRuleCorrespondentSource | None = None
    assign_correspondent: int | None = None
    assign_document_type: int | None = None
    assign_owner_from_rule: bool | None = None
    order: int | None = None
    attachment_type: MailRuleAttachmentType | None = None
    consumption_scope: MailRuleConsumptionScope | None = None
    pdf_layout: MailRulePdfLayout | None = None
    stop_processing: bool | None = None
