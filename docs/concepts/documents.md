# Documents

`paperless.documents` provides the full feature set of the Paperless-ngx document API — in addition to the standard CRUD operations available on all resources.

---

## Fetching a document

```python
document = await paperless.documents(42)

print(document.id)
print(document.title)
print(document.correspondent)   # int (id) or None
print(document.document_type)   # int (id) or None
print(document.tags)            # list[int]
print(document.created)         # datetime.date | None
print(document.content)         # extracted text content
print(document.page_count)
print(document.mime_type)
print(document.archive_serial_number)
```

---

## Downloading file contents

Every document can be fetched in three modes: **download** (archived), **preview** and **thumbnail**. All return a `DownloadedDocument` instance.

```python
download  = await paperless.documents.download(42)
preview   = await paperless.documents.preview(42)
thumbnail = await paperless.documents.thumbnail(42)
```

Or using an already-fetched document:

```python
doc = await paperless.documents(42)

download  = await doc.get_download()
preview   = await doc.get_preview()
thumbnail = await doc.get_thumbnail()
```

The `DownloadedDocument` holds:

| Attribute              | Description                                   |
| ---------------------- | --------------------------------------------- |
| `content`              | Raw binary file data                          |
| `content_type`         | MIME type, e.g. `"application/pdf"`           |
| `disposition_type`     | `"attachment"` or `"inline"`                  |
| `disposition_filename` | Suggested filename from `Content-Disposition` |
| `original`             | Whether the original file was requested       |

### Requesting the original file

By default, the archived (processed) version is returned. Pass `original=True` to get the original uploaded file:

```python
download = await paperless.documents.download(42, original=True)
```

---

## Searching documents

### Full-text search

```python
async for document in paperless.documents.search("type:invoice"):
    print(document.title, document.search_hit.score)
```

You can also pass the query as a keyword argument:

```python
async for document in paperless.documents.search(query="annual report"):
    ...
```

### Custom field query

```python
async for document in paperless.documents.search(
    custom_field_query='["amount", "gte", 10000]'
):
    ...
```

