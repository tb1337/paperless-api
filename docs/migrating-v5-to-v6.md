# Migrating from v5 to v6

## Python version requirement raised to 3.13

v6 drops support for **Python 3.12**. The minimum required version is now **Python 3.13**.

If you are still on Python 3.12, upgrade your runtime before updating pypaperless to v6.

---

v6 is also almost a full rewrite of pypaperless. Three things drove it:

- **Models were too tightly coupled to the HTTP layer.** In v5, every model instance carried a reference to the client and called it directly. That made testing awkward and sharing models between contexts impossible. v6 models are plain data — all I/O goes through services.
- **No runtime type safety.** v5 used dataclasses with manual dict conversion, so bad API responses would silently produce wrong values. v6 uses Pydantic v2, which validates every response at parse time.
- **`aiohttp` got removed.** `httpx` is modern, has a cleaner sync/async API and a built-in mock transport that makes testing easier.

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
| 10  | Rename four `Paperless`-prefixed exception classes                         | [Error handling](#error-handling)                                             |

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

In v5, CRUD operations lived on model instances. v6 moves the canonical API to
the **service** level, but also re-adds **shortcuts** on the model
instances themselves for convenience (see below).

### update()

=== "v5"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await doc.update()
    ```

=== "v6 – service (canonical)"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await paperless.documents.update(doc)
    ```

=== "v6 – model shortcut"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await doc.update()          # delegates to the service
    ```

### delete()

=== "v5"
    ```python
    doc = await paperless.documents(42)
    await doc.delete()
    ```

=== "v6 – service (canonical)"
    ```python
    doc = await paperless.documents(42)
    await paperless.documents.delete(doc)
    ```

=== "v6 – model shortcut"
    ```python
    doc = await paperless.documents(42)
    await doc.delete()          # delegates to the service
    ```

This applies to every resource — correspondents, tags, custom fields, etc.

### save() — creating new resources

=== "v5"
    ```python
    draft = paperless.documents.draft(document=raw_bytes, title="Invoice")
    pk = await draft.save()
    ```

=== "v6 – service (canonical)"
    ```python
    draft = paperless.documents.create(document=raw_bytes, title="Invoice")
    task_id = await paperless.documents.save(draft)
    ```

=== "v6 – model shortcut"
    ```python
    draft = paperless.documents.create(document=raw_bytes, title="Invoice")
    task_id = await draft.save()    # delegates to the service
    ```

For all other resources (correspondents, tags, …):

=== "v5"
    ```python
    draft = paperless.tags.draft(name="urgent")
    pk = await draft.save()
    ```

=== "v6 – service (canonical)"
    ```python
    draft = paperless.tags.create(name="urgent")
    pk = await paperless.tags.save(draft)
    ```

=== "v6 – model shortcut"
    ```python
    draft = paperless.tags.create(name="urgent")
    pk = await draft.save()         # delegates to the service
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
    draft = paperless.documents.notes.create(note="Checked.", document=42)
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

### Exception renames

Four exception classes lost their `Paperless` prefix to follow standard Python naming conventions. `PaperlessConnectionError` is the only exception kept as-is, because it would otherwise shadow Python's built-in `ConnectionError`.

| v5                                | v6                       |
| --------------------------------- | ------------------------ |
| `PaperlessAuthError`              | `AuthError`              |
| `PaperlessInvalidTokenError`      | `InvalidTokenError`      |
| `PaperlessInactiveOrDeletedError` | `InactiveOrDeletedError` |
| `PaperlessForbiddenError`         | `ForbiddenError`         |

=== "v5"
    ```python
    from pypaperless.exceptions import PaperlessAuthError, PaperlessForbiddenError

    except PaperlessAuthError:
        ...
    except PaperlessForbiddenError:
        ...
    ```

=== "v6"
    ```python
    from pypaperless.exceptions import AuthError, ForbiddenError

    except AuthError:
        ...
    except ForbiddenError:
        ...
    ```

### New exception base classes

v6 introduces intermediate base classes that you can use to catch whole groups of related errors:

| Class                 | Catches                                                             |
| --------------------- | ------------------------------------------------------------------- |
| `InitializationError` | All session/transport errors (unchanged from v5)                    |
| `ResponseError`       | `BadJsonResponseError`, `JsonResponseWithError`                     |
| `DraftError`          | `DraftFieldRequiredError`, `DraftNotSupportedError`                 |
| `ResourceError`       | `ItemNotFoundError`, `PrimaryKeyRequiredError`, `TaskNotFoundError` |
| `DocumentError`       | `AsnRequestError`, `SendEmailError`                                 |
