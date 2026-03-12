# Document Types

Document types classify documents into categories (e.g. *Invoice*, *Contract*, *Receipt*). They support the full CRUD lifecycle and permission management.

## Models

### `DocumentType`

| Field            | Description                  |
| ---------------- | ---------------------------- |
| `id`             | Primary key                  |
| `slug`           | URL-safe identifier          |
| `name`           | Display name                 |
| `document_count` | Number of assigned documents |

### `DocumentTypeDraft`

| Field   | Description                       |
| ------- | --------------------------------- |
| `name`  | Display name *(required on save)* |
| `owner` | Owner user id                     |

## Fetch one

```python
document_type = await paperless.document_types(4)
print(document_type.name)            # "Invoice"
print(document_type.document_count)  # 17
```

## Iterate

```python
async for dt in paperless.document_types:
    print(dt.id, dt.name)

# Map id → name
type_map = {dt.id: dt.name async for dt in paperless.document_types.reduce()}
```

## Create

```python
draft = paperless.document_types.draft()
draft.name = "Invoice"

pk = await paperless.document_types.save(draft)
print(pk)  # primary key of the new document type
```

## Update

```python
dt = await paperless.document_types(4)
dt.name = "Invoice (updated)"
changed = await paperless.document_types.update(dt)
```

## Delete

```python
dt = await paperless.document_types(4)
deleted = await paperless.document_types.delete(dt)
```

## Permissions

```python
paperless.document_types.request_permissions = True
dt = await paperless.document_types(4)

print(dt.owner)        # owner user id
print(dt.permissions)  # PermissionTable

paperless.document_types.request_permissions = False
```

See [Permissions](../permissions.md) for details on reading and modifying permission sets.
