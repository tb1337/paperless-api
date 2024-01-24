"""PyPaperless models."""

from .custom_fields import CustomField, CustomFieldDraft, CustomFieldType, CustomFieldValueType
from .documents import (
    Document,
    DocumentDraft,
    DocumentMeta,
    DocumentMetadataType,
    DocumentNote,
    DocumentNoteDraft,
)
from .mails import MailAccount, MailRule
from .pages import Page
from .permissions import Group, User

__all__ = (
    "CustomField",
    "CustomFieldDraft",
    "CustomFieldType",
    "CustomFieldValueType",
    "Document",
    "DocumentDraft",
    "DocumentMeta",
    "DocumentMetadataType",
    "DocumentNote",
    "DocumentNoteDraft",
    "Group",
    "MailAccount",
    "MailRule",
    "Page",
    "User",
)
