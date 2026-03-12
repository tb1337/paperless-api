# Statistics

The `statistics` resource returns aggregate counts and metadata about the Paperless-ngx document archive. It is a parameter-free singleton call.

## Model

| Field                       | Description                            |
| --------------------------- | -------------------------------------- |
| `documents_total`           | Total number of documents              |
| `documents_inbox`           | Documents in the inbox                 |
| `inbox_tag`                 | Primary inbox tag id                   |
| `inbox_tags`                | All inbox tag ids                      |
| `document_file_type_counts` | MIME type breakdown                    |
| `character_count`           | Total characters across all documents  |
| `tag_count`                 | Number of tags                         |
| `correspondent_count`       | Number of correspondents               |
| `document_type_count`       | Number of document types               |
| `storage_path_count`        | Number of storage paths                |
| `current_asn`               | Highest assigned archive serial number |

### `StatisticDocumentFileTypeCount`

| Field             | Description                        |
| ----------------- | ---------------------------------- |
| `mime_type`       | MIME type string                   |
| `mime_type_count` | Number of documents with this type |

## Fetch

No primary key — call without arguments:

```python
stats = await paperless.statistics()

print(stats.documents_total)      # 1024
print(stats.documents_inbox)      # 3
print(stats.current_asn)          # 512
print(stats.correspondent_count)  # 47

for ft in stats.document_file_type_counts or []:
    print(ft.mime_type, ft.mime_type_count)
    # "application/pdf" 980
    # "image/jpeg" 44
```
