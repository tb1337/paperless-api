"""Controllers for Paperless api endpoints."""

from .default import (
    ConsumptionTemplatesController,
    CorrespondentsController,
    CustomFieldsController,
    DocumentTypesController,
    GroupsController,
    MailAccountsController,
    MailRulesController,
    SavedViewsController,
    ShareLinksController,
    StoragePathsController,
    TagsController,
    UsersController,
    WorkflowActionsController,
    WorkflowsController,
    WorkflowTriggersController,
)
from .documents import DocumentsController
from .tasks import TasksController

__all__ = [
    "ConsumptionTemplatesController",
    "CorrespondentsController",
    "CustomFieldsController",
    "DocumentsController",
    "DocumentTypesController",
    "GroupsController",
    "MailAccountsController",
    "MailRulesController",
    "SavedViewsController",
    "ShareLinksController",
    "StoragePathsController",
    "TagsController",
    "TasksController",
    "UsersController",
    "WorkflowActionsController",
    "WorkflowsController",
    "WorkflowTriggersController",
]
