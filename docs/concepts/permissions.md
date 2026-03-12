# Permissions

Paperless-ngx supports **object-level permissions** — some resources can have explicit `view` and `change` permissions assigned to individual users or groups.

---

## Resources that support permissions

The following resources include permission fields (`SecurableMixin`):

- `documents`
- `correspondents`
- `document_types`
- `storage_paths`
- `tags`

---

## Permission fields on a model

When permissions are loaded, a `Document` (or other securable model) exposes:

| Field             | Description                                  |
| ----------------- | -------------------------------------------- |
| `owner`           | User ID of the owner                         |
| `user_can_change` | Whether the current user can change the item |
| `permissions`     | Full permission table                        |

```python
doc = await paperless.documents(42)

print(doc.owner)
print(doc.user_can_change)

if doc.has_permissions:
    print(doc.permissions.view.users)   # list[int]
    print(doc.permissions.view.groups)  # list[int]
    print(doc.permissions.change.users)
    print(doc.permissions.change.groups)
```

!!! note
    `doc.permissions` is `None` unless you explicitly request the full permissions (see below).

---

## Requesting permissions alongside data

By default, Paperless-ngx does not include the full permission table in responses. Enable it by setting `request_permissions = True` on the service:

```python
# Enable full permissions for all subsequent requests on this service
paperless.documents.request_permissions = True

doc = await paperless.documents(42)
print(doc.permissions)

async for doc in paperless.documents:
    print(doc.owner, doc.permissions)

# Disable again when no longer needed
paperless.documents.request_permissions = False
```

The `request_permissions` flag can be toggled at any time and applies to all methods on the service (`__call__`, iteration, `update()`) until it is reset.

Alternatively, use a `reduce()` context with the `full_perms` parameter:

```python
async with paperless.documents.reduce(full_perms="true"):
    async for doc in paperless.documents:
        print(doc.permissions)
```

---

## Creating an item with permissions

When drafting a new item, use `set_permissions` to assign ownership and ACLs at creation time (`SecurableDraftMixin`):

```python
from pypaperless.models.mixins.securable import PermissionTable, PermissionSet

perms = PermissionTable(
    view=PermissionSet(users=[2, 3], groups=[]),
    change=PermissionSet(users=[2], groups=[1]),
)

draft = paperless.tags.draft(
    name="confidential",
    owner=1,
    set_permissions=perms,
)

new_id = await paperless.tags.save(draft)
```

---

## Updating permissions on an existing item

Fetch the item, modify the `permissions` field, then call `update()`:

```python
from pypaperless.models.mixins.securable import PermissionTable, PermissionSet

doc = await paperless.documents(42)

doc.permissions = PermissionTable(
    view=PermissionSet(users=[2, 3], groups=[]),
    change=PermissionSet(users=[2], groups=[]),
)
doc.owner = 1

await paperless.documents.update(doc)
```

---

## `PermissionTable` and `PermissionSet`

```python
class PermissionSet:
    users: list[int]   # user IDs
    groups: list[int]  # group IDs

class PermissionTable:
    view: PermissionSet
    change: PermissionSet
```

---

## Listing users and groups

To populate permission assignments, you can enumerate users and groups:

```python
async for user in paperless.users:
    print(user.id, user.username)

async for group in paperless.groups:
    print(group.id, group.name)
```
