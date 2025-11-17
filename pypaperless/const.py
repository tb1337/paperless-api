"""PyPaperless constants."""

from __future__ import annotations

from enum import StrEnum

API_VERSION = 9

CONFIG = "config"  # pylint: disable=invalid-name
CONSUMPTION_TEMPLATES = "consumption_templates"  # pylint: disable=invalid-name
CORRESPONDENTS = "correspondents"  # pylint: disable=invalid-name
CUSTOM_FIELDS = "custom_fields"  # pylint: disable=invalid-name
DOCUMENTS = "documents"  # pylint: disable=invalid-name
DOCUMENT_TYPES = "document_types"  # pylint: disable=invalid-name
GROUPS = "groups"  # pylint: disable=invalid-name
LOGS = "logs"  # pylint: disable=invalid-name
MAIL_ACCOUNTS = "mail_accounts"  # pylint: disable=invalid-name
MAIL_RULES = "mail_rules"  # pylint: disable=invalid-name
PROCESSED_MAIL = "processed_mail"  # pylint: disable=invalid-name
SAVED_VIEWS = "saved_views"  # pylint: disable=invalid-name
SHARE_LINKS = "share_links"  # pylint: disable=invalid-name
STATISTICS = "statistics"  # pylint: disable=invalid-name
REMOTE_VERSION = "remote_version"  # pylint: disable=invalid-name
STATUS = "status"  # pylint: disable=invalid-name
STORAGE_PATHS = "storage_paths"  # pylint: disable=invalid-name
TAGS = "tags"  # pylint: disable=invalid-name
TASKS = "tasks"  # pylint: disable=invalid-name
USERS = "users"  # pylint: disable=invalid-name
WORKFLOW_ACTIONS = "workflow_actions"  # pylint: disable=invalid-name
WORKFLOWS = "workflows"  # pylint: disable=invalid-name
WORKFLOW_TRIGGERS = "workflow_triggers"  # pylint: disable=invalid-name
UNKNOWN = "unknown"  # pylint: disable=invalid-name

