"""Models and types for bulk-edit operations."""

from typing import Literal

type BulkEditObjectType = Literal["tags", "correspondents", "document_types", "storage_paths"]
