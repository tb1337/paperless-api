"""PyPaperless constants."""

from enum import StrEnum

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

API_PATH = {
    "index": "/api/",
    f"{CUSTOM_FIELDS}": f"/api/{CUSTOM_FIELDS}/",
    f"{CUSTOM_FIELDS}_single": f"/api/{CUSTOM_FIELDS}/{{pk}}/",
    f"{DOCUMENTS}": f"/api/{DOCUMENTS}/",
    f"{DOCUMENTS}_meta": f"/api/{DOCUMENTS}/{{pk}}/metadata/",
    f"{DOCUMENTS}_notes": f"/api/{DOCUMENTS}/{{pk}}/notes/",
    f"{DOCUMENTS}_post": f"/api/{DOCUMENTS}/post_document/",
    f"{DOCUMENTS}_single": f"/api/{DOCUMENTS}/{{pk}}/",
    f"{GROUPS}": f"/api/{GROUPS}/",
    f"{GROUPS}_single": f"/api/{GROUPS}/{{pk}}/",
    f"{MAIL_ACCOUNTS}": f"/api/{MAIL_ACCOUNTS}/",
    f"{MAIL_ACCOUNTS}_single": f"/api/{MAIL_ACCOUNTS}/{{pk}}/",
    f"{MAIL_RULES}": f"/api/{MAIL_RULES}/",
    f"{MAIL_RULES}_single": f"/api/{MAIL_RULES}/{{pk}}/",
    f"{SAVED_VIEWS}": f"/api/{SAVED_VIEWS}/",
    f"{SAVED_VIEWS}_single": f"/api/{SAVED_VIEWS}/{{pk}}/",
    f"{SHARE_LINKS}": f"/api/{SHARE_LINKS}/",
    f"{SHARE_LINKS}_single": f"/api/{SHARE_LINKS}/{{pk}}/",
    f"{USERS}": f"/api/{USERS}/",
    f"{USERS}_single": f"/api/{USERS}/{{pk}}/",
}


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
