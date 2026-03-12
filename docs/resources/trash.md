# Trash

The `trash` resource exposes documents that have been soft-deleted in Paperless-ngx. Trashed documents can be restored or permanently deleted. The service iterates over `Document` objects just like the main `documents` service.

## Model

Trashed documents use the same `Document` model. The only additional field populated in the trash context is:

| Field        | Description                                        |
| ------------ | -------------------------------------------------- |
| `deleted_at` | Timestamp when the document was moved to the trash |

All other `Document` fields are present as usual.

## Iterate

```python
async for doc in paperless.trash:
    print(doc.id, doc.title, doc.deleted_at)

# Collect all trashed documents as a list
trashed = await paperless.trash.as_list()
print(f"{len(trashed)} document(s) in trash")
```

## Restore

Restore one or more documents back to the document archive:

```python
await paperless.trash.restore([42, 43])
```

## Empty

Permanently delete documents from the trash. Pass a list of IDs to delete specific documents, or call without arguments to empty the entire trash:

```python
# Delete specific documents permanently
await paperless.trash.empty([42, 43])

# Empty the entire trash
await paperless.trash.empty()
```

!!! warning
    `empty()` permanently destroys documents. This action cannot be undone.
