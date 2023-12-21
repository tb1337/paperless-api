"""API endpoints for Paperless resources."""

from .default import (
    ConsumptionTemplatesEndpoint,
    CorrespondentsEndpoint,
    CustomFieldEndpoint,
    DocumentTypesEndpoint,
    GroupsEndpoint,
    MailAccountsEndpoint,
    MailRulesEndpoint,
    SavedViewsEndpoint,
    ShareLinkEndpoint,
    StoragePathsEndpoint,
    TagsEndpoint,
    UsersEndpoint,
)
from .documents import DocumentsEndpoint
from .tasks import TasksEndpoint

__all__ = [
    "ConsumptionTemplatesEndpoint",
    "CorrespondentsEndpoint",
    "CustomFieldEndpoint",
    "DocumentTypesEndpoint",
    "DocumentsEndpoint",
    "GroupsEndpoint",
    "MailAccountsEndpoint",
    "MailRulesEndpoint",
    "SavedViewsEndpoint",
    "ShareLinkEndpoint",
    "StoragePathsEndpoint",
    "TagsEndpoint",
    "TasksEndpoint",
    "UsersEndpoint",
]
