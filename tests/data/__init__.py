"""Raw data constants."""

import json
from pathlib import Path

from .v0_0_0 import (
    V0_0_0_CORRESPONDENTS,
    V0_0_0_DOCUMENT_SUGGESTIONS,
    V0_0_0_DOCUMENT_TYPES,
    V0_0_0_DOCUMENTS,
    V0_0_0_DOCUMENTS_METADATA,
    V0_0_0_DOCUMENTS_SEARCH,
    V0_0_0_GROUPS,
    V0_0_0_MAIL_ACCOUNTS,
    V0_0_0_MAIL_RULES,
    V0_0_0_OBJECT_PERMISSIONS,
    V0_0_0_PATHS,
    V0_0_0_REMOTE_VERSION,
    V0_0_0_SAVED_VIEWS,
    V0_0_0_TAGS,
    V0_0_0_TASKS,
    V0_0_0_TOKEN,
    V0_0_0_USERS,
)
from .v1_8_0 import V1_8_0_PATHS, V1_8_0_STORAGE_PATHS
from .v1_17_0 import V1_17_0_DOCUMENT_NOTES
from .v2_0_0 import (
    V2_0_0_CONFIG,
    V2_0_0_CUSTOM_FIELDS,
    V2_0_0_PATHS,
    V2_0_0_SHARE_LINKS,
)
from .v2_3_0 import (
    V2_3_0_PATHS,
    V2_3_0_WORKFLOW_ACTIONS,
    V2_3_0_WORKFLOW_TRIGGERS,
    V2_3_0_WORKFLOWS,
)
from .v2_6_0 import V2_6_0_STATUS
from .v2_15_0 import V2_15_0_STATISTICS

# mypy: ignore-errors


def _read_schema(filename: str) -> dict:
    filepath = Path(f"tests/data/api-schema_{filename}.json")
    with Path.open(filepath, mode="r", encoding="utf-8") as file:
        return json.load(file)


_schema_v2_15_0 = _read_schema("v2.15.0")

PATCHWORK = {
    # 0.0.0
    "paths": V0_0_0_PATHS | V1_8_0_PATHS | V2_0_0_PATHS | V2_3_0_PATHS,
    "paths_v0_0_0": V0_0_0_PATHS,
    "paths_v1_8_0": V1_8_0_PATHS,
    "paths_v2_0_0": V2_0_0_PATHS,
    "paths_v2_3_0": V2_3_0_PATHS,
    "correspondents": V0_0_0_CORRESPONDENTS,
    "documents": V0_0_0_DOCUMENTS,
    "documents_metadata": V0_0_0_DOCUMENTS_METADATA,
    "documents_search": V0_0_0_DOCUMENTS_SEARCH,
    "documents_suggestions": V0_0_0_DOCUMENT_SUGGESTIONS,
    "document_types": V0_0_0_DOCUMENT_TYPES,
    "groups": V0_0_0_GROUPS,
    "mail_accounts": V0_0_0_MAIL_ACCOUNTS,
    "mail_rules": V0_0_0_MAIL_RULES,
    "object_permissions": V0_0_0_OBJECT_PERMISSIONS,
    "saved_views": V0_0_0_SAVED_VIEWS,
    "tags": V0_0_0_TAGS,
    "tasks": V0_0_0_TASKS,
    "token": V0_0_0_TOKEN,
    "users": V0_0_0_USERS,
    "remote_version": V0_0_0_REMOTE_VERSION,
    # 1.8.0
    "storage_paths": V1_8_0_STORAGE_PATHS,
    # 1.17.0
    "document_notes": V1_17_0_DOCUMENT_NOTES,
    # 2.0.0
    "config": V2_0_0_CONFIG,
    "custom_fields": V2_0_0_CUSTOM_FIELDS,
    "share_links": V2_0_0_SHARE_LINKS,
    # 2.3.0
    "workflows": V2_3_0_WORKFLOWS,
    "workflow_actions": V2_3_0_WORKFLOW_ACTIONS,
    "workflow_triggers": V2_3_0_WORKFLOW_TRIGGERS,
    # 2.6.0
    "status": V2_6_0_STATUS,
    # 2.15.0
    "schema": _schema_v2_15_0,
    "statistics": V2_15_0_STATISTICS,
}

__all__ = ("PATCHWORK",)
