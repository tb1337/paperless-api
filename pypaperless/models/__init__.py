"""Models for Paperless resources."""

from .custom_fields import CustomField, CustomFieldPost
from .documents import (
    Document,
    DocumentMetadata,
    DocumentMetaInformation,
    DocumentNote,
    DocumentNotePost,
    DocumentPost,
)
from .groups import Group
from .mails import MailAccount, MailRule
from .matching import (
    Correspondent,
    CorrespondentPost,
    DocumentType,
    DocumentTypePost,
    StoragePath,
    StoragePathPost,
    Tag,
    TagPost,
)
from .saved_views import SavedView, SavedViewFilterRule
from .share_links import ShareLink, ShareLinkPost
from .tasks import Task
from .users import User
from .workflows import ConsumptionTemplate, Workflow, WorkflowAction, WorkflowTrigger

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
    "Workflow",
    "WorkflowAction",
    "WorkflowTrigger",
]
