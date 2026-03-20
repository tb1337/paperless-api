# Search Query Builder

The `SearchQuery` builder provides a fluent, composable DSL for constructing Whoosh-style query strings for the Paperless-ngx global search endpoint (`/api/search/`).

The builder output is a plain string - it is fully compatible with the raw string API. Both raw strings and builder objects are accepted by `paperless.search()`.

---

## Quick start

```python
from pypaperless.models.types import SearchQuery

# Plain term
result = await paperless.search("invoice")

# Using the builder (equivalent to above)
result = await paperless.search(SearchQuery("invoice"))

# Field-scoped: tag:unpaid
result = await paperless.search(SearchQuery.field("tag", "unpaid"))

# Combined: (invoice AND tag:unpaid)
q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
result = await paperless.search(q)
```

---

## Atoms

### Plain term

```python
SearchQuery("produ*name")   # wildcard
SearchQuery("contract")     # exact word
```

### Field-scoped term (`field:value`)

Match against a specific metadata field:

```python
SearchQuery.field("type", "invoice")
SearchQuery.field("tag", "unpaid")
SearchQuery.field("correspondent", "university")
```

The field names correspond to the Paperless-ngx Whoosh index fields: `type`, `tag`, `correspondent`, `title`, `content`.

### Date range (`field:[start to end]`)

```python
SearchQuery.date_range("created", "2005", "2009")
# → created:[2005 to 2009]

SearchQuery.date_range("added", "yesterday", "today")
# → added:[yesterday to today]

SearchQuery.date_range("modified", "2024-01-01", "2024-12-31")
# → modified:[2024-01-01 to 2024-12-31]
```

Paperless-ngx uses Whoosh's date parsing - relative expressions like `today`, `yesterday`, and partial dates like `2024` are all valid.

---

## Combining expressions

### AND (`&`)

All terms must match. Chaining `&` flattens into a single AND node (no extra parentheses):

```python
q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
# str(q) → "(invoice AND tag:unpaid)"

q = SearchQuery("shop") & SearchQuery.field("type", "invoice") & SearchQuery.date_range("created", "2020", "2024")
# str(q) → "(shop AND type:invoice AND created:[2020 to 2024])"
```

### OR (`|`)

At least one term must match. Chaining `|` also flattens:

```python
q = SearchQuery.field("tag", "inbox") | SearchQuery.field("tag", "important")
# str(q) → "(tag:inbox OR tag:important)"
```

### NOT (`~`)

Negates a term or expression:

```python
q = ~SearchQuery.field("type", "letter")
# str(q) → "NOT type:letter"
```

---

## Complex expressions

Operators compose freely:

```python
from pypaperless.models.types import SearchQuery

# "Find invoices or receipts tagged unpaid, from 2020 onwards, that are not letters"
q = (
    (SearchQuery.field("type", "invoice") | SearchQuery.field("type", "receipt"))
    & SearchQuery.field("tag", "unpaid")
    & SearchQuery.date_range("created", "2020", "today")
    & ~SearchQuery.field("type", "letter")
)
# str(q) → "((type:invoice OR type:receipt) AND tag:unpaid AND created:[2020 to today] AND NOT type:letter)"

result = await paperless.search(q)
```

---

## `str()` passthrough

Calling `str()` on any builder object yields the Whoosh query string directly:

```python
q = SearchQuery("contract") & SearchQuery.date_range("created", "2015", "2019")
print(str(q))
# (contract AND created:[2015 to 2019])
```

This means you can freely mix builder objects and raw strings in your code - both work with `paperless.search()`:

```python
# These are equivalent:
result = await paperless.search("invoice")
result = await paperless.search(SearchQuery("invoice"))
```

---

## API reference

| Class / method                        | Output format                     |
| ------------------------------------- | --------------------------------- |
| `SearchQuery(term)`                   | `term`                            |
| `SearchQuery.field(name, value)`      | `name:value`                      |
| `SearchQuery.date_range(name, s, e)`  | `name:[s to e]`                   |
| `q1 & q2` → `SearchQueryAnd`         | `(q1 AND q2)`                     |
| `q1 \| q2` → `SearchQueryOr`         | `(q1 OR q2)`                      |
| `~q` → `SearchQueryNot`              | `NOT q`                           |

All classes are importable from `pypaperless.models.types` or directly from `pypaperless.builders.search`.
