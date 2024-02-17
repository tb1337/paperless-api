"""Raw data constants for Paperless versions >= 2.3.0."""

from tests.const import PAPERLESS_TEST_URL

# mypy: ignore-errors

V2_3_0_PATHS = {
    "workflows": f"{PAPERLESS_TEST_URL}/api/workflows/",
    "workflow_actions": f"{PAPERLESS_TEST_URL}/api/workflow_actions/",
    "workflow_triggers": f"{PAPERLESS_TEST_URL}/api/workflow_triggers/",
}

V2_3_0_WORKFLOWS = {
    "count": 3,
    "next": None,
    "previous": None,
    "all": [1, 2, 3],
    "results": [
        {
            "id": 1,
            "name": "Importordner Template",
            "order": 1,
            "enabled": True,
            "triggers": [
                {
                    "id": 1,
                    "sources": [1],
                    "type": 1,
                    "filter_path": None,
                    "filter_filename": "*.pdf",
                    "filter_mailrule": None,
                    "matching_algorithm": 0,
                    "match": "",
                    "is_insensitive": None,
                    "filter_has_tags": [],
                    "filter_has_correspondent": None,
                    "filter_has_document_type": None,
                }
            ],
            "actions": [
                {
                    "id": 1,
                    "type": 1,
                    "assign_title": "Some workflow title",
                    "assign_tags": [4],
                    "assign_correspondent": 9,
                    "assign_document_type": 8,
                    "assign_storage_path": 2,
                    "assign_owner": 3,
                    "assign_view_users": [],
                    "assign_view_groups": [],
                    "assign_change_users": [],
                    "assign_change_groups": [],
                    "assign_custom_fields": [2],
                }
            ],
        },
        {
            "id": 2,
            "name": "API Upload Template",
            "order": 2,
            "enabled": True,
            "triggers": [
                {
                    "id": 2,
                    "sources": [1, 2],
                    "type": 1,
                    "filter_path": "/api/*",
                    "filter_filename": "*.pdf",
                    "filter_mailrule": None,
                    "matching_algorithm": 0,
                    "match": "",
                    "is_insensitive": None,
                    "filter_has_tags": [],
                    "filter_has_correspondent": None,
                    "filter_has_document_type": None,
                }
            ],
            "actions": [
                {
                    "id": 2,
                    "type": 1,
                    "assign_title": "API",
                    "assign_tags": [4],
                    "assign_correspondent": 9,
                    "assign_document_type": 12,
                    "assign_storage_path": 2,
                    "assign_owner": 3,
                    "assign_view_users": [],
                    "assign_view_groups": [],
                    "assign_change_users": [],
                    "assign_change_groups": [],
                    "assign_custom_fields": [5],
                }
            ],
        },
        {
            "id": 3,
            "name": "Email Template",
            "order": 3,
            "enabled": False,
            "triggers": [
                {
                    "id": 3,
                    "sources": [3],
                    "type": 1,
                    "filter_path": "/mail/*",
                    "filter_filename": "*.eml",
                    "filter_mailrule": 1,
                    "matching_algorithm": 0,
                    "match": "",
                    "is_insensitive": True,
                    "filter_has_tags": [],
                    "filter_has_correspondent": None,
                    "filter_has_document_type": None,
                }
            ],
            "actions": [
                {
                    "id": 3,
                    "type": 1,
                    "assign_title": None,
                    "assign_tags": [],
                    "assign_correspondent": None,
                    "assign_document_type": None,
                    "assign_storage_path": None,
                    "assign_owner": 2,
                    "assign_view_users": [3, 7],
                    "assign_view_groups": [1],
                    "assign_change_users": [6],
                    "assign_change_groups": [],
                    "assign_custom_fields": [],
                }
            ],
        },
    ],
}

V2_3_0_WORKFLOW_ACTIONS = {
    "count": 0,
    "next": None,
    "previous": None,
    "all": [],
    "results": [],
}
for wf in V2_3_0_WORKFLOWS["results"]:
    V2_3_0_WORKFLOW_ACTIONS["count"] += 1
    for act in wf["actions"]:
        V2_3_0_WORKFLOW_ACTIONS["all"].append(act["id"])
        V2_3_0_WORKFLOW_ACTIONS["results"].append(act)

V2_3_0_WORKFLOW_TRIGGERS = {
    "count": 0,
    "next": None,
    "previous": None,
    "all": [],
    "results": [],
}
for wf in V2_3_0_WORKFLOWS["results"]:
    V2_3_0_WORKFLOW_TRIGGERS["count"] += 1
    for act in wf["triggers"]:
        V2_3_0_WORKFLOW_TRIGGERS["all"].append(act["id"])
        V2_3_0_WORKFLOW_TRIGGERS["results"].append(act)
