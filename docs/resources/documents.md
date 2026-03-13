# Documents

Documents are the core resource in Paperless-ngx. This page shows the essential CRUD examples. For the full feature set — downloading, searching, notes, next ASN, email, and upload — see the dedicated [Documents](../concepts/documents.md) page.

## Models

### `Document` *(key fields)*

| Field           | Description                        |
| --------------- | ---------------------------------- |
| `id`            | Primary key                        |
| `title`         | Document title                     |
| `content`       | Full-text content (OCR result)     |
| `document_type` | Assigned document type id          |
| `correspondent` | Assigned correspondent id          |
| `storage_path`  | Assigned storage path id           |
| `tags`          | Assigned tag ids                   |
| `created`       | Creation date                      |
| `created_date`  | Creation date (date-only property) |
| `added`         | Date added to Paperless            |
| `asn`           | Archive serial number              |
| `custom_fields` | Custom field values                |

### `DocumentDraft`

| Field           | Description           |
| --------------- | --------------------- |
| `title`         | Document title        |
| `document_type` | Document type id      |
| `correspondent` | Correspondent id      |
| `storage_path`  | Storage path id       |
| `tags`          | Tag ids               |
| `created`       | Created date          |
| `asn`           | Archive serial number |
| `custom_fields` | Custom field values   |

## Fetch one

```python
doc = await paperless.documents(42)
print(doc.title)
print(doc.created_date)  # datetime.date
```

## Iterate

```python
async for doc in paperless.documents:
    print(doc.id, doc.title)

# All documents in memory
all_docs = await paperless.documents.as_list()
```

## Create (upload)

To upload a new document, use `draft()` + `save()`. The first positional argument to `save()` is the raw file content (`bytes`):

```python
with open("invoice.pdf", "rb") as fh:
    raw = fh.read()

draft = paperless.documents.draft()
draft.title = "Invoice 2024"
draft.correspondent = 7
draft.tags = [1, 3]

task_id = await paperless.documents.save(draft, raw)
```

`save()` returns a `str` task UUID. Monitor progress via `paperless.tasks`.

## Update

```python
doc = await paperless.documents(42)
doc.title = "Updated title"
doc.tags = [1, 2, 5]
changed = await paperless.documents.update(doc)
```

## Delete

```python
doc = await paperless.documents(42)
deleted = await paperless.documents.delete(doc)
```

## Permissions

```python
async with paperless.documents.with_permissions():
    doc = await paperless.documents(42)
    print(doc.owner)        # owner user id
    print(doc.permissions)  # Permissions
```

---

!!! note
    For downloading, searching, note management, and more, see [Documents](../concepts/documents.md).
