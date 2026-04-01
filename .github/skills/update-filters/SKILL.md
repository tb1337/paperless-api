---
name: update-filters
description: "Update the query filter TypedDicts in pypaperless/models/filters.py by reading the paperless-ngx source FilterSets, then sync the service filter() overrides and the docs. Use whenever paperless-ngx adds, renames, or removes filter fields."
argument-hint: "Optional: name of a specific resource to update (e.g. Document, Tag). Omit to update all."
---

# Update Query Filters in pypaperless

## When to Use

- paperless-ngx added or changed filter fields in `src/documents/filters.py`
- A new resource is added that needs a typed `filter()` override
- `ruff` or `mypy` reports issues in `pypaperless/models/filters.py`

## Files Involved

| File                             | Purpose                                       |
| -------------------------------- | --------------------------------------------- |
| `pypaperless/models/filters.py`  | TypedDicts — one per filterable resource      |
| `pypaperless/models/types.py`    | Re-exports all filter TypedDicts              |
| `pypaperless/services/<name>.py` | `filter()` override with `Unpack[XxxFilters]` |
| `pypaperless/services/trash.py`  | Also uses `DocumentFilters`                   |
| `docs/resources.md`              | General `filter()` documentation              |
| `docs/resources/<name>.md`       | Per-resource filter examples                  |

---

## Step 1 — Read the upstream FilterSets

Fetch the current paperless-ngx `filters.py` source:

```bash
curl -sL https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/dev/src/documents/filters.py
```

For each `FilterSet` class, collect:

1. **`Meta.fields` dict** — keys are field names, values are lookup lists
   (`ID_KWARGS`, `CHAR_KWARGS`, `INT_KWARGS`, `DATE_KWARGS`, `DATETIME_KWARGS`, or explicit lists like `["isnull"]`)
2. **Explicitly declared filter attributes** outside `Meta` (e.g. `is_tagged`, `tags__id__all`, `title_content`)

### Lookup group → Python type mapping

| Group constant    | Lookups                                           | Python type                                         |
| ----------------- | ------------------------------------------------- | --------------------------------------------------- |
| `ID_KWARGS`       | `exact`, `in`                                     | `int` for `exact`; `str` for `in` (comma-separated) |
| `CHAR_KWARGS`     | `istartswith`, `iendswith`, `icontains`, `iexact` | `str`                                               |
| `INT_KWARGS`      | `exact`, `gt`, `gte`, `lt`, `lte`, `isnull`       | `int` for numeric; `bool` for `isnull`              |
| `DATE_KWARGS`     | `year`, `month`, `day`, `gt`, `gte`, `lt`, `lte`  | `int` for components; `str` for comparisons         |
| `DATETIME_KWARGS` | same as `DATE_KWARGS` + `date__gt/gte/lt/lte`     | same                                                |
| `["isnull"]`      | `isnull`                                          | `bool`                                              |
| `["exact"]`       | `exact`                                           | `str` (or `int` if the field is numeric)            |
| `["icontains"]`   | `icontains`                                       | `str`                                               |

### Field name → TypedDict key expansion

For a `Meta.fields` entry `"field_name": LOOKUP_GROUP`, expand to one key per lookup:

- `"id": ID_KWARGS` → `id: int` and `id__in: str`
- `"name": CHAR_KWARGS` → `name__icontains: str`, `name__istartswith: str`, `name__iendswith: str`, `name__iexact: str`
- `"created": DATE_KWARGS` → `created__year: int`, `created__month: int`, `created__day: int`, `created__gt: str`, …
- `"correspondent": ["isnull"]` → `correspondent__isnull: bool`

For explicitly declared attributes (outside `Meta`), add them directly with their semantic type:

- `BooleanFilter` → `bool`
- `ObjectFilter` → `str` (comma-separated PKs)
- `TitleContentFilter`, `EffectiveContentFilter`, `MimeTypeFilter`, `CustomFieldsFilter` → `str`
- `CustomFieldQueryFilter` → `str` (JSON expression)

