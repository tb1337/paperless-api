"""Tests for pypaperless."""

from dataclasses import dataclass
from typing import Any

from pypaperless import helpers, models
from pypaperless.const import PaperlessResource
from pypaperless.models import common

# mypy: ignore-errors


@dataclass
class ResourceTestMapping:
    """Mapping for test cases."""

    resource: str
    helper_cls: type
    model_cls: type
    draft_cls: type | None = None
    draft_defaults: dict[str, Any] | None = None


CONFIG_MAP = ResourceTestMapping(
    PaperlessResource.CONFIG,
    helpers.ConfigHelper,
    models.Config,
)

CORRESPONDENT_MAP = ResourceTestMapping(
    PaperlessResource.CORRESPONDENTS,
    helpers.CorrespondentHelper,
    models.Correspondent,
    models.CorrespondentDraft,
    {
        "name": "New Correspondent",
        "match": "",
        "matching_algorithm": common.MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)

CUSTOM_FIELD_MAP = ResourceTestMapping(
    PaperlessResource.CUSTOM_FIELDS,
    helpers.CustomFieldHelper,
    models.CustomField,
    models.CustomFieldDraft,
    {
        "name": "New Custom Field",
        "data_type": common.CustomFieldType.BOOLEAN,
    },
)

DOCUMENT_MAP = ResourceTestMapping(
    PaperlessResource.DOCUMENTS,
    helpers.DocumentHelper,
    models.Document,
    models.DocumentDraft,
    {
        "document": b"...example...content...",
        "tags": [1, 2, 3],
        "correspondent": 1,
        "document_type": 1,
        "storage_path": 1,
        "title": "New Document",
        "created": None,
        "archive_serial_number": 1,
    },
)

DOCUMENT_TYPE_MAP = ResourceTestMapping(
    PaperlessResource.DOCUMENT_TYPES,
    helpers.DocumentTypeHelper,
    models.DocumentType,
    models.DocumentTypeDraft,
    {
        "name": "New Document Type",
        "match": "",
        "matching_algorithm": common.MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)

GROUP_MAP = ResourceTestMapping(
    PaperlessResource.GROUPS,
    helpers.GroupHelper,
    models.Group,
)

MAIL_ACCOUNT_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_ACCOUNTS,
    helpers.MailAccountHelper,
    models.MailAccount,
)

MAIL_RULE_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_RULES,
    helpers.MailRuleHelper,
    models.MailRule,
)

SAVED_VIEW_MAP = ResourceTestMapping(
    PaperlessResource.SAVED_VIEWS,
    helpers.SavedViewHelper,
    models.SavedView,
)

SHARE_LINK_MAP = ResourceTestMapping(
    PaperlessResource.SHARE_LINKS,
    helpers.ShareLinkHelper,
    models.ShareLink,
    models.ShareLinkDraft,
    {
        "expiration": None,
        "document": 1,
        "file_version": common.ShareLinkFileVersionType.ORIGINAL,
    },
)

STATUS_MAP = ResourceTestMapping(
    PaperlessResource.STATUS,
    helpers.StatusHelper,
    models.Status,
)

STORAGE_PATH_MAP = ResourceTestMapping(
    PaperlessResource.STORAGE_PATHS,
    helpers.StoragePathHelper,
    models.StoragePath,
    models.StoragePathDraft,
    {
        "name": "New Storage Path",
        "path": "path/to/test",
        "match": "",
        "matching_algorithm": common.MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)

TAG_MAP = ResourceTestMapping(
    PaperlessResource.TAGS,
    helpers.TagHelper,
    models.Tag,
    models.TagDraft,
    {
        "name": "New Tag",
        "color": "#012345",
        "text_color": "#987654",
        "is_inbox_tag": False,
        "match": "",
        "matching_algorithm": common.MatchingAlgorithmType.ANY,
        "is_insensitive": True,
    },
)

TASK_MAP = ResourceTestMapping(
    PaperlessResource.TASKS,
    helpers.TaskHelper,
    models.Task,
)

USER_MAP = ResourceTestMapping(
    PaperlessResource.USERS,
    helpers.UserHelper,
    models.User,
)

WORKFLOW_MAP = ResourceTestMapping(
    PaperlessResource.WORKFLOWS,
    helpers.WorkflowHelper,
    models.Workflow,
)
