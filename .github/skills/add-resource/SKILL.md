---
name: add-resource
description: "Add a new Paperless-ngx API resource to pypaperless. Use when implementing a new endpoint, service, model, or sub-service (e.g. /api/trash/, /api/documents/{id}/history/). Covers model definition, service class, const.py wiring, client registration, test fixtures, unit tests, script/pngx_audit_coverage.py, and script/pngx_smoketest.py."
argument-hint: "Name or path of the endpoint to implement (e.g. /api/trash/)"
---

# Add a New Resource to pypaperless

## When to Use

- Implementing a new top-level endpoint (e.g. `/api/trash/`)
- Implementing a document sub-service (e.g. `/api/documents/{id}/history/`)
- Any time a `/api/...` path is listed as "unimplemented" in `script/pngx_audit_coverage.py`

## Decision Tree

Before starting, answer these questions:

| Question                                                          | →                                                                                                     |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Is it a sub-resource of `/api/documents/{id}/...`?                | → **Document sub-service** (see [Sub-service pattern](./references/patterns.md#document-sub-service)) |
| Does GET return `{ count, next, previous, all, results }`?        | → **Paginated** (`IterableMixin`, `PageGenerator`)                                                    |
| Does GET return a flat list `[...]`?                              | → **Flat list** (direct `request_json` + list comprehension)                                          |
| Does GET return a single object (not a list)?                     | → **Direct** (`CallableMixin` only, no `IterableMixin`)                                               |
| Does the endpoint have POST/action methods (e.g. restore, empty)? | → Add explicit `async def` methods calling `self._client.request("post", ...)`                        |

## Step-by-Step Procedure

### 1. Research the Endpoint

```bash
source /home/vscode/.local/dev-venv/bin/activate
# Inspect live response
curl -s http://172.17.0.1:8000/api/<endpoint>/ \
  -H "Authorization: Token 3e9505078d32d8ad4ecea00fa0eec8e426622b52" | python3 -m json.tool | head -60
# Check OpenAPI schema component
python3 -c "
import httpx, json
r = httpx.get('http://172.17.0.1:8000/api/schema/?format=json',
    headers={'Authorization': 'Token 3e9505078d32d8ad4ecea00fa0eec8e426622b52'})
s = r.json()
# Replace 'ComponentName' with the schema component name
print(json.dumps(s['components']['schemas'].get('ComponentName', {}), indent=2))
"
```

### 2. `pypaperless/const.py`

Add a string constant, an `API_PATH` entry, and a `PaperlessResource` enum value:

```python
# String constant (alphabetical order)
TRASH = "trash"

# API_PATH dict entry
f"{TRASH}": f"/api/{TRASH}/",

# PaperlessResource enum
TRASH = TRASH
```

For document sub-services, add only an `API_PATH` entry (no new resource constant needed):

```python
f"{DOCUMENTS}_history": f"/api/{DOCUMENTS}/{{pk}}/history/",
```

### 3. Model (`pypaperless/models/<name>.py` or into `documents.py`)

See [model templates](./references/patterns.md#model-templates) for full code examples.

- Inherit from `PaperlessModel`
- Set `_api_path: ClassVar[str] = API_PATH["<key>"]`
- All fields `Optional` (use `| None = None`)
- Use `datetime.datetime | None` for timestamps
- Use `StrEnum` subclasses for typed enum fields
- Export from `pypaperless/models/__init__.py`

**If reusing an existing model** (e.g. `Document` for `/api/trash/`): no new model needed.

### 4. Service (`pypaperless/services/<name>.py`)

See [service templates](./references/patterns.md#service-templates).

**Top-level paginated service:**

```python
class TrashService(ServiceBase, mixins.IterableMixin[Document]):
    _api_path = API_PATH["trash"]
    _resource = PaperlessResource.TRASH
    _resource_cls = Document
```

**Document sub-service (flat list):**

```python
class DocumentHistoryService(ServiceBase):
    _api_path = API_PATH["documents_history"]
    _resource = PaperlessResource.DOCUMENTS
    _resource_cls = DocumentHistory

    def __init__(self, client, attached_to=None):
        super().__init__(client)
        self._attached_to = attached_to

    async def __call__(self, pk=None):
        doc_pk = self._get_document_pk(pk)
        res = await self._client.request_json("get", self._api_path.format(pk=doc_pk))
        return [self._resource_cls.from_data(self._client, {**item, "document": doc_pk})
                for item in res]

    def _get_document_pk(self, pk=None):
        if not any((self._attached_to, pk)):
            raise PrimaryKeyRequiredError(...)
        return cast(int, self._attached_to or pk)
```

**Action methods (POST):**

```python
async def restore(self, documents: list[int]) -> None:
    res = await self._client.request("post", self._api_path,
        json={"action": "restore", "documents": documents})
    res.raise_for_status()
```

### 5. Wire Up

**`pypaperless/services/__init__.py`** — export the new service class.

**`pypaperless/client.py`** — register in `Paperless.__init__`:

```python
self.trash = services.TrashService(self)
```

**For document sub-services** — wire into `DocumentService.__init__` and add a lazy property on `Document` (see [sub-service wiring](./references/patterns.md#document-sub-service)).

### 6. Test Fixture (`tests/data/<name>.py`)

Create realistic snapshot data matching the actual API response shape:

- **Paginated**: wrap in `{ "count": N, "next": null, "previous": null, "all": [...], "results": [...] }`
- **Flat list**: plain `[{...}, ...]`
- **Direct**: single `{...}` dict

Export from `tests/data/__init__.py` (import + add to `__all__`).

### 7. Unit Tests (`tests/test_models_specific.py`)

Add a `class TestModel<Name>:` with:

- `test_iter` / `test_call` — test the main GET path via `httpx_mock`
- `test_<action>` — test each POST method
- For sub-services: also test via the parent `document.property()` and the `PrimaryKeyRequiredError` case

Pattern for mocking:

```python
httpx_mock.add_response(method="GET",
    url=f"{PAPERLESS_TEST_URL}{API_PATH['trash']}",  # or re.compile(...) for query params
    status_code=200, json=DATA_TRASH)
```

### 8. `script/pngx_audit_coverage.py`

Add an `EndpointSpec` to the `ENDPOINTS` list:

```python
EndpointSpec("Trash", "/api/trash/?page_size=1", Document, "paginated", "Document"),
```

`unwrap` values:

- `"paginated"` — DRF paginated response
- `"direct"` — single object
- `"list_index0"` — flat list (use first element)

If the service injects fields not in the API response (e.g. `document` PK):

- Add to `KNOWN_EXTRAS["ModelName"]`
- Add to `KNOWN_SCHEMA_EXTRAS["ModelName"]`

### 9. Documentation (`docs/resources/<name>.md`)

Create a Markdown page under `docs/resources/` for the new resource:

- **Heading** — resource name (e.g. `# Trash`)
- **Short description** — one sentence about what this resource represents
- **Model table** — all fields with a brief description
- **Sub-model tables** — one table per nested model class (if any)
- **Usage examples** — `GET` (call / iterate), any `POST` actions (restore, update, …)

Follow the style of existing pages such as
`docs/resources/statistics.md` (direct call) or
`docs/resources/correspondents.md` (full CRUD).

Then update **`docs/resources.md`**:

- Add the new resource to the **capability matrix** table (alphabetical order).
  Columns: `call`, `iterate`, `draft`/`save`, `update`, `delete`, `permissions`.

Then register the new page in **`zensical.toml`** (the MkDocs nav):

- Add a `{ "Name" = "resources/<name>.md" }` entry inside the `"Resources"` nav list, in alphabetical order.

```toml
{ "Profile" = "resources/profile.md" },
{ "Trash"   = "resources/trash.md" },
```

### 10. `script/pngx_smoketest.py`

Add a test function before the relevant section and wire it into `main()`:

```python
async def test_trash(p: Paperless) -> None:
    _hdr("Trash – list deleted documents")
    await check("trash.as_list()", p.trash.as_list(),
        detail_fn=lambda r: f"count={len(r)}")
```

### 11. Validate

```bash
source /home/vscode/.local/dev-venv/bin/activate

# Unit tests
python -m pytest tests/ -x -q

# Linting
ruff check pypaperless/

# Live audit (requires running Paperless instance)
python script/pngx_audit_coverage.py

# Live smoketest
python script/pngx_smoketest.py
```

Expected: all unit tests pass, audit shows `<Name> → OK`, smoketest shows 0 failed.

## Checklist

- [ ] `const.py` — string constant + `API_PATH` + `PaperlessResource`
- [ ] Model class with `_api_path`, typed fields, `StrEnum` for enums
- [ ] `models/__init__.py` — export
- [ ] Service class with correct mixins
- [ ] `services/__init__.py` — export
- [ ] `client.py` — register on `Paperless`
- [ ] Test fixture in `tests/data/`
- [ ] `tests/data/__init__.py` — export
- [ ] Unit tests in `test_models_specific.py`
- [ ] `script/pngx_audit_coverage.py` — `EndpointSpec` + any `KNOWN_EXTRAS`
- [ ] `docs/resources/<name>.md` — model table + usage examples
- [ ] `docs/resources.md` — capability matrix row
- [ ] `zensical.toml` — nav entry in alphabetical order
- [ ] `script/pngx_smoketest.py` — test function + wired in `main()`
- [ ] All tests green, lint clean

## Reference

- [Code patterns & templates](./references/patterns.md)
- Live Paperless: `http://172.17.0.1:8000` · Token: `3e9505078d32d8ad4ecea00fa0eec8e426622b52`
- Test document ID: `1980`
