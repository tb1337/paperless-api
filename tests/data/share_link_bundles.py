"""Share link bundles snapshot."""

DATA_SHARE_LINK_BUNDLES = {
    "count": 2,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 1,
            "created": "2024-01-15T10:00:00.000000Z",
            "expiration": "2024-02-15T10:00:00.000000Z",
            "slug": "bundle-abc123",
            "file_version": "archive",
            "status": "ready",
            "size_bytes": 204800,
            "last_error": None,
            "built_at": "2024-01-15T10:05:00.000000Z",
            "documents": [1, 2, 3],
            "document_count": 3,
        },
        {
            "id": 2,
            "created": "2024-01-16T09:00:00.000000Z",
            "expiration": None,
            "slug": "bundle-xyz789",
            "file_version": "original",
            "status": "pending",
            "size_bytes": None,
            "last_error": None,
            "built_at": None,
            "documents": [4, 5],
            "document_count": 2,
        },
    ],
}
