"""Raw data constants for Paperless versions >= 2.15.0."""

# mypy: ignore-errors

V2_15_0_STATISTICS = {
    "documents_total": 1337,
    "documents_inbox": 2,
    "inbox_tag": 1,
    "inbox_tags": [1],
    "document_file_type_counts": [
        {"mime_type": "application/pdf", "mime_type_count": 1334},
        {"mime_type": "image/jpeg", "mime_type_count": 2},
        {"mime_type": "message/rfc822", "mime_type_count": 1},
    ],
    "character_count": 13371337,
    "tag_count": 5,
    "correspondent_count": 42,
    "document_type_count": 23,
    "storage_path_count": 5,
    "current_asn": 84,
}
