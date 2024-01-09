"""PyPaperless const values."""

from enum import IntFlag, StrEnum

from awesomeversion import AwesomeVersion

PAPERLESS_V1_8_0 = AwesomeVersion("1.8.0")
PAPERLESS_V2_0_0 = AwesomeVersion("2.0.0")
PAPERLESS_V2_3_0 = AwesomeVersion("2.3.0")


CTRL_CONSUMPTION_TEMPLATES = "consumption_templates"
CTRL_CORRESPONDENTS = "correspondents"
CTRL_CUSTOM_FIELDS = "custom_fields"
CTRL_DOCUMENTS = "documents"
CTRL_DOCUMENT_TYPES = "document_types"
CTRL_GROUPS = "groups"
CTRL_MAIL_ACCOUNTS = "mail_accounts"
CTRL_MAIL_RULES = "mail_rules"
CTRL_SAVED_VIEWS = "saved_views"
CTRL_SHARE_LINKS = "share_links"
CTRL_STORAGE_PATHS = "storage_paths"
CTRL_TAGS = "tags"
CTRL_TASKS = "tasks"
CTRL_USERS = "users"
CTRL_WORKFLOW_ACTIONS = "workflow_actions"
CTRL_WORKFLOWS = "workflows"
CTRL_WORKFLOW_TRIGGERS = "workflow_triggers"
CTRL_UNKNOWN = "unknown"


class PaperlessFeature(IntFlag):
    """Supported controllers."""

    STORAGE_PATHS = 1
    SHARE_LINKS = 2
    CUSTOM_FIELDS = 4
    CONSUMPTION_TEMPLATES = 8
    WORKFLOWS = 16
    CONFIGS = 32


class ControllerPath(StrEnum):
    """Represent paths of api endpoints."""

    CONSUMPTION_TEMPLATES = CTRL_CONSUMPTION_TEMPLATES
    CORRESPONDENTS = CTRL_CORRESPONDENTS
    CUSTOM_FIELDS = CTRL_CUSTOM_FIELDS
    DOCUMENTS = CTRL_DOCUMENTS
    DOCUMENT_TYPES = CTRL_DOCUMENT_TYPES
    GROUPS = CTRL_GROUPS
    MAIL_ACCOUNTS = CTRL_MAIL_ACCOUNTS
    MAIL_RULES = CTRL_MAIL_RULES
    SAVED_VIEWS = CTRL_SAVED_VIEWS
    SHARE_LINKS = CTRL_SHARE_LINKS
    STORAGE_PATHS = CTRL_STORAGE_PATHS
    TAGS = CTRL_TAGS
    TASKS = CTRL_TASKS
    USERS = CTRL_USERS
    WORKFLOWS = CTRL_WORKFLOWS
    WORKFLOW_ACTIONS = CTRL_WORKFLOW_ACTIONS
    WORKFLOW_TRIGGERS = CTRL_WORKFLOW_TRIGGERS
    UNKNOWN = CTRL_UNKNOWN
