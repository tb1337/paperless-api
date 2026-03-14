# Custom field query

The `custom_field_query` filter lets you search documents by custom field values using a structured boolean expression. Paperless-ngx parses the expression serverside — pypaperless provides a small builder so you never have to construct the JSON by hand.

---

## Builder classes

| Class                                | Operator shortcut | JSON output            |
| ------------------------------------ | ----------------- | ---------------------- |
| `CustomFieldQuery(field, op, value)` | —                 | `[field, op, value]`   |
| `CustomFieldQueryAnd(q1, q2, …)`     | `q1 & q2`         | `["AND", [q1, q2, …]]` |
| `CustomFieldQueryOr(q1, q2, …)`      | `q1 &#124; q2`    | `["OR", [q1, q2, …]]`  |
| `CustomFieldQueryNot(q)`             | `~q`              | `["NOT", q]`           |

Import from `pypaperless.models.custom_field_query` (or via `pypaperless.models.types`):

```python
from pypaperless.models.custom_field_query import CustomFieldQuery
```

---

## Basic usage

Build an expression and pass `str(q)` to the `custom_field_query` kwarg of `documents.filter()`:

```python
from pypaperless.models.custom_field_query import CustomFieldQuery

q = CustomFieldQuery("Status", "exact", "open")

async with paperless.documents.filter(custom_field_query=str(q)) as docs:
    async for doc in docs:
        print(doc.title)
```

---

## Combining expressions

Use `&`, `|` and `~` to build boolean queries. Chained `&` and `|` are automatically flattened:

```python
q = (
    CustomFieldQuery("Status", "exact", "open")
    & CustomFieldQuery("Amount", "gte", 100)
    & ~CustomFieldQuery("Archived", "exact", True)
)
# Serialises to:
# ["AND", [["Status","exact","open"], ["Amount","gte",100], ["NOT",["Archived","exact",true]]]]
```

OR across multiple categories:

```python
q = (
    CustomFieldQuery("Category", "exact", "A")
    | CustomFieldQuery("Category", "exact", "B")
    | CustomFieldQuery("Category", "exact", "C")
)
```

---

## Referencing a field

`field` can be either the **integer ID** or the **name string**:

```python
CustomFieldQuery(42, "exists", True)        # by ID
CustomFieldQuery("Invoice Amount", "gte", 100)  # by name
```

---

## Supported operators

The valid operators depend on the field's data type:

| Applies to                           | Operators                                      |
| ------------------------------------ | ---------------------------------------------- |
| **All types**                        | `exact` `in` `isnull` `exists`                 |
| `STRING` `LONGTEXT` `URL` `MONETARY` | `icontains` `istartswith` `iendswith`          |
| `INTEGER` `FLOAT` `MONETARY` `DATE`  | `gt` `gte` `lt` `lte` `range`                  |
| `DOCUMENT_LINK`                      | `contains`                                     |
| `DATE` (component)                   | `year__exact` `month__exact` `day__exact` etc. |

### `exists` vs `isnull`

`exists` is the idiomatic way to check field presence:

```python
CustomFieldQuery("Due Date", "exists", True)   # document has the field
CustomFieldQuery("Due Date", "exists", False)  # document does not have the field
```

### `in` and `range`

Pass a list as the value:

```python
CustomFieldQuery("Status", "in", ["open", "pending"])
CustomFieldQuery("Amount", "range", [10, 100])  # start, end (inclusive)
```

### Date components

```python
CustomFieldQuery("Invoice Date", "year__exact", 2024)
CustomFieldQuery("Invoice Date", "month__exact", 12)
```

---

## Using `build()`

`str(q)` is shorthand for `json.dumps(q.build())`. Call `build()` directly if you need the raw Python structure:

```python
q = CustomFieldQuery("Amount", "gte", 50) & CustomFieldQuery("Status", "exact", "open")
print(q.build())
# ["AND", [["Amount", "gte", 50], ["Status", "exact", "open"]]]

print(str(q))
# '["AND", [["Amount", "gte", 50], ["Status", "exact", "open"]]]'
```

---

## Server-side limits

Paperless-ngx enforces:

- Maximum nesting depth: **10**
- Maximum number of atoms: **20**

Exceeding these limits returns a HTTP 400 validation error.
