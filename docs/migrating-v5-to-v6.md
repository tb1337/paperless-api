# Migrating from v5 to v6

v6 is a full rewrite of pypaperless, motivated by three concrete problems with v5:

- **Tight coupling between models and the HTTP layer.** In v5, every model instance held a reference to the `Paperless` client and called it directly for `update()`, `delete()`, and `save()`. This made models hard to construct in tests and impossible to pass between different client contexts. v6 makes models pure data containers — all I/O goes through service objects.
- **Runtime type safety.** v5 used plain dataclasses with manual dict-to-object conversion. v6 uses Pydantic v2, which validates all incoming API data against the declared field types at parse time. The Pydantic team's own benchmarks show v2 parses 5–17× faster than v1 and catches malformed payloads that would previously have silently produced wrong values.
- **HTTP client ergonomics.** `aiohttp` requires an explicit session lifecycle and has no built-in sync support. `httpx` has a unified sync/async API, ships with a `MockTransport` for testing without a live server, and handles connection pooling transparently.

The changes are mechanical at call sites but the reasoning is architectural.

---

## Quick checklist

| #   | What to change                                                             | Section                                                                       |
| --- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 1   | Replace `aiohttp` / `yarl` with `httpx`                                    | [Dependencies](#dependencies)                                                 |
| 2   | Update `Paperless(...)` constructor arguments                              | [Initializing the client](#initializing-the-client)                           |
| 3   | Replace `reduce()` with `filter()` — different call pattern                | [Iteration and filtering](#iteration-and-filtering)                           |
| 4   | Move `update()`, `delete()`, `save()` from model instances to services     | [CRUD](#crud-update-delete-save)                                              |
| 5   | Replace `request_permissions = True` with `with_permissions()`             | [Permissions](#permissions)                                                   |
| 6   | Replace `doc.get_download()`, `get_metadata()`, etc.                       | [Document convenience methods removed](#document-convenience-methods-removed) |
| 7   | Note deletion: `note.delete()` → service call                              | [Document notes](#document-notes)                                             |
| 8   | `generate_api_token()` custom-client argument renamed                      | [Token generation](#token-generation)                                         |
| 9   | New: `paperless.profile`, `paperless.trash`, `paperless.documents.history` | [New resources](#new-resources)                                               |

---

## Dependencies

Replace `aiohttp` and `yarl` with `httpx`:

=== "v5"
    ```toml
    dependencies = ["aiohttp", "yarl", "pypaperless"]
    ```

=== "v6"
    ```toml
    dependencies = ["httpx", "pypaperless"]
    ```

---

## Initializing the client

The constructor signature changed. `session` was renamed to `client`, and `request_args` was removed.

=== "v5"
    ```python
    import aiohttp
    paperless = Paperless("http://localhost:8000", "mytoken")
    paperless = Paperless("http://localhost:8000", "mytoken", session=my_session)
    paperless = Paperless("http://localhost:8000", "mytoken", request_args={"ssl": False})
    ```

=== "v6"
    ```python
    import httpx
    paperless = Paperless("http://localhost:8000", "mytoken")
    paperless = Paperless("http://localhost:8000", "mytoken", client=my_httpx_client)

    # SSL / TLS customization — pass a pre-configured httpx.AsyncClient
    client = httpx.AsyncClient(verify=False)  # or verify="/path/to/cert.pem"
    paperless = Paperless("http://localhost:8000", "mytoken", client=client)
    ```

The `url` parameter no longer accepts `yarl.URL` objects — pass a plain string.

---

## Token generation

`generate_api_token()` is a static method on `Paperless`. The optional custom-client argument was renamed from `session` to `client`:

=== "v5"
    ```python
    token = await Paperless.generate_api_token(url, username, password, session=my_session)
    ```

=== "v6"
    ```python
    token = await Paperless.generate_api_token(url, username, password, client=my_client)
    ```

---

## Iteration and filtering

`reduce()` was replaced by `filter()`. The key difference: the context manager now **yields the service object**, so you iterate over `ctx` instead of reusing the outer service name.

=== "v5"
    ```python
    # reduce() mutated the helper for the duration of the block
    async with paperless.documents.reduce(title__icontains="invoice"):
        async for doc in paperless.documents:
            print(doc.title)
    ```

=== "v6"
    ```python
    async with paperless.documents.filter(title__icontains="invoice") as ctx:
        async for doc in ctx:
            print(doc.title)
    ```

The `pages()` method was removed. Use `as_list()` or iterate directly.

=== "v5"
    ```python
    async for page in paperless.documents.pages(page_size=25):
        for doc in page:
            print(doc.title)
    ```

=== "v6"
    ```python
    docs = await paperless.documents.as_list()

    async for doc in paperless.documents:
        print(doc.title)
    ```

---

## CRUD: update, delete, save

In v5, CRUD operations lived on model instances. In v6 they live on the service.

### update()

=== "v5"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await doc.update()
    ```

=== "v6"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await paperless.documents.update(doc)
    ```

### delete()

=== "v5"
    ```python
    doc = await paperless.documents(42)
    await doc.delete()
    ```

=== "v6"
    ```python
    doc = await paperless.documents(42)
    await paperless.documents.delete(doc)
    ```

This applies to every resource — correspondents, tags, custom fields, etc.

### save() — creating new resources

=== "v5"
    ```python
    draft = paperless.documents.draft(document=raw_bytes, title="Invoice")
    pk = await draft.save()
    ```

=== "v6"
    ```python
    draft = paperless.documents.draft(document=raw_bytes, title="Invoice")
    task_id = await paperless.documents.save(draft)
    ```

For all other resources (correspondents, tags, …):

=== "v5"
    ```python
    draft = paperless.tags.draft(name="urgent")
    pk = await draft.save()
    ```

=== "v6"
    ```python
    draft = paperless.tags.draft(name="urgent")
    pk = await paperless.tags.save(draft)
    ```

---

## Permissions

The mutable `request_permissions` setter was replaced by a `with_permissions()` context manager. The flag is now automatically reset on exit.

=== "v5"
    ```python
    paperless.documents.request_permissions = True
    doc = await paperless.documents(42)
    print(doc.owner, doc.permissions)
    paperless.documents.request_permissions = False  # had to reset manually
    ```

=== "v6"
    ```python
    async with paperless.documents.with_permissions() as ctx:
        doc = await ctx(42)
        print(doc.owner, doc.permissions)
        async for doc in ctx:
            print(doc.owner, doc.permissions)
    # flag is reset automatically on exit, even on exceptions
    ```

---

## Document convenience methods removed

The shortcut methods on `Document` instances that delegated back to the helper were removed. Call the service directly.

| v5 (on model instance)                  | v6 (on service)                                             |
| --------------------------------------- | ----------------------------------------------------------- |
| `await doc.get_download()`              | `await paperless.documents.download(doc.id)`                |
| `await doc.get_download(original=True)` | `await paperless.documents.download(doc.id, original=True)` |
| `await doc.get_metadata()`              | `await paperless.documents.metadata(doc.id)`                |
| `await doc.get_preview()`               | `await paperless.documents.preview(doc.id)`                 |
| `await doc.get_thumbnail()`             | `await paperless.documents.thumbnail(doc.id)`               |
| `await doc.get_suggestions()`           | `await paperless.documents.suggestions(doc.id)`             |

---

## Document notes

Note deletion moved from the model to the service, consistent with the general CRUD pattern.

=== "v5"
    ```python
    notes = await paperless.documents.notes(42)
    for note in notes:
        await note.delete()
    ```

=== "v6"
    ```python
    notes = await paperless.documents.notes(42)
    for note in notes:
        await paperless.documents.notes.delete(note)
    ```

Creating a new note:

=== "v5"
    ```python
    draft = paperless.documents.notes.draft(note="Checked.", document=42)
    note_id, doc_id = await draft.save()
    ```

=== "v6"
    ```python
    draft = paperless.documents.notes.draft(note="Checked.", document=42)
    note_id, doc_id = await paperless.documents.notes.save(draft)
    ```

---

## New resources

Two new top-level services were added.

### `paperless.profile`

Access the currently authenticated user's own profile:

```python
profile = await paperless.profile()
print(profile.username, profile.email)
```

See [Profile](resources/profile.md) for details.

### `paperless.trash`

Browse and manage soft-deleted documents:

```python
async for doc in paperless.trash:
    print(doc.id, doc.title, doc.deleted_at)

await paperless.trash.restore([42, 43])
await paperless.trash.empty()   # empties entire trash
```

The `Document.is_deleted` property returns `True` for documents retrieved from the trash.

See [Trash](resources/trash.md) for details.

### `paperless.documents.history`

A new document audit-log sub-service:

```python
entries = await paperless.documents.history(42)
for entry in entries:
    print(entry.actor, entry.timestamp, entry.action)
```

---

## Error handling

`PaperlessConnectionError` is now raised for `httpx.ConnectError` rather than `aiohttp.ClientConnectorError`. If you catch library-specific exceptions, update accordingly:

=== "v5"
    ```python
    except aiohttp.ClientConnectorError:
        ...
    ```

=== "v6"
    ```python
    except httpx.ConnectError:
        ...
    # or catch the pypaperless wrapper (works in both v5 and v6)
    except PaperlessConnectionError:
        ...
    ```
```
