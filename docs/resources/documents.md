# Documents

Documents are the core resource in Paperless-ngx. This page shows the essential CRUD examples. For the full feature set - downloading, searching, notes, next ASN, email, and upload - see the dedicated [Documents](../concepts/documents.md) page.

## Models

See [`pypaperless/models/documents/document.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/documents/document.py) for all fields and [`pypaperless/models/types.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/types.py) for enum and filter types, and the [Paperless-ngx API docs](https://docs.paperless-ngx.com/api/) for the upstream schema.

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

draft = paperless.documents.create()
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

## Shortcuts

Model instances expose `update()` and `delete()` directly; draft instances expose `save()`:

```python
doc = await paperless.documents(42)
doc.title = "Updated title"
changed = await doc.update()

await doc.delete()

# Draft.save() returns a task UUID, same as paperless.documents.save(draft)
draft = paperless.documents.create()
draft.title = "Invoice 2024"
draft.document = raw_bytes
task_id = await draft.save()
```

Document instances also expose shortcuts for the sub-resource operations:

```python
doc = await paperless.documents(42)

# file access
downloaded = await doc.download()
preview    = await doc.preview()
thumb      = await doc.thumbnail()

# metadata and suggestions
meta        = await doc.metadata()
suggestions = await doc.suggestions()

# similar documents (async generator)
async for similar in doc.more_like():
    print(similar.title)

# send by e-mail
await doc.email(
    addresses="alice@example.com",
    subject="Invoice",
    message="See attachment.",
)

# notes, history, and share links (bound sub-services)
notes   = await doc.notes()           # list[DocumentNote]
entries = await doc.history()         # list[DocumentHistory]
links   = await doc.share_links()     # list[ShareLink]
note_draft = doc.notes.create(note="Checked.")
await doc.notes.save(note_draft)
await note_draft.save()               # same, as a draft shortcut
await notes[0].delete()               # note instance shortcut
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
