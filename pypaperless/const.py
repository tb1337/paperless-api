"""PyPaperless constants."""

from enum import StrEnum

API_PATH = {
    "index": "/api/",
    "custom_fields": "/api/custom_fields/",
    "custom_fields_single": "/api/custom_fields/{pk}/",
    "documents": "/api/documents/",
    "documents_meta": "/api/documents/{pk}/metadata/",
    "documents_notes": "/api/documents/{pk}/notes/",
    "documents_post": "/api/documents/post_document/",
    "documents_single": "/api/documents/{pk}/",
}


CONSUMPTION_TEMPLATES = "consumption_templates"
CORRESPONDENTS = "correspondents"
CUSTOM_FIELDS = "custom_fields"
DOCUMENTS = "documents"
DOCUMENT_TYPES = "document_types"
GROUPS = "groups"
MAIL_ACCOUNTS = "mail_accounts"
MAIL_RULES = "mail_rules"
SAVED_VIEWS = "saved_views"
SHARE_LINKS = "share_links"
STORAGE_PATHS = "storage_paths"
TAGS = "tags"
TASKS = "tasks"
USERS = "users"
WORKFLOW_ACTIONS = "workflow_actions"
WORKFLOWS = "workflows"
WORKFLOW_TRIGGERS = "workflow_triggers"
UNKNOWN = "unknown"


class PaperlessEndpoints(StrEnum):
    """Represent paths of api endpoints."""

    CONSUMPTION_TEMPLATES = CONSUMPTION_TEMPLATES
    CORRESPONDENTS = CORRESPONDENTS
    CUSTOM_FIELDS = CUSTOM_FIELDS
    DOCUMENTS = DOCUMENTS
    DOCUMENT_TYPES = DOCUMENT_TYPES
    GROUPS = GROUPS
    MAIL_ACCOUNTS = MAIL_ACCOUNTS
    MAIL_RULES = MAIL_RULES
    SAVED_VIEWS = SAVED_VIEWS
    SHARE_LINKS = SHARE_LINKS
    STORAGE_PATHS = STORAGE_PATHS
    TAGS = TAGS
    TASKS = TASKS
    USERS = USERS
    WORKFLOWS = WORKFLOWS
    WORKFLOW_ACTIONS = WORKFLOW_ACTIONS
    WORKFLOW_TRIGGERS = WORKFLOW_TRIGGERS
    UNKNOWN = UNKNOWN
