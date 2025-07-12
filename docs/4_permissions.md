# Permissions

Some resources of *Paperless-ngx* support retrieving and updating of object-level permissions. They are tricky, so here is little guidance for handling them.

## Documentation

* [Basic Usage](1_basic_usage.md)
* [Working with documents](2_documents.md)
* [Working with custom fields](3_custom_fields.md)
* [Permissions](4_permissions.md) - This page ;)

---

**On this page:**

- [About permissions in **pypaperless**](#about-permissions-in-pypaperless)
- [Toggle requesting](#toggle-requesting)
- [Create item with permissions](#create-item-with-permissions)
- [Update permissions](#update-permissions)

## About permissions in **pypaperless**

At the moment, **pypaperless** provides only minimal support for permissions. Due to the way *Paperless-ngx* implements and exposes object-level permissions via the Django API, it’s hard to envision practical use cases for managing them automatically.

> [!CAUTION]
> The permission model is subject to change in the future, when I feel the need for it.

## Toggle requesting

When requesting data from *Paperless-ngx*, it delivers two permission fields by default: `owner` and `user_can_change`.

You have to explicitly call the API to return the permissions table by enabling that feature. To do so, you have to enable it one by one for each resource in **pypaperless**.

```python
paperless.documents.request_permissions = True

document = await paperless.documents(23)

print(document.has_permissions)
#-> True
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/23/?full_perms=true`

Requesting permissions stays enabled until it gets disabled again.

```python
paperless.documents.request_permissions = False

document = await paperless.documents(23)

print(document.has_permissions)
#-> False
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/23/`

## Create item with permissions

When creating new resource items, you can apply permissions by setting a `PermissionTableType` to the optional `set_permissions` field.

> [!WARNING]
> Both `PermissionTableType` and `PermissionSetType` automatically initialize empty lists for their fields unless you provided a value.

```python
from pypaperless.models.common import PermissionSetType, PermissionTableType

draft = paperless.correspondents.draft()

draft.name = "Correspondent with perms"
draft.set_permissions = PermissionTableType(
    view=PermissionSetType(
        users=[23],
    ),
)
# ...
```

## Update permissions

If you want to change permissions of a resource item, you have to enable requesting them before fetching it. The `permissions` field gets available then, ready for modifications.

```python
paperless.documents.request_permissions = True
document = await paperless.documents(23)

if document.has_permissions:
    document.permissions.view.users.append(5)
    await document.update()
```

> [!NOTE]
> Executed http requests: <br>
> `PATCH` `https://localhost:8000/api/documents/23/?full_perms=true`
