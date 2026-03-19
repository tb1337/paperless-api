"""Provide `Search` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH
from pypaperless.models.correspondents import Correspondent
from pypaperless.models.custom_fields import CustomField
from pypaperless.models.document_types import DocumentType
from pypaperless.models.documents import Document
from pypaperless.models.mails import MailAccount, MailRule
from pypaperless.models.permissions import Group, User
from pypaperless.models.saved_views import SavedView
from pypaperless.models.storage_paths import StoragePath
from pypaperless.models.tags import Tag
from pypaperless.models.workflows import Workflow

from .base import PaperlessModel


class SearchResult(PaperlessModel):
    """Represent a Paperless global search result."""

    _api_path: ClassVar[str] = API_PATH["search"]

    total: int | None = None
    documents: list[Document] | None = None
    saved_views: list[SavedView] | None = None
    tags: list[Tag] | None = None
    correspondents: list[Correspondent] | None = None
    document_types: list[DocumentType] | None = None
    storage_paths: list[StoragePath] | None = None
    users: list[User] | None = None
    groups: list[Group] | None = None
    mail_rules: list[MailRule] | None = None
    mail_accounts: list[MailAccount] | None = None
    workflows: list[Workflow] | None = None
    custom_fields: list[CustomField] | None = None
