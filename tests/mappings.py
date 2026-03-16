"""Resource test mappings for parameterized tests."""

from dataclasses import dataclass
from typing import Any

from pypaperless import models, services
from pypaperless.const import PaperlessResource
from pypaperless.models import types

from .data import (
    DATA_CONFIG,
    DATA_CORRESPONDENTS,
    DATA_CUSTOM_FIELDS,
    DATA_DOCUMENT_TYPES,
    DATA_DOCUMENTS,
    DATA_GROUPS,
    DATA_MAIL_ACCOUNTS,
    DATA_MAIL_RULES,
    DATA_PROCESSED_MAIL,
    DATA_SAVED_VIEWS,
    DATA_SHARE_LINKS,
    DATA_STATUS,
    DATA_STORAGE_PATHS,
    DATA_TAGS,
    DATA_TASKS,
    DATA_USERS,
    DATA_WORKFLOWS,
)


@dataclass
class ResourceTestMapping:
    """Mapping for parameterized resource test cases."""

    resource: str
    data: dict[str, Any] | list[dict[str, Any]]
    service_cls: type
    model_cls: type
    draft_cls: type | None = None
    draft_defaults: dict[str, Any] | None = None
    # field name to blank-out for DraftFieldRequiredError check; None = skip
    required_field: str | None = "name"
    # field and value used by test_update
    update_field: str = "name"
    update_value: Any = "Name Updated"


CONFIG_MAP = ResourceTestMapping(
    PaperlessResource.CONFIG,
    DATA_CONFIG,
    services.ConfigService,
    models.Config,
)

CORRESPONDENT_MAP = ResourceTestMapping(
    PaperlessResource.CORRESPONDENTS,
    DATA_CORRESPONDENTS,
    services.CorrespondentService,
    models.Correspondent,
    models.CorrespondentDraft,
    {
        "name": "New Correspondent",
        "match": "",
        "matching_algorithm": types.MatchingAlgorithm.ANY,
        "is_insensitive": True,
    },
)

CUSTOM_FIELD_MAP = ResourceTestMapping(
    PaperlessResource.CUSTOM_FIELDS,
    DATA_CUSTOM_FIELDS,
    services.CustomFieldService,
    models.CustomField,
    models.CustomFieldDraft,
    {
        "name": "New Custom Field",
        "data_type": types.CustomFieldType.BOOLEAN,
    },
    required_field=None,
)

DOCUMENT_MAP = ResourceTestMapping(
    PaperlessResource.DOCUMENTS,
    DATA_DOCUMENTS,
    services.DocumentService,
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
    DATA_DOCUMENT_TYPES,
    services.DocumentTypeService,
    models.DocumentType,
    models.DocumentTypeDraft,
    {
        "name": "New Document Type",
        "match": "",
        "matching_algorithm": types.MatchingAlgorithm.ANY,
        "is_insensitive": True,
    },
)

GROUP_MAP = ResourceTestMapping(
    PaperlessResource.GROUPS,
    DATA_GROUPS,
    services.GroupService,
    models.Group,
)

MAIL_ACCOUNT_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_ACCOUNTS,
    DATA_MAIL_ACCOUNTS,
    services.MailAccountService,
    models.MailAccount,
)

MAIL_RULE_MAP = ResourceTestMapping(
    PaperlessResource.MAIL_RULES,
    DATA_MAIL_RULES,
    services.MailRuleService,
    models.MailRule,
)

PROCESSED_MAIL_MAP = ResourceTestMapping(
    PaperlessResource.PROCESSED_MAIL,
    DATA_PROCESSED_MAIL,
    services.ProcessedMailService,
    models.ProcessedMail,
)

SAVED_VIEW_MAP = ResourceTestMapping(
    PaperlessResource.SAVED_VIEWS,
    DATA_SAVED_VIEWS,
    services.SavedViewService,
    models.SavedView,
)

SHARE_LINK_MAP = ResourceTestMapping(
    PaperlessResource.SHARE_LINKS,
    DATA_SHARE_LINKS,
    services.ShareLinkService,
    models.ShareLink,
    models.ShareLinkDraft,
    {
        "expiration": None,
        "document": 1,
        "file_version": types.ShareLinkFileVersion.ORIGINAL,
    },
    required_field=None,
    update_field="document",
    update_value=2,
)

STATUS_MAP = ResourceTestMapping(
    PaperlessResource.STATUS,
    DATA_STATUS,
    services.StatusService,
    models.Status,
)

STORAGE_PATH_MAP = ResourceTestMapping(
    PaperlessResource.STORAGE_PATHS,
    DATA_STORAGE_PATHS,
    services.StoragePathService,
    models.StoragePath,
    models.StoragePathDraft,
    {
        "name": "New Storage Path",
        "path": "path/to/test",
        "match": "",
        "matching_algorithm": types.MatchingAlgorithm.ANY,
        "is_insensitive": True,
    },
)

TAG_MAP = ResourceTestMapping(
    PaperlessResource.TAGS,
    DATA_TAGS,
    services.TagService,
    models.Tag,
    models.TagDraft,
    {
        "name": "New Tag",
        "color": "#012345",
        "text_color": "#987654",
        "is_inbox_tag": False,
        "match": "",
        "matching_algorithm": types.MatchingAlgorithm.ANY,
        "is_insensitive": True,
    },
)

TASK_MAP = ResourceTestMapping(
    PaperlessResource.TASKS,
    DATA_TASKS,
    services.TaskService,
    models.Task,
)

USER_MAP = ResourceTestMapping(
    PaperlessResource.USERS,
    DATA_USERS,
    services.UserService,
    models.User,
)

WORKFLOW_MAP = ResourceTestMapping(
    PaperlessResource.WORKFLOWS,
    DATA_WORKFLOWS,
    services.WorkflowService,
    models.Workflow,
)
