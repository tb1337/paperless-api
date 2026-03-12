# Tags

Tags are labels that can be applied to documents for classification and filtering. They support the full CRUD lifecycle and permission management.

## Models

### `Tag`

| Field            | Description                           |
| ---------------- | ------------------------------------- |
| `id`             | Primary key                           |
| `slug`           | URL-safe identifier                   |
| `name`           | Display name                          |
| `color`          | Hex color string (e.g. `"#a6cee3"`)   |
| `text_color`     | Text color for contrast               |
| `is_inbox_tag`   | Whether this is the inbox tag         |
| `document_count` | Number of documents with this tag     |
| `parent`         | Parent tag id (for hierarchical tags) |
| `children`       | Child tags                            |

### `TagDraft`

| Field          | Description                            |
| -------------- | -------------------------------------- |
| `name`         | Display name *(required on save)*      |
| `color`        | Hex color string *(required on save)*  |
| `text_color`   | Text color                             |
| `is_inbox_tag` | Mark as inbox tag *(required on save)* |
| `parent`       | Parent tag id                          |
| `owner`        | Owner user id                          |

## Fetch one

```python
tag = await paperless.tags(5)
print(tag.name)            # "Invoice"
print(tag.color)           # "#a6cee3"
print(tag.document_count)  # 38
```

## Iterate

```python
async for tag in paperless.tags:
    print(tag.id, tag.name, tag.color)

# Name → id lookup
tag_map = {t.name: t.id async for t in paperless.tags.reduce()}

# Find the inbox tag
inbox = next(
    (t async for t in paperless.tags.reduce() if t.is_inbox_tag),
    None,
)
```

## Create

```python
draft = paperless.tags.draft()
draft.name = "Invoice"
draft.color = "#a6cee3"
draft.is_inbox_tag = False

pk = await paperless.tags.save(draft)
print(pk)  # primary key of the new tag
```

## Update

```python
tag = await paperless.tags(5)
tag.color = "#ff0000"
changed = await paperless.tags.update(tag)
```

## Delete

```python
tag = await paperless.tags(5)
deleted = await paperless.tags.delete(tag)
```

## Permissions

```python
paperless.tags.request_permissions = True
tag = await paperless.tags(5)

print(tag.owner)        # owner user id
print(tag.permissions)  # PermissionTable

paperless.tags.request_permissions = False
```

See [Permissions](../concepts/permissions.md) for details.