Custom field query syntax is documented in the [Paperless-ngx API reference](https://docs.paperless-ngx.com/api/#filtering-by-custom-fields).

### Search hits

When a document was returned from a search, it carries a `DocumentSearchHit`:

```python
if document.has_search_hit:
    hit = document.search_hit
    print(hit.score)
    print(hit.highlights)
    print(hit.rank)
```

---

## More-like search

Find documents similar to a given document:

```python
async for document in paperless.documents.more_like(42):
    print(document.title)
```

---

## Metadata

```python
meta = await paperless.documents.metadata(42)

# or via a fetched document
doc = await paperless.documents(42)
meta = await doc.get_metadata()
```

The returned `DocumentMeta` object includes embedded metadata from the file (e.g. EXIF or PDF metadata):

```python
for entry in meta.original_metadata:
    print(entry.namespace, entry.key, entry.value)
```

---

## Suggestions

Paperless-ngx can suggest classifiers (correspondent, document type, tags) for a document:

```python
suggestions = await paperless.documents.suggestions(42)

# or via a fetched document
doc = await paperless.documents(42)
suggestions = await doc.get_suggestions()

print(suggestions.correspondents)   # list[int]
print(suggestions.document_types)   # list[int]
print(suggestions.tags)             # list[int]
print(suggestions.storage_paths)    # list[int]
```

---

## Notes

Every document can have a list of notes attached to it.

```python
# Fetch notes for a document
notes = await paperless.documents.notes(42)

# or via a fetched document
doc = await paperless.documents(42)
notes = await doc.notes()

for note in notes:
    print(note.note, note.created)
```

### Adding a note

```python
# Pass the document pk as the first positional argument
draft = paperless.documents.notes.draft(42, note="This needs review")
note_id, doc_id = await paperless.documents.notes.save(draft)
```

Or via a fetched document (the document pk is bound automatically):

```python
doc = await paperless.documents(42)
draft = doc.notes.draft(note="This needs review")
note_id, doc_id = await doc.notes.save(draft)
```

### Deleting a note

```python
note = notes[0]
await paperless.documents.notes.delete(note)
```

---

## Next available ASN

Request the next free archive serial number from Paperless-ngx:

```python
next_asn = await paperless.documents.get_next_asn()
print(f"Next ASN: {next_asn}")
```

---

## Uploading a document

Use `draft()` to construct a document upload and `save()` to submit it. The document content must be provided as `bytes`.

```python
with open("invoice.pdf", "rb") as f:
    content = f.read()

draft = paperless.documents.draft(
    document=content,
    filename="invoice.pdf",
    title="Invoice 2024-01",
    created=datetime.datetime(2024, 1, 15),
    correspondent=3,
    document_type=2,
    tags=[1, 5],
    archive_serial_number=1042,
)

task_id = await paperless.documents.save(draft)
print(f"Upload queued as task: {task_id}")
```

!!! note
    Unlike other resources, `save()` for documents returns a **task ID string**, not an integer ID. The document is processed asynchronously by Paperless-ngx. Use `paperless.tasks` to monitor the task.

### Document draft fields

| Field                   | Description                    |
| ----------------------- | ------------------------------ |
| `document`              | **Required.** Raw file content |
| `filename`              | Optional original filename     |
| `title`                 | Document title                 |
| `created`               | Document creation date         |
| `correspondent`         | Correspondent ID               |
| `document_type`         | Document type ID               |
| `storage_path`          | Storage path ID                |
| `tags`                  | Tag IDs                        |
| `archive_serial_number` | Archive serial number          |
| `custom_fields`         | Custom field assignments       |

### Uploading with custom fields

You can attach custom fields in two ways:

**As a list of field IDs** (Paperless assigns `null` as value):

```python
draft = paperless.documents.draft(
    document=content,
    custom_fields=[3, 8],
)
```

**As a `DocumentCustomFieldList`** (with explicit values):

```python
from pypaperless.models.documents import DocumentCustomFieldList
from pypaperless.models.custom_fields import CustomFieldValue

cf_list = DocumentCustomFieldList(paperless, data=[])
cf_list += CustomFieldValue(field=3, value="ACME Corp")
cf_list += CustomFieldValue(field=8, value=42)

draft = paperless.documents.draft(document=content, custom_fields=cf_list)
```

See [Custom fields](custom_fields.md) for the full custom field API.

---

## Monitoring upload tasks

After uploading a document, use `paperless.tasks` to check the status:

```python
task_id = await paperless.documents.save(draft)

import asyncio
for _ in range(30):
    await asyncio.sleep(2)
    task = await paperless.tasks(task_id)
    if task.status in ("SUCCESS", "FAILURE"):
        break

print(task.status, task.result)
```

---

## Sending documents by e-mail

You can send one or more documents as attachments to one or more e-mail addresses:

```python
await paperless.documents.email(
    [23, 42],
    addresses="alice@example.com, bob@example.com",
    subject="Your requested documents",
    message="Please find the documents attached.",
)
```

A single document can also be passed as an integer:

```python
await paperless.documents.email(
    42,
    addresses="alice@example.com",
    subject="Invoice",
    message="See attachment.",
    use_archive_version=False,  # send original instead of archived version
)
```

| Parameter             | Default | Description                                 |
| --------------------- | ------- | ------------------------------------------- |
| `documents`           | —       | Document ID(s) to send                      |
| `addresses`           | —       | Comma-separated recipient e-mail addresses  |
| `subject`             | —       | E-mail subject                              |
| `message`             | —       | E-mail body text                            |
| `use_archive_version` | `True`  | Send archived version; `False` for original |

Raises `SendEmailError` if the Paperless server rejects the request.

---

## Audit history

Every change to a document is recorded as an audit-log entry. Use `document.history()` or the service directly to retrieve the full history of a document.

```python
# Via a fetched document (document pk is bound automatically)
doc = await paperless.documents(42)
entries = await doc.history()

for entry in entries:
    print(entry.timestamp, entry.action, entry.actor.username if entry.actor else "—")
    print(entry.changes)   # dict of changed fields

# Via the service, passing the document pk explicitly
entries = await paperless.documents.history(42)
```

### `DocumentHistory` fields

| Field       | Description                                           |
| ----------- | ----------------------------------------------------- |
| `id`        | Entry id                                              |
| `document`  | Document pk (injected by the service layer)           |
| `timestamp` | When the change occurred                              |
| `action`    | `"create"` or `"update"` (`DocumentHistoryAction`)    |
| `changes`   | Dict mapping field names to `[old, new]` pairs        |
| `actor`     | The user who made the change (`DocumentHistoryActor`) |

### `DocumentHistoryActor` fields

| Field      | Description     |
| ---------- | --------------- |
| `id`       | User id         |
| `username` | Username string |
