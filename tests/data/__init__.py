"""Raw data constants."""

import json
from pathlib import Path

from .config import DATA_CONFIG
from .correspondents import DATA_CORRESPONDENTS
from .custom_fields import DATA_CUSTOM_FIELDS
from .document_metadata import DATA_DOCUMENT_METADATA
from .document_notes import DATA_DOCUMENT_NOTES
from .document_suggestions import DATA_DOCUMENT_SUGGESTIONS
from .document_types import DATA_DOCUMENT_TYPES
from .documents import DATA_DOCUMENTS
from .documents_search import DATA_DOCUMENTS_SEARCH
from .groups import DATA_GROUPS
from .mail import DATA_MAIL_ACCOUNTS, DATA_MAIL_RULES, DATA_PROCESSED_MAIL
from .object_permissions import DATA_OBJECT_PERMISSIONS
from .paths import DATA_PATHS
from .remote_version import DATA_REMOTE_VERSION
from .saved_views import DATA_SAVED_VIEWS
from .share_links import DATA_SHARE_LINKS
from .statistics import DATA_STATISTICS
from .status import DATA_STATUS
from .storage_paths import DATA_STORAGE_PATHS
from .tags import DATA_TAGS
from .tasks import DATA_TASKS
from .token import DATA_TOKEN
from .users import DATA_USERS
from .workflow import DATA_WORKFLOW_ACTIONS, DATA_WORKFLOW_TRIGGERS, DATA_WORKFLOWS

# mypy: ignore-errors


def _read_schema() -> dict:
    filepath = Path("tests/data/schema.json")
    with Path.open(filepath, mode="r", encoding="utf-8") as file:
        return json.load(file)


DATA_SCHEMA = _read_schema()


__all__ = (
    "DATA_CONFIG",
    "DATA_CORRESPONDENTS",
    "DATA_CUSTOM_FIELDS",
    "DATA_DOCUMENTS",
    "DATA_DOCUMENTS_SEARCH",
    "DATA_DOCUMENT_METADATA",
    "DATA_DOCUMENT_NOTES",
    "DATA_DOCUMENT_SUGGESTIONS",
    "DATA_DOCUMENT_TYPES",
    "DATA_GROUPS",
    "DATA_MAIL_ACCOUNTS",
    "DATA_MAIL_RULES",
    "DATA_OBJECT_PERMISSIONS",
    "DATA_PATHS",
    "DATA_PROCESSED_MAIL",
    "DATA_REMOTE_VERSION",
    "DATA_SAVED_VIEWS",
    "DATA_SCHEMA",
    "DATA_SHARE_LINKS",
    "DATA_STATISTICS",
    "DATA_STATUS",
    "DATA_STORAGE_PATHS",
    "DATA_TAGS",
    "DATA_TASKS",
    "DATA_TOKEN",
    "DATA_USERS",
    "DATA_WORKFLOWS",
    "DATA_WORKFLOW_ACTIONS",
    "DATA_WORKFLOW_TRIGGERS",
)
