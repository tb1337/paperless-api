"""Models for Paperless resources."""

from .consumption_templates import ConsumptionTemplate
from .correspondents import Correspondent, CorrespondentPost
from .custom_fields import CustomField, CustomFieldPost
from .document_types import DocumentType, DocumentTypePost
from .documents import (
    Document,
    DocumentMetadata,
    DocumentMetaInformation,
    DocumentNote,
    DocumentNotePost,
    DocumentPost,
)
from .groups import Group
from .mail_accounts import MailAccount
from .mail_rules import MailRule
from .saved_views import SavedView, SavedViewFilterRule
from .share_links import ShareLink, ShareLinkPost
from .storage_paths import StoragePath, StoragePathPost
from .tags import Tag, TagPost
from .tasks import Task
from .users import User

__all__ = [
    "ConsumptionTemplate",
    "Correspondent",
    "CorrespondentPost",
    "CustomField",
    "CustomFieldPost",
    "Document",
    "DocumentPost",
    "DocumentMetadata",
    "DocumentMetaInformation",
    "DocumentNote",
    "DocumentNotePost",
    "DocumentType",
    "DocumentTypePost",
    "Group",
    "MailAccount",
    "MailRule",
    "SavedView",
    "SavedViewFilterRule",
    "ShareLink",
    "ShareLinkPost",
    "StoragePath",
    "StoragePathPost",
    "Tag",
    "TagPost",
    "Task",
    "User",
]
