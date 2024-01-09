"""Raw data constants for all Paperless versions."""

from tests.const import PAPERLESS_TEST_URL

V0_0_0_PATHS = {
    "correspondents": f"{PAPERLESS_TEST_URL}/api/correspondents/",
    "document_types": f"{PAPERLESS_TEST_URL}/api/document_types/",
    "documents": f"{PAPERLESS_TEST_URL}/api/documents/",
    "logs": f"{PAPERLESS_TEST_URL}/api/logs/",
    "tags": f"{PAPERLESS_TEST_URL}/api/tags/",
    "saved_views": f"{PAPERLESS_TEST_URL}/api/saved_views/",
    "tasks": f"{PAPERLESS_TEST_URL}/api/tasks/",
    "users": f"{PAPERLESS_TEST_URL}/api/users/",
    "groups": f"{PAPERLESS_TEST_URL}/api/groups/",
    "mail_accounts": f"{PAPERLESS_TEST_URL}/api/mail_accounts/",
    "mail_rules": f"{PAPERLESS_TEST_URL}/api/mail_rules/",
}
