"""Document history snapshot."""

DATA_DOCUMENT_HISTORY = [
    {
        "id": 10,
        "timestamp": "2024-01-15T10:30:00Z",
        "action": "update",
        "changes": {
            "title": ["Old Title", "New Title"],
        },
        "actor": {
            "id": 1,
            "username": "admin",
        },
    },
    {
        "id": 9,
        "timestamp": "2024-01-14T09:00:00Z",
        "action": "update",
        "changes": {
            "tags": {
                "type": "m2m",
                "operation": "add",
                "objects": ["invoices", "2024"],
            },
        },
        "actor": {
            "id": 1,
            "username": "admin",
        },
    },
    {
        "id": 1,
        "timestamp": "2024-01-01T08:00:00Z",
        "action": "create",
        "changes": {
            "id": ["None", "42"],
            "content": ["None", "Document content here."],
        },
        "actor": {
            "id": 1,
            "username": "admin",
        },
    },
]
