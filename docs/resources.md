# Resources

Every Paperless-ngx entity is exposed through a **service** on the `Paperless` instance. Each service supports a consistent set of operations — fetch, iterate, create, update or delete.

---

## Capability matrix

| Resource         | `call` | `iterate` | `draft`/`save` | `update` | `delete` | `permissions` |
| ---------------- | :----: | :-------: | :------------: | :------: | :------: | :-----------: |
| `config`         |   ✓    |           |                |          |          |               |
| `correspondents` |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |       ✓       |
| `custom_fields`  |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |               |
| `documents`      |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |       ✓       |
| `document_types` |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |       ✓       |
| `groups`         |   ✓    |     ✓     |                |          |          |               |
| `mail_accounts`  |   ✓    |     ✓     |                |          |          |       ✓       |
| `mail_rules`     |   ✓    |     ✓     |                |          |          |       ✓       |
| `processed_mail` |   ✓    |     ✓     |                |          |          |       ✓       |
| `saved_views`    |   ✓    |     ✓     |                |          |          |       ✓       |
| `share_links`    |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |               |
| `statistics`     |   ✓    |           |                |          |          |               |
| `remote_version` |   ✓    |           |                |          |          |               |
| `status`         |   ✓    |           |                |          |          |               |
| `storage_paths`  |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |       ✓       |
| `tags`           |   ✓    |     ✓     |       ✓        |    ✓     |    ✓     |       ✓       |
| `tasks`          |   ✓    |     ✓     |                |          |          |               |
| `users`          |   ✓    |     ✓     |                |          |          |               |
| `workflows`      |   ✓    |     ✓     |                |          |          |               |

---

## Fetching a single item

Call the service with a primary key to retrieve one item:

```python
document = await paperless.documents(42)
correspondent = await paperless.correspondents(7)
tag = await paperless.tags(3)
```

### Lazy loading

Pass `lazy=True` to create a model instance without making any HTTP request. Useful when you only need the primary key reference:

```python
doc = await paperless.documents(42, lazy=True)
# doc.id == 42, but no data was fetched
```

---

## Iterating over all items

Use `async for` to iterate over every item in a resource. pypaperless handles pagination automatically:

```python
async for correspondent in paperless.correspondents:
    print(correspondent.id, correspondent.name)

async for tag in paperless.tags:
    print(tag.name, tag.colour)
```

### Getting all primary keys

To retrieve a flat list of all primary keys without fetching full model data:

```python
all_ids: list[int] = await paperless.documents.all()
```

### Pagination

You can iterate page-by-page instead of item-by-item:

```python
async for page in paperless.documents.pages():
    print(f"Page has {len(page)} documents")
    for doc in page:
        print(doc.title)
```

Control the starting page:

```python
async for page in paperless.documents.pages(page=3):
    ...
```

---

## Filtering with `reduce()`

`reduce()` is an async context manager that applies server-side filters to iteration. Any Paperless-ngx API filter parameter is accepted.

```python
async with paperless.documents.reduce(title__icontains="invoice"):
    async for document in paperless.documents:
        print(document.title)
```

You can combine multiple filters and control pagination:

```python
filters = {
    "page_size": 50,
    "correspondent__id": 3,
    "title__icontains": "2024",
}

async with paperless.documents.reduce(**filters):
    async for document in paperless.documents:
        ...
```

The filter context is automatically cleared when the `async with` block exits.

---

## Creating items

Use `draft()` to create a new draft model and `save()` to persist it:

```python
# Create a new tag
draft = paperless.tags.draft(name="important", colour="#ff0000")
new_id = await paperless.tags.save(draft)
print(f"Created tag with id {new_id}")
```

```python
# Create a new correspondent
draft = paperless.correspondents.draft(name="ACME Corp")
new_id = await paperless.correspondents.save(draft)
```

!!! note
    `save()` returns the integer `id` of the created resource for most resource types, or a `task_id` string when uploading a document.

For required fields, see the model reference in the source code. If required fields are missing, `DraftFieldRequiredError` is raised.

---

## Updating items

Modify fields on a fetched model and call `update()`:

```python
tag = await paperless.tags(3)
tag.name = "urgent"
tag.colour = "#ff0000"

updated = await paperless.tags.update(tag)
print(f"Updated: {updated}")  # True if any field changed
```

`update()` returns `True` if any field was changed and sent to the API, `False` if no fields differed from the stored state. The model is refreshed in-place after a successful update.

By default, only changed fields are sent via `PATCH`. Pass `only_changed=False` to replace all fields via `PUT`:

```python
await paperless.tags.update(tag, only_changed=False)
```

---

## Deleting items

```python
tag = await paperless.tags(3)

if await paperless.tags.delete(tag):
    print("Tag deleted successfully.")
```

`delete()` returns `True` when the deletion was successful (HTTP 204), `False` otherwise.

---

## Model fields: matching & algorithms

Resources like `Correspondent`, `Tag`, `DocumentType` and `StoragePath` include matching fields inherited from `MatchingFieldsMixin`:

| Field                | Description                |
| -------------------- | -------------------------- |
| `match`              | The matching pattern       |
| `matching_algorithm` | How the pattern is applied |
| `is_insensitive`     | Case-insensitive matching  |

**`MatchingAlgorithm` values:**

| Value         | Meaning                       |
| ------------- | ----------------------------- |
| `NONE` (0)    | No automatic matching         |
| `ANY` (1)     | Match any word                |
| `ALL` (2)     | Match all words               |
| `LITERAL` (3) | Exact literal match           |
| `REGEX` (4)   | Regular expression            |
| `FUZZY` (5)   | Fuzzy matching                |
| `AUTO` (6)    | Automatic (Paperless decides) |
