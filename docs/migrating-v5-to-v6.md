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

| #   | What to change                                                                                                  | Section                                                                       |
| --- | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 1   | Replace `aiohttp` / `yarl` with `httpx`                                                                         | [Dependencies](#dependencies)                                                 |
| 2   | Update `Paperless(...)` constructor arguments; new: `PaperlessConfig` and env vars                              | [Initializing the client](#initializing-the-client)                           |
| 3   | Replace `reduce()` with `filter()` — different call pattern                                                     | [Iteration and filtering](#iteration-and-filtering)                           |
| 4   | `draft()` renamed to `create()`; `update()`, `delete()`, `save()` moved to services — shortcuts still on models | [CRUD](#crud)                                                                 |
| 5   | Replace `request_permissions = True` with `with_permissions()`                                                  | [Permissions](#permissions)                                                   |
| 6   | Rename `doc.get_download()`, `doc.get_metadata()`, etc. — shortcuts are back                                    | [Document convenience methods renamed](#document-convenience-methods-renamed) |
| 7   | Note deletion: `note.delete()` → service call                                                                   | [Document notes](#document-notes)                                             |
| 8   | `generate_api_token()` custom-client argument renamed                                                           | [Token generation](#token-generation)                                         |
| 9   | New: `paperless.profile`, `paperless.trash`, `paperless.documents.history`                                      | [New resources](#new-resources)                                               |
| 10  | Rename four `Paperless`-prefixed exception classes                                                              | [Error handling](#error-handling)                                             |

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
    ```

!!! tip "SSL / TLS customization"
    Pass a pre-configured `httpx.AsyncClient` to control TLS behaviour:
    ```python
    client = httpx.AsyncClient(verify=False)  # or verify="/path/to/cert.pem"
    paperless = Paperless("http://localhost:8000", "mytoken", client=client)
    ```

The `url` parameter no longer accepts `yarl.URL` objects — pass a plain string.

### New: `PaperlessConfig` and environment variables

v6 adds two additional initialization modes via the new `PaperlessConfig` class (backed by `pydantic-settings`):

**Config object** — useful when you want to construct or validate settings in one place:

```python
from pypaperless import Paperless, PaperlessConfig

cfg = PaperlessConfig(url="http://localhost:8000", token="mytoken")
paperless = Paperless(config=cfg)
```

**Environment variables** — pass no arguments at all; `PaperlessConfig` reads the values automatically:

```python
paperless = Paperless()
```

| Environment variable              | Maps to                           |
| --------------------------------- | --------------------------------- |
| `PYPAPERLESS_URL`                 | URL of the Paperless-ngx instance |
| `PYPAPERLESS_TOKEN`               | API token                         |
| `PYPAPERLESS_REQUEST_API_VERSION` | API version header (optional)     |

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

## CRUD

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

=== "v6"
    ```python
    doc = await paperless.documents(42)
    doc.title = "New Title"
    await doc.update()
    ```

=== "v6 (service)"
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
    await doc.delete()
    ```

=== "v6 (service)"
    ```python
    doc = await paperless.documents(42)
    await paperless.documents.delete(doc)
    ```

This applies to every resource — correspondents, tags, custom fields, etc.

### save()

`draft()` was renamed to `create()`. The call signature is otherwise identical.

=== "v5"
    ```python
    draft = paperless.documents.draft(document=raw_bytes, title="Invoice")
    task_id = await draft.save()
    ```

=== "v6"
    ```python
    draft = paperless.documents.create(document=raw_bytes, title="Invoice")
    task_id = await draft.save()
    ```

=== "v6 (service)"
    ```python
    draft = paperless.documents.create(document=raw_bytes, title="Invoice")
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
    draft = paperless.tags.create(name="urgent")
    pk = await draft.save()
    ```

=== "v6 (service)"
    ```python
    draft = paperless.tags.create(name="urgent")
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
    paperless.documents.request_permissions = False
    ```

=== "v6"
    ```python
    async with paperless.documents.with_permissions() as ctx:
        doc = await ctx(42)
        print(doc.owner, doc.permissions)
        async for doc in ctx:
            print(doc.owner, doc.permissions)
    ```

!!! note
    Unlike v5, `with_permissions()` resets it automatically on exit, even if an exception occurs.

---

## Document convenience methods renamed

The `get_*` shortcut methods on `Document` instances were renamed. The canonical API lives on the service, but the model shortcuts are still available:

| v5 (on model instance)                  | v6 shortcut                         | v6                                                          |
| --------------------------------------- | ----------------------------------- | ----------------------------------------------------------- |
| `await doc.get_download()`              | `await doc.download()`              | `await paperless.documents.download(doc.id)`                |
| `await doc.get_download(original=True)` | `await doc.download(original=True)` | `await paperless.documents.download(doc.id, original=True)` |
| `await doc.get_preview()`               | `await doc.preview()`               | `await paperless.documents.preview(doc.id)`                 |
| `await doc.get_thumbnail()`             | `await doc.thumbnail()`             | `await paperless.documents.thumbnail(doc.id)`               |
| `await doc.get_metadata()`              | `await doc.metadata()`              | `await paperless.documents.metadata(doc.id)`                |
| `await doc.get_suggestions()`           | `await doc.suggestions()`           | `await paperless.documents.suggestions(doc.id)`             |
| *(not available)*                       | `async for d in doc.more_like()`    | `async for d in paperless.documents.more_like(doc.id)`      |
| *(not available)*                       | `await doc.email(...)`              | `await paperless.documents.email(doc.id, ...)`              |
| *(not available)*                       | `notes = await doc.notes()`         | `notes = await paperless.documents.notes(doc.id)`           |
| *(not available)*                       | `entries = await doc.history()`     | `entries = await paperless.documents.history(doc.id)`       |

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
    doc = await paperless.documents(42)
    notes = await doc.notes()
    for note in notes:
        await note.delete()
    ```

=== "v6 (service)"
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
    doc = await paperless.documents(42)
    draft = doc.notes.create(note="Checked.")
    note_id, doc_id = await draft.save()
    ```

!!! note
    When using `doc.notes`, the document pk is bound automatically — no need to pass `document=` to `create()`.

=== "v6 (service)"
    ```python
    draft = paperless.documents.notes.create(42, note="Checked.")
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
await paperless.trash.empty()
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
    except PaperlessConnectionError:
        ...
    ```

!!! tip
    `PaperlessConnectionError` wraps `httpx.ConnectError` and works in both v5 and v6 — catching it is the most forward-compatible option.

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