---

## Step 2 — Update `pypaperless/models/filters.py`

### FilterSet → TypedDict mapping

| paperless-ngx FilterSet  | pypaperless TypedDict  |
| ------------------------ | ---------------------- |
| `CorrespondentFilterSet` | `CorrespondentFilters` |
| `TagFilterSet`           | `TagFilters`           |
| `DocumentTypeFilterSet`  | `DocumentTypeFilters`  |
| `StoragePathFilterSet`   | `StoragePathFilters`   |
| `CustomFieldFilterSet`   | `CustomFieldFilters`   |
| `DocumentFilterSet`      | `DocumentFilters`      |
| `PaperlessTaskFilterSet` | `TaskFilters`          |
| `ShareLinkFilterSet`     | `ShareLinkFilters`     |

### Style rules

- **No** `page` or `page_size` fields in the TypedDicts — pagination params are passed as plain kwargs alongside filters, outside the typed scope
- `total=False` on every class (all fields optional)
- **Classifier resources** (Correspondent, Tag, DocumentType, StoragePath, CustomField) inherit from `_NameFilters` (which itself extends `_IdFilters`). Only add extra fields in the subclass.
- `DocumentFilters` inherits `_IdFilters` + `_CreatedFilters`; `ShareLinkFilters` inherits `_CreatedFilters`. Both define their remaining fields directly.
- Private base hierarchy: `_IdFilters` → `_NameFilters`; `_CreatedFilters` is independent.
- **No section-header comments** (they trigger ERA001). Remove them entirely.
- **Keep** inline comments only when the semantics are non-obvious:
  - `# comma-separated PKs` on `id__in` / `*__id__none` fields
  - `# backwards-compat alias` on deprecated lookup aliases
  - Boolean semantics: `# True → document has at least one tag`
  - Special behaviour: `# searches title AND content simultaneously`, `# JSON expression, see paperless-ngx docs`
- **Field order**: fields within each TypedDict are sorted **alphabetically** by key name.
- **Class order**: public filter classes must be sorted **alphabetically** by class name. Private bases (`_CreatedFilters`, `_IdFilters`, `_NameFilters`) always stay at the top of the file, before the public classes.
- **Mandatory inheritance**: every new filter class **must** inherit from the most specific private base that fits rather than duplicating fields. Use `_NameFilters` whenever the resource has `name__*` + `id` fields. Use `_IdFilters` when only id fields are needed. Use `_CreatedFilters` for date-range resources. Combine with multiple inheritance where appropriate (`_IdFilters, _CreatedFilters`). A class body that consists solely of the docstring (no extra fields) is correct and expected when the base already provides everything.
- No blank lines between fields within the same TypedDict

### Template — classifier resource (inherits `_NameFilters`)

Provides `id`, `id__in`, `name__icontains/istartswith/iendswith/iexact` automatically.

```python
class XxxFilters(_NameFilters, total=False):
    """Filters for :attr:`Paperless.xxx`."""

    # only fields NOT already in _NameFilters, sorted alphabetically
    some_extra_flag: bool
```

If the resource has no extra fields, the class body is just the docstring (no field duplication!):

```python
class XxxFilters(_NameFilters, total=False):
    """Filters for :attr:`Paperless.xxx`."""
```

**Real-world example** — `GroupFilters` has exactly the same fields as `_NameFilters` (`id`, `id__in`, `name__icontains/istartswith/iendswith/iexact`), so it inherits with an empty body:

```python
class GroupFilters(_NameFilters, total=False):
    """Filters for :attr:`Paperless.groups`."""
```

### Template — resource with created-date filters (inherits `_CreatedFilters`)

Provides all `created__year/month/day/gt/gte/lt/lte/date__*` fields automatically.

```python
class XxxFilters(_CreatedFilters, total=False):
    """Filters for :attr:`Paperless.xxx`."""

    # only non-created fields
    expiration__year: int
    ...
```

### Template — resource with id + created-date filters

