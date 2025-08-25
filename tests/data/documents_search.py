"""Documents search snapshot."""

# mypy: ignore-errors

DATA_DOCUMENTS_SEARCH = {
    "count": 1,
    "next": None,
    "previous": None,
    "all": [1],
    "results": [
        {
            "id": 1,
            "correspondent": 1,
            "document_type": 2,
            "storage_path": None,
            "title": "Crazy Document",
            "content": "some OCRd text",
            "tags": [],
            "created": "2011-06-22T00:00:00+00:00",
            "created_date": "2011-06-22",
            "modified": "2023-08-08T06:06:35.495972+00:00",
            "added": "2023-06-30T05:44:14.317925+00:00",
            "archive_serial_number": None,
            "original_file_name": "Scan_2023-06-29_113857.pdf",
            "archived_file_name": "2011-06-22 filename.pdf",
            "owner": 2,
            "user_can_change": True,
            "notes": [],
            "custom_fields": [],
            "__search_hit__": {
                "score": 1.0,
                "highlights": "some neat hint",
                "note_highlights": "",
                "rank": 0,
            },
        },
    ],
}
