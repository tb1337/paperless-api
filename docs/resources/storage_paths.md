# Storage Paths

Storage paths define directory templates that control where Paperless-ngx stores archived documents on disk. They support the full CRUD lifecycle and permission management.

## Models

### `StoragePath`

| Field            | Description                         |
| ---------------- | ----------------------------------- |
| `id`             | Primary key                         |
| `slug`           | URL-safe identifier                 |
| `name`           | Display name                        |
| `path`           | Directory path template             |
| `document_count` | Number of documents using this path |

### `StoragePathDraft`

| Field   | Description                                                                 |
| ------- | --------------------------------------------------------------------------- |
| `name`  | Display name *(required on save)*                                           |
| `path`  | Path template, e.g. `"{created_year}/{correspondent}"` *(required on save)* |
| `owner` | Owner user id                                                               |

## Fetch one

```python
sp = await paperless.storage_paths(2)
print(sp.name)  # "By year"
print(sp.path)  # "{created_year}/{correspondent}/{title}"
```

## Iterate

```python
async for sp in paperless.storage_paths:
    print(sp.id, sp.name, sp.path)

# Build a name → path mapping
path_map = {sp.name: sp.path async for sp in paperless.storage_paths.reduce()}
```

## Create

```python
draft = paperless.storage_paths.draft()
draft.name = "By year and type"
draft.path = "{created_year}/{document_type}/{title}"

pk = await paperless.storage_paths.save(draft)
print(pk)  # primary key of the new storage path
```

## Update

```python
sp = await paperless.storage_paths(2)
sp.path = "{created_year}/{correspondent}/{title}"
changed = await paperless.storage_paths.update(sp)
```

## Delete

```python
sp = await paperless.storage_paths(2)
deleted = await paperless.storage_paths.delete(sp)
```

## Permissions

```python
async with paperless.storage_paths.with_permissions():
    sp = await paperless.storage_paths(2)
    print(sp.owner)        # owner user id
    print(sp.permissions)  # Permissions
```

See [Permissions](../concepts/permissions.md) for details.