API_PATH = {
    "index": "/api/schema/",
    "token": "/api/token/",
    f"{CONFIG}": f"/api/{CONFIG}/",
    f"{CONFIG}_single": f"/api/{CONFIG}/{{pk}}/",
    f"{CORRESPONDENTS}": f"/api/{CORRESPONDENTS}/",
    f"{CORRESPONDENTS}_single": f"/api/{CORRESPONDENTS}/{{pk}}/",
    f"{CUSTOM_FIELDS}": f"/api/{CUSTOM_FIELDS}/",
    f"{CUSTOM_FIELDS}_single": f"/api/{CUSTOM_FIELDS}/{{pk}}/",
    f"{DOCUMENTS}": f"/api/{DOCUMENTS}/",
    f"{DOCUMENTS}_download": f"/api/{DOCUMENTS}/{{pk}}/download/",
    f"{DOCUMENTS}_email": f"/api/{DOCUMENTS}/email/",
    f"{DOCUMENTS}_meta": f"/api/{DOCUMENTS}/{{pk}}/metadata/",
    f"{DOCUMENTS}_next_asn": f"/api/{DOCUMENTS}/next_asn/",
    f"{DOCUMENTS}_notes": f"/api/{DOCUMENTS}/{{pk}}/notes/",
    f"{DOCUMENTS}_preview": f"/api/{DOCUMENTS}/{{pk}}/preview/",
    f"{DOCUMENTS}_thumbnail": f"/api/{DOCUMENTS}/{{pk}}/thumb/",
    f"{DOCUMENTS}_post": f"/api/{DOCUMENTS}/post_document/",
    f"{DOCUMENTS}_single": f"/api/{DOCUMENTS}/{{pk}}/",
    f"{DOCUMENTS}_suggestions": f"/api/{DOCUMENTS}/{{pk}}/suggestions/",
    f"{DOCUMENT_TYPES}": f"/api/{DOCUMENT_TYPES}/",
    f"{DOCUMENT_TYPES}_single": f"/api/{DOCUMENT_TYPES}/{{pk}}/",
    f"{GROUPS}": f"/api/{GROUPS}/",
    f"{GROUPS}_single": f"/api/{GROUPS}/{{pk}}/",
    f"{MAIL_ACCOUNTS}": f"/api/{MAIL_ACCOUNTS}/",
    f"{MAIL_ACCOUNTS}_single": f"/api/{MAIL_ACCOUNTS}/{{pk}}/",
    f"{MAIL_RULES}": f"/api/{MAIL_RULES}/",
    f"{MAIL_RULES}_single": f"/api/{MAIL_RULES}/{{pk}}/",
    f"{PROCESSED_MAIL}": f"/api/{PROCESSED_MAIL}/",
    f"{PROCESSED_MAIL}_single": f"/api/{PROCESSED_MAIL}/{{pk}}/",
    f"{SAVED_VIEWS}": f"/api/{SAVED_VIEWS}/",
    f"{SAVED_VIEWS}_single": f"/api/{SAVED_VIEWS}/{{pk}}/",
    f"{SHARE_LINKS}": f"/api/{SHARE_LINKS}/",
    f"{SHARE_LINKS}_single": f"/api/{SHARE_LINKS}/{{pk}}/",
    f"{STATISTICS}": f"/api/{STATISTICS}/",
    f"{REMOTE_VERSION}": f"/api/{REMOTE_VERSION}/",
    f"{STATUS}": f"/api/{STATUS}/",
    f"{STORAGE_PATHS}": f"/api/{STORAGE_PATHS}/",
    f"{STORAGE_PATHS}_single": f"/api/{STORAGE_PATHS}/{{pk}}/",
    f"{TAGS}": f"/api/{TAGS}/",
    f"{TAGS}_single": f"/api/{TAGS}/{{pk}}/",
    f"{TASKS}": f"/api/{TASKS}/",
    f"{TASKS}_single": f"/api/{TASKS}/{{pk}}/",
    f"{USERS}": f"/api/{USERS}/",
    f"{USERS}_single": f"/api/{USERS}/{{pk}}/",
    f"{WORKFLOWS}": f"/api/{WORKFLOWS}/",
    f"{WORKFLOWS}_single": f"/api/{WORKFLOWS}/{{pk}}/",
    f"{WORKFLOW_ACTIONS}": f"/api/{WORKFLOW_ACTIONS}/",
    f"{WORKFLOW_ACTIONS}_single": f"/api/{WORKFLOW_ACTIONS}/{{pk}}/",
    f"{WORKFLOW_TRIGGERS}": f"/api/{WORKFLOW_TRIGGERS}/",
    f"{WORKFLOW_TRIGGERS}_single": f"/api/{WORKFLOW_TRIGGERS}/{{pk}}/",
}


class PaperlessResource(StrEnum):
    """Represent paths of api endpoints."""

    CONFIG = CONFIG
    CONSUMPTION_TEMPLATES = CONSUMPTION_TEMPLATES
    CORRESPONDENTS = CORRESPONDENTS
    CUSTOM_FIELDS = CUSTOM_FIELDS
    DOCUMENTS = DOCUMENTS
    DOCUMENT_TYPES = DOCUMENT_TYPES
    GROUPS = GROUPS
    LOGS = LOGS
    MAIL_ACCOUNTS = MAIL_ACCOUNTS
    MAIL_RULES = MAIL_RULES
    PROCESSED_MAIL = PROCESSED_MAIL
    SAVED_VIEWS = SAVED_VIEWS
    SHARE_LINKS = SHARE_LINKS
    STATISTICS = STATISTICS
    REMOTE_VERSION = REMOTE_VERSION
    STATUS = STATUS
    STORAGE_PATHS = STORAGE_PATHS
    TAGS = TAGS
    TASKS = TASKS
    USERS = USERS
    WORKFLOWS = WORKFLOWS
    WORKFLOW_ACTIONS = WORKFLOW_ACTIONS
    WORKFLOW_TRIGGERS = WORKFLOW_TRIGGERS
    UNKNOWN = UNKNOWN

    @classmethod
    def _missing_(cls: type[PaperlessResource], *_: object) -> PaperlessResource:
        """Set default member on unknown value."""
        return cls.UNKNOWN