```python
class XxxFilters(_IdFilters, _CreatedFilters, total=False):
    """Filters for :attr:`Paperless.xxx`."""

    # fields beyond id/id__in and created__*
    title__icontains: str
    ...
```

---

## Step 3 — Update `pypaperless/models/types.py`

Ensure every TypedDict is imported and listed in `__all__`:

```python
from .filters import (
    CorrespondentFilters,
    CustomFieldFilters,
    DocumentFilters,
    DocumentTypeFilters,
    ShareLinkFilters,
    StoragePathFilters,
    TagFilters,
)
```

Add new TypedDict names to `__all__` in alphabetical order.

---

## Step 4 — Update service `filter()` overrides

Every service that uses `IterableMixin` needs a `filter()` override. The pattern is identical for all:

```python
# imports at top of file
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self, Unpack

from pypaperless.models.filters import XxxFilters

# inside the service class, directly after _resource_cls assignment
@asynccontextmanager
async def filter(self, **kwargs: Unpack[XxxFilters]) -> AsyncGenerator[Self, None]:
    """Iterate with server-side filters.

    See :class:`~pypaperless.models.filters.XxxFilters` for available keys.
    """
    async with self._store_filters(**kwargs) as ctx:
        yield ctx
```

### Service → Filters mapping

| Service class          | Filter TypedDict       |
| ---------------------- | ---------------------- |
| `CorrespondentService` | `CorrespondentFilters` |
| `TagService`           | `TagFilters`           |
| `DocumentTypeService`  | `DocumentTypeFilters`  |
| `StoragePathService`   | `StoragePathFilters`   |
| `CustomFieldService`   | `CustomFieldFilters`   |
| `ShareLinkService`     | `ShareLinkFilters`     |
| `DocumentsService`     | `DocumentFilters`      |
| `TrashService`         | `DocumentFilters`      |
| `GroupService`         | `GroupFilters`         |
| `UserService`          | `UserFilters`          |

Services **without** a `filter()` override (no FilterSet upstream):
`SavedViewService`, `WorkflowService`, `MailAccountService`, `MailRuleService`, `ProcessedMailService`

`TaskService` has an upstream `PaperlessTaskFilterSet` (`TaskFilters` exists), but its `__aiter__` fetches a flat
non-paginated list and does not use `IterableMixin`. Until the service is reworked to support pagination,
do **not** add a `filter()` override there.

---

## Step 5 — Update `docs/resources.md`

The section **"Filtering with `filter()`"** should mention that filter keys are type-checked:

````markdown
## Filtering with `filter()`

`filter()` is an async context manager that applies server-side filters to
iteration. Filter keys are fully type-checked — your IDE will autocomplete
available parameters and flag unknown keys.

Each service exposes its own typed filter set (e.g. `DocumentFilters`,
`TagFilters`); import them from `pypaperless.models.types` if you want to
construct the dict separately:

```python
from pypaperless.models.types import DocumentFilters

filters: DocumentFilters = {
    "correspondent__id": 3,
    "title__icontains": "invoice",
    "page_size": 50,
}

async with paperless.documents.filter(**filters):
    async for document in paperless.documents:
        ...
```
````

````

---

## Step 6 — Update per-resource docs

For resources that have a `FilterSet` upstream, update `docs/resources/<name>.md` to
show a concrete typed example. Use the resource's most common filter keys.

**Template:**

```markdown
## Filtering

Use `filter()` to apply server-side filters.  Available keys are defined in
`DocumentFilters` (importable from `pypaperless.models.types`):

```python
async with paperless.documents.filter(
    title__icontains="invoice",
    correspondent__id=3,
    tags__id__all="5,12",
) as docs:
    async for doc in docs:
        print(doc.title)
````

````

Only update docs files that already have a `filter()` usage example — do not
create new doc files as part of this skill.

---

## Step 7 — Add or Update Tests

### Unit tests — `tests/test_common.py`

The `TestFilters` class verifies TypedDict structure.  For **new** TypedDicts, add or extend:

