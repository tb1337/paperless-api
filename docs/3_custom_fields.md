# Working with custom fields

When classifying your documents, you may want to add custom fields to them. As of `v5.0`, **pypaperless** introduces a completely new way of working with them!

## Documentation

* [Basic Usage](1_basic_usage.md)
* [Working with documents](2_documents.md)
* [Working with custom fields](3_custom_fields.md) - This page ;)
* [Permissions](4_permissions.md)

---

**On this page:**

- [Introduction to custom fields](#introduction-to-custom-fields)
- [Caching](#caching)
  - [Providing a cache](#providing-a-cache)
  - [Without cache](#without-cache)
- [Checking for custom fields](#checking-for-custom-fields)
- [Iterating over custom fields](#iterating-over-custom-fields)
- [Fetching custom field values](#fetching-custom-field-values)
  - [Without fallback (get)](#without-fallback-get)
  - [With fallback (default)](#with-fallback-default)
- [Adding custom fields to a document](#adding-custom-fields-to-a-document)
  - [Draft a new value](#draft-a-new-value)
  - [Attaching to a document](#attaching-to-a-document)
- [Removing custom fields from a document](#removing-custom-fields-from-a-document)
  - [Choose a custom field](#choose-a-custom-field)
  - [Detach it from document](#detach-it-from-document)
- [Updating custom field values](#updating-custom-field-values)
- [Special custom field data types](#special-custom-field-data-types)
  - [Date](#date)
  - [Document reference](#document-reference)
  - [Monetary](#monetary)
  - [Select](#select)

## Introduction to custom fields

In *Paperless-ngx*, custom fields allow you to enrich your documents with additional, structured data. Prior to `v5.0`, working with them was cumbersome: you had to loop through field IDs and values, manually resolve field metadata, and handle parsing based on their types.

Here is an example of how the *Paperless-ngx* API returns custom field instances:

```json
{
    "custom_fields": [
        {
            "value": 42,
            "field": 11
        },
    ]
}
```

As you can see, this only gives you the field’s ID. To get more details (like its name, type, or metadata), you must fetch the full `CustomField`:

```json
{
  "id": 1,
  "name": "Very Important Document (VID)",
  "data_type": "boolean",
  "extra_data": {
    "select_options": [
      null
    ],
    "default_currency": null
  },
  "document_count": 23
}
```

To simplify this, **pypaperless** now provides a smarter, more convenient interface for interacting with custom fields.

## Caching

### Providing a cache

You can now cache the list of custom fields for your *Paperless-ngx* instance. This allows **pypaperless** to map fields to rich model classes automatically when documents are fetched:

```python
# initialize the cache
paperless.cache.custom_fields = await paperless.custom_fields.as_dict()
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/`

Now, when you fetch a document, its fields are automatically mapped to their corresponding typed value objects:

```python
document = await paperless.documents(1337)

print(list(document.custom_fields))
#-> [
#     CustomFieldIntegerValue(field=1, value=42, name='Any Number Field', data_type=<CustomFieldType.INTEGER: 'integer'>, extra_data={'select_options': [None], 'default_currency': None}),
#     CustomFieldBooleanValue(field=3, value=True, ...),
#     CustomFieldSelectValue(field=5, ...)
# ]
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/1337/`

### Without cache

If you don’t provide a cache, custom fields are returned as generic `CustomFieldValue` instances:

```python
print(list(document.custom_fields))
#-> [
#     CustomFieldValue(field=1, value=42),
#     CustomFieldValue(field=3, value=True),
#     CustomFieldValue(field=5, ...)
# ]
```

> [!TIP]
> This approach can be useful in scenarios where you're certain that, for example, field 1 contains the integer value you need to operate on.

## Checking for custom fields

To check whether a custom field is attached to a document:

**Example 1: using a `CustomField` instance**

```python
specific_custom_field = await paperless.custom_fields(1)

if specific_custom_field in document.custom_fields:
    print("Custom field 1 is present!")
else:
    print("Custom field 1 is missing!")
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/1/`

**Example 2: using the field's ID**

```python
custom_field_id = 1

field = document.custom_fields.get(custom_field_id)
# do something with: field.value
```

## Iterating over custom fields

To iterate through all custom fields of a document:

```python
for field in document.custom_fields:
    # do something
```

## Fetching custom field values

Its time to work with specific custom field values. **pypaperless** provides different ways to retrieve the actual value of a field.

### Without fallback (get)

> [!CAUTION]
> Note that `document.custom_fields.get(...)` will raise `ItemNotFoundError` if the given custom field doesn't exist in the document data. If that could happen and you prefer not to perform an existence check before, you should use `.default(...)`.

**Example 1: using `CustomField` instance**

```python
specific_custom_field = await paperless.custom_fields(1)

field = document.custom_fields.get(specific_custom_field)
print(field.value)
#-> 42
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/1/`

**Example 2: using the field's ID**

```python
custom_field_id = 1

field = document.custom_fields.get(custom_field_id)
print(field.value)
#-> 42
```

**Example 3: Type safety**

Due to the dynamic data structure of the *Paperless-ngx* API, static typing for `CustomFieldValue` instances is not possible in your development environment. However, if you don't want to give up type safety during development, you can either use `typing.cast()` or the following approach:

```python
from pypaperless.models.common import CustomFieldIntegerValue

field = document.custom_fields.get(custom_field_id, expected_type=CustomFieldIntegerValue)
```

> [!TIP]
> A `TypeError` is raised if the type of the custom field does not correspond to the expected type.

### With fallback (default)

This avoids errors if the field is missing and returns `None` instead.

**Example 1: using `CustomField` instance**

```python
specific_custom_field = await paperless.custom_fields(1)

if field := document.custom_fields.default(specific_custom_field):
    print(field.value)
    #-> 42
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/1/`

**Example 2: using the field's ID**

```python
custom_field_id = 1

if field := document.custom_fields.default(custom_field_id):
    print(field.value)
    #-> 42
```

**Example 3: Type safety**

Just like with `get()`, this method ensures type safety as well.

```python
from pypaperless.models.common import CustomFieldIntegerValue

field = document.custom_fields.default(custom_field_id, expected_type=CustomFieldIntegerValue)
```

> [!TIP]
> A `TypeError` is raised if the type of the custom field does not correspond to the expected type.

## Adding custom fields to a document

If you want to add new custom fields to your documents, you have to draft custom field values and add them to the documents custom fields list.

### Draft a new value

Use the `draft_value` method on a `CustomField`:

**Example 1: with cache ([read about caching](#providing-a-cache))**

```python
my_int_field = await paperless.custom_fields(1)

new_field_value = my_int_field.draft_value(42)
print(new_field_value)
#-> CustomFieldIntegerValue(field=1, value=42, name='My Integer Field', data_type=<CustomFieldType.INTEGER: 'integer'>, ...)
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/1/`

**Example 2: without cache**

```python
new_field_value = my_int_field.draft_value(42)
print(new_field_value)
#-> CustomFieldValue(field=1, value=42, ...)
```

**Example 3: Typing**

There is optional type mapping for your development environment the same way as with `get()` and `default()`. Unlike the previous cases, **no exception is raised** if the type doesn't match.

```python
from pypaperless.models.common import CustomFieldIntegerValue

new_field_value = my_int_field.draft_value(42, expected_type=CustomFieldIntegerValue)
```

### Attaching to a document

The new custom field value is ready to go:

```python
document = await paperless.documents(1337)

document.custom_fields.add(new_field_value)
# or simply use
document.custom_fields += new_field_value
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/1337/`

> [!CAUTION]
> Don't forget to call `document.update()` to persist your change in the *Paperless-ngx* database. You can read more about that [here](1_basic_usage.md#updating-existing-items).

## Removing custom fields from a document

In some cases, you may want to remove custom fields from documents again. It is as easy as adding fields.

### Choose a custom field

You can remove fields in three ways.

**Example 1: using `CustomField` instance**

```python
my_int_field = await paperless.custom_fields(1)
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/custom_fields/1/`

**Example 2: using the field's ID**

```python
my_int_field = 1
```

**Example 3: using `CustomFieldValue` instance**

```python
my_int_field = document.custom_fields.get(1)
```

### Detach it from document

The custom field value is ready to be removed:

```python
document = await paperless.documents(1337)

document.custom_fields.remove(my_int_field)
# or simply use
document.custom_fields -= my_int_field
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/1337/`

> [!CAUTION]
> Don't forget to call `document.update()` to persist your change in the *Paperless-ngx* database. You can read more about that [here](1_basic_usage.md#updating-existing-items).

## Updating custom field values

As with every other entity in **pypaperless**, custom field values can be manipulated by just setting a new value to them.

**Example 1: integer custom field**

```python
document = await paperless.documents(1337)

if field := document.custom_fields.default(1):
    field.value = 23
    await document.update()
```

**Example 2: monetary custom field**

This custom field value is one of the special cases, [scroll down](#monetary) to read more about them.

```python
document = await paperless.documents(1337)

if field := document.custom_fields.default(2):
    field.amount = 42.23
    await document.update()

print(field.value)
#-> EUR42.23
```

## Special custom field data types

There are many data types for custom fields in *Paperless-ngx*, for example, strings and integers. While both are very common, special data types are also available. **pypaperless** provides some extra functionality for these.

### Date

Values in `CustomFieldDateValue` are parsed into `datetime.date`. If parsing fails, the raw string or `None` is returned.

### Document reference

Returns a list of document IDs. You can fetch full documents manually if needed.

### Monetary

Monetary values such as `EUR123.45` are exposed via:

* `.amount`: Gets or sets the actual amount.
* `.currency`: Gets or sets the currency (EUR, USD, ...).

> [!WARNING]
> Input is not validated client-side. Invalid values will trigger API errors.

### Select

The `CustomFieldSelectValue` raw value is set to an internal ID by *Paperless-ngx*. **pypaperless** ships with properties which resolve the real values for you.

* `.label`: Returns the label for `value` or falls back to `None`.
* `.labels`: Returns the list of labels of the `CustomField`.
