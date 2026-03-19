"""PyPaperless models."""

from .config import Config
from .correspondents import Correspondent, CorrespondentDraft
from .custom_fields import CustomField, CustomFieldDraft
from .document_types import DocumentType, DocumentTypeDraft
from .documents import (
    Document,
    DocumentCustomFieldList,
    DocumentDraft,
    DocumentHistory,
    DocumentHistoryAction,
    DocumentMeta,
    DocumentNote,
    DocumentNoteDraft,
    DocumentSuggestions,
    DownloadedDocument,
)
from .mails import MailAccount, MailRule, ProcessedMail
from .pages import Page
from .permissions import Group, User
from .profile import Profile, ProfileSocialAccount
from .remote_version import RemoteVersion
from .saved_views import SavedView
from .search import SearchResult
from .share_links import ShareLink, ShareLinkDraft
from .statistics import Statistic
from .status import Status
from .storage_paths import StoragePath, StoragePathDraft
from .tags import Tag, TagDraft
from .tasks import Task
from .workflows import Workflow, WorkflowAction, WorkflowTrigger

__all__ = (
    "Config",
    "Correspondent",
    "CorrespondentDraft",
    "CustomField",
    "CustomFieldDraft",
    "Document",
    "DocumentCustomFieldList",
    "DocumentDraft",
    "DocumentHistory",
    "DocumentHistoryAction",
    "DocumentMeta",
    "DocumentNote",
    "DocumentNoteDraft",
    "DocumentSuggestions",
    "DocumentType",
    "DocumentTypeDraft",
    "DownloadedDocument",
    "Group",
    "MailAccount",
    "MailRule",
    "Page",
    "ProcessedMail",
    "Profile",
    "ProfileSocialAccount",
    "RemoteVersion",
    "SavedView",
    "SearchResult",
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
