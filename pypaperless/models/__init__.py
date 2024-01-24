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
from .saved_views import SavedView, SavedViewFilterRuleType
from .share_links import ShareLink, ShareLinkDraft, ShareLinkFileVersionType

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
    "SavedView",
    "SavedViewFilterRuleType",
    "ShareLink",
    "ShareLinkDraft",
    "ShareLinkFileVersionType",
    "User",
)
