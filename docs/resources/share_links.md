# Share Links

Share links create publicly accessible URLs for individual documents without requiring authentication. They support the full CRUD lifecycle.

## Models

### `ShareLink`

| Field          | Description                               |
| -------------- | ----------------------------------------- |
| `id`           | Primary key                               |
| `created`      | Creation timestamp                        |
| `expiration`   | Expiry timestamp (`None` = never expires) |
| `slug`         | URL slug included in the public link      |
| `document`     | Associated document id                    |
| `file_version` | Which file version to share               |

### `ShareLinkDraft`

| Field          | Description                       |
| -------------- | --------------------------------- |
| `document`     | Document id *(required on save)*  |
| `file_version` | File version *(required on save)* |
| `expiration`   | Optional expiry timestamp         |

**`ShareLinkFileVersion` values:** `"archive"`, `"original"`

## Fetch one

```python
link = await paperless.share_links(8)
print(link.slug)       # "abc123xyz"
print(link.document)   # 42
print(link.expiration) # datetime(2024, 12, 31, ...) or None
```

## Iterate

```python
async for link in paperless.share_links:
    print(link.id, link.document, link.slug)

# Find links for a specific document
doc_links = [
    lnk async for lnk in paperless.share_links.filter()
    if lnk.document == 42
]
```

## Create

```python
import datetime
from pypaperless.models.share_links import ShareLinkFileVersion

draft = paperless.share_links.draft()
draft.document = 42
draft.file_version = ShareLinkFileVersion.ARCHIVE
draft.expiration = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

slug = await paperless.share_links.save(draft)
print(slug)  # "abc123xyz"  (str, not an int)
```

!!! note
    `save()` returns the link's `slug` string, not an integer primary key.

## Update

```python
import datetime

link = await paperless.share_links(8)
link.expiration = datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc)
changed = await paperless.share_links.update(link)
```

## Delete

```python
link = await paperless.share_links(8)
deleted = await paperless.share_links.delete(link)
```