1. `test_all_filter_classes_have_annotations` — add the new class to `_ALL_FILTER_CLASSES`.
2. `test_all_filters_exclude_page_fields` — already covered by `_ALL_FILTER_CLASSES`.
3. Add a resource-specific test verifying key fields unique to that TypedDict (e.g. `is_root` for `TagFilters`, `path__icontains` for `StoragePathFilters`).

Pattern for a resource-specific field test:

```python
def test_xxx_filters_fields(self) -> None:
    """XxxFilters must contain resource-specific fields."""
    all_keys = XxxFilters.__optional_keys__ | XxxFilters.__required_keys__
    assert "some_field__icontains" in all_keys
````

Also add the new TypedDict to the import block at the top of `test_common.py`.

### Unit tests — `tests/test_models_specific.py`

The `TestTypedReduce` class tests each service's typed `filter()` at the HTTP level. For every new service with a typed override, add a test method:

```python
async def test_xxx_filter_typed(
    self, httpx_mock: HTTPXMock, paperless: Paperless
) -> None:
    """xxx.filter() accepts XxxFilters kwargs."""
    from .data import DATA_XXX

    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"^" + f"{PAPERLESS_TEST_URL}{API_PATH['xxx']}" + r"\?.*$"),
        status_code=200,
        json=DATA_XXX,
    )
    async with paperless.xxx.filter(name__icontains="test") as q:
        async for item in q:
            assert item is not None
```

Use a filter key specific to that TypedDict so the test exercises the correct override.

### Smoketest — `script/pngx_smoketest.py`

The `test_filter_context` function covers live filter calls. For new services, add a block inside that function:

```python
try:
    async with p.xxx.filter(name__icontains="a"):
        count = 0
        async for _ in p.xxx:
            count += 1
            if count >= PAGE_SIZE:
                break
    ok("xxx.filter(name__icontains='a')", f"iterated={count}")
except Exception as exc:
    fail("xxx.filter()", exc)
```

Choose a filter key that is both safe (read-only, unlikely to cause errors) and specific to the TypedDict.

---

## Step 8 — Validate

Run the full validation sequence:

```bash
# 1. Unit tests + coverage
/usr/local/py-utils/bin/pytest -x -q

# 2. Live smoketest
source /home/vscode/.local/dev-venv/bin/activate && python script/pngx_smoketest.py

# 3. API field coverage audit
python script/pngx_audit_coverage.py
```

All three must pass before the task is complete.

---

## Common Mistakes

- **Do not** add `# section header` comments inside TypedDicts — ERA001 will flag them.
- **Do not** add `page` or `page_size` to a filter TypedDict — those are plain kwargs passed outside the typed scope.
- **Do not** repeat `id`/`id__in` or `name__*` fields in a class that inherits `_NameFilters` — they are already provided.
- **Do not** repeat `created__*` fields in a class that inherits `_CreatedFilters` — they are already provided.
- **Do not** define a new filter class as a flat `TypedDict` when a private base already covers its fields. Always inherit. A class body with only a docstring is correct when the base provides everything.
- **Do not** sort fields in a way that breaks the alphabetical rule. Fields within each TypedDict must be alphabetically ordered (except for large upstream-mirrored classes like `DocumentFilters` where semantic grouping is kept).
- **Do not** use `TypeVar` with `Unpack` — this is not supported by PEP 692. Every service needs its own concrete override.
- **Do not** update services that don't have a corresponding FilterSet (e.g. `SavedViewService`). Their `filter()` falls back to the base `IterableMixin` which accepts `**kwargs: Unpack[_BaseFilters]`.
- **Do not** call `super().filter(**kwargs)` in service overrides — the base `filter()` signature only accepts `**kwargs: Unpack[_BaseFilters]` (empty TypedDict) and cannot receive the extra keys. Call `self._store_filters(**kwargs)` instead.
- **Do not** forget to add the new TypedDict to `_ALL_FILTER_CLASSES` in `tests/test_common.py`.
