# Documents

Documents are the core resource in Paperless-ngx. This page shows the essential CRUD examples. For the full feature set — downloading, searching, notes, next ASN, email, and upload — see the dedicated [Documents](../concepts/documents.md) page.

## Models

See [`pypaperless/models/documents.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/documents.py) for all fields and types, and the [Paperless-ngx API docs](https://docs.paperless-ngx.com/api/) for the upstream schema.

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
    To filter documents by custom field values, see [Custom Field Query](../concepts/custom_field_query.md).
