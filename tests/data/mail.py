"""Mail snapshots."""

# mypy: ignore-errors

DATA_MAIL_ACCOUNTS = {
    "count": 1,
    "next": None,
    "previous": None,
    "all": [1],
    "results": [
        {
            "id": 1,
            "name": "Test Account",
            "imap_server": "imap.omega.net",
            "imap_port": 1337,
            "imap_security": 2,
            "username": "omega-weapon",
            "password": "********************",
            "character_set": "UTF-8",
            "is_token": False,
            "owner": 1,
            "user_can_change": True,
        }
    ],
}

DATA_MAIL_RULES = {
    "count": 1,
    "next": None,
    "previous": None,
    "all": [1],
    "results": [
        {
            "id": 1,
            "name": "Test",
            "account": 1,
            "folder": "INBOX",
            "filter_from": None,
            "filter_to": None,
            "filter_subject": None,
            "filter_body": None,
            "filter_attachment_filename_include": None,
            "filter_attachment_filename_exclude": None,
            "maximum_age": 3,
            "action": 3,
            "action_parameter": None,
            "assign_title_from": 1,
            "assign_tags": [],
            "assign_correspondent_from": 1,
            "assign_correspondent": None,
            "assign_document_type": None,
            "assign_owner_from_rule": True,
            "order": 1,
            "attachment_type": 1,
            "consumption_scope": 1,
            "owner": 1,
            "user_can_change": True,
        }
    ],
}
