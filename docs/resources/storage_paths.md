# Storage Paths

Storage paths define directory templates that control where Paperless-ngx stores archived documents on disk. They support the full CRUD lifecycle and permission management.

## Models

See [`pypaperless/models/storage_paths.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/storage_paths.py) for all fields and [`pypaperless/models/types.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/types.py) for enum and filter types, and the [Paperless-ngx API docs](https://docs.paperless-ngx.com/api/) for the upstream schema.

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

# Keyed by id
paths = await paperless.storage_paths.as_dict()
```

## Create

```python
draft = paperless.storage_paths.create()
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

## Shortcuts

Model instances expose `update()` and `delete()` directly; draft instances expose `save()`:

```python
sp = await paperless.storage_paths(2)
sp.path = "{created_year}/{correspondent}/{title}"
changed = await sp.update()

await sp.delete()

draft = paperless.storage_paths.create(name="Archive", path="{created_year}/{title}")
pk = await draft.save()
```

## Permissions

```python
async with paperless.storage_paths.with_permissions():
    sp = await paperless.storage_paths(2)
    print(sp.owner)        # owner user id
    print(sp.permissions)  # Permissions
```

See [Permissions](../concepts/permissions.md) for details.
