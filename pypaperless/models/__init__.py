"""PyPaperless models."""

from .classifiers import (
    Correspondent,
    CorrespondentDraft,
    DocumentType,
    DocumentTypeDraft,
    StoragePath,
    StoragePathDraft,
    Tag,
    TagDraft,
)
from .custom_fields import CustomField, CustomFieldDraft
from .documents import Document, DocumentDraft, DocumentMeta, DocumentNote, DocumentNoteDraft
from .mails import MailAccount, MailRule
from .pages import Page
from .permissions import Group, User
from .saved_views import SavedView
from .share_links import ShareLink, ShareLinkDraft

__all__ = (
    "Correspondent",
    "CorrespondentDraft",
    "CustomField",
    "CustomFieldDraft",
    "Document",
    "DocumentDraft",
    "DocumentMeta",
    "DocumentNote",
    "DocumentNoteDraft",
    "DocumentType",
    "DocumentTypeDraft",
    "Group",
    "MailAccount",
    "MailRule",
    "Page",
    "SavedView",
    "ShareLink",
    "ShareLinkDraft",
    "StoragePath",
    "StoragePathDraft",
    "Tag",
    "TagDraft",
    "User",
)
