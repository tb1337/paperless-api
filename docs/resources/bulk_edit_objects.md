# Bulk Edit Objects

The `bulk_edit_objects` service lets you set permissions or permanently delete
multiple non-document objects - tags, correspondents, document types or storage
paths - in a single API call.

It does not support the standard CRUD lifecycle (no `call`, `iterate`, `create`,
`update`). It is a write-only bulk-action endpoint.

## Set permissions

Assign an owner and/or view/change grants to a list of objects:

```python
from pypaperless.models.types import Permissions

await paperless.bulk_edit_objects.set_permissions(
    "tags",
    [1, 2, 3],
    owner=1,
    permissions=Permissions(view_users=[2, 3], change_users=[1]),
)
```

To merge with existing permissions instead of replacing them:

```python
await paperless.bulk_edit_objects.set_permissions(
    "correspondents",
    [4, 5],
    owner=1,
    merge=True,
)
```

**Supported `object_type` values:** `"tags"`, `"correspondents"`,
`"document_types"`, `"storage_paths"`.

Parameters:

| Parameter     | Type                    | Description                                          |
| ------------- | ----------------------- | ---------------------------------------------------- |
| `object_type` | `str`                   | Resource type (see above)                            |
| `objects`     | `list[int]`             | Primary keys of objects to operate on                |
| `owner`       | `int` or `None`         | New owner user ID. `None` leaves the owner unchanged |
| `permissions` | `Permissions` or `None` | View/change grants. `None` leaves them unchanged     |
| `merge`       | `bool`                  | `True` merges; `False` (default) replaces            |

## Delete

Permanently delete a list of objects:

```python
await paperless.bulk_edit_objects.delete("correspondents", [4, 5])
await paperless.bulk_edit_objects.delete("tags", [7, 8, 9])
```

!!! warning
    This is a permanent deletion - objects cannot be recovered.

Parameters:

| Parameter     | Type        | Description                       |
| ------------- | ----------- | --------------------------------- |
| `object_type` | `str`       | Resource type (see above)         |
| `objects`     | `list[int]` | Primary keys of objects to delete |
