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
from .config import Config
from .custom_fields import CustomField, CustomFieldDraft
from .documents import (
    Document,
    DocumentDraft,
    DocumentMeta,
    DocumentNote,
    DocumentNoteDraft,
)
from .mails import MailAccount, MailRule
from .pages import Page
from .permissions import Group, User
from .remote_version import RemoteVersion
from .saved_views import SavedView
from .share_links import ShareLink, ShareLinkDraft
from .statistics import Statistic
from .status import Status
from .tasks import Task
from .workflows import Workflow, WorkflowAction, WorkflowTrigger

__all__ = (
    "Config",
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
    "RemoteVersion",
    "SavedView",
    "ShareLink",
    "ShareLinkDraft",
    "Statistic",
    "Status",
    "StoragePath",
    "StoragePathDraft",
    "Tag",
    "TagDraft",
    "Task",
    "User",
    "Workflow",
    "WorkflowAction",
    "WorkflowTrigger",
)
