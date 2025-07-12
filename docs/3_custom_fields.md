# Working with custom fields

When classifying your documents, you may want to add custom fields to them. As of `v4.2`, **pypaperless** introduced a complete new way of working with them!

## Documentation

* [Basic Usage](1_basic_usage.md)
* [Working with documents](2_documents.md)
* [Working with custom fields](3_custom_fields.md) - This page ;)
* [Permissions](4_permissions.md)

---

**On this page:**

- [Introduction to custom fields](#introduction-to-custom-fields)
- [Caching](#caching)
  - [Provide a cache](#provide-a-cache)
  - [Without cache](#without-cache)
- [Verifying existence of a custom field](#verifying-existence-of-a-custom-field)
  - [By `CustomField` instance itself](#by-customfield-instance-itself)
  - [By primary key](#by-primary-key)
- [Iterating all custom fields](#iterating-all-custom-fields)
- [Fetching custom field values](#fetching-custom-field-values)
  - [Without fallback (get)](#without-fallback-get)
    - [By `CustomField` instance itself](#by-customfield-instance-itself-1)
    - [By primary key](#by-primary-key-1)
    - [Type safety](#type-safety)
  - [With fallback to `None` (default)](#with-fallback-to-none-default)
    - [By `CustomField` instance itself](#by-customfield-instance-itself-2)
    - [By primary key](#by-primary-key-2)
    - [Type safety](#type-safety-1)
- [Adding custom fields to a document](#adding-custom-fields-to-a-document)
- [Special custom field data types](#special-custom-field-data-types)
  - [Date](#date)
  - [Document reference](#document-reference)
  - [Monetary](#monetary)
  - [Select](#select)

## Introduction to custom fields

When classifying your documents, you may want to add custom fields to them in *Paperless-ngx*. Working with their values could be tricky and required you to loop through lists of field primary keys and their values. You also had to look up the custom fields by their primary key and parse the values according to their data types.

This is a typical `CustomFieldInstance` object provided by the *Paperless-ngx* API:

```json
{
    // ...
    // inside document object
    "custom_fields": [
        {
            "value": 42,
            "field": 11
        },
    ],
    // ...
}
```

This provides no details about the custom field except for its primary key. Details can be found in the `CustomField` object itself, by explicitly requesting it:

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

Prior to `v4.2`, **pypaperless** only allowed direct manipulation of the `custom_fields` list, which was cumbersome and introduced significant overhead in your code. As custom fields are growing in importance more and more, it was about time to introduce a smarter way.

## Caching

### Provide a cache

You may now add all currently existing custom fields of your *Paperless-ngx* instance to a **pypaperless** cache. The main benefit of this cache mechanism is that **pypaperless** makes use of it while mapping JSON objects to their model classes upon requesting them from the API.

```python
# initialize the cache
paperless.cache.custom_fields = await paperless.custom_fields.as_dict()
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/custom_fields/`

When fetching a document now, its custom fields are mapped to `CustomField...Value` objects.

```python
document = await paperless.documents(1337)

print(list(document.custom_fields))
#-> [
#     CustomFieldIntegerValue(field=1, value=42, name='Any Number Field', data_type=<CustomFieldType.INTEGER: 'integer'>, extra_data={'select_options': [None], 'default_currency': None}),
#     CustomFieldBooleanValue(field=3, value=True, ...),
#     CustomFieldSelectValue(field=5, ...)
# ]
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/1337/`

### Without cache

If you decide to not provide a cache, documents custom fields are mapped to the basic `CustomFieldValue` object, which provides only very basic functionality. You have to request the custom field configuration by yourself.

```python
print(list(document.custom_fields))
#-> [
#     CustomFieldValue(field=1, value=42),
#     CustomFieldValue(field=3, value=True),
#     CustomFieldValue(field=5, ...)
# ]
```

> [!TIP]
> This approach can be useful in scenarios where you're certain that, for example, field 11 contains the integer value you need to operate on.

## Verifying existence of a custom field

If you want to check whether a specific custom field is present in a document, pypaperless offers the following approaches.

### By `CustomField` instance itself

```python
specific_custom_field = await paperless.custom_fields(1)

if specific_custom_field in document.custom_fields:
    print("Custom field 1 is present!")
else:
    print("Custom field 1 is missing!")
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/custom_fields/1/`

### By primary key

```python
custom_field_id = 1

field = document.custom_fields.get(custom_field_id)
# do something with: field.value
```

## Iterating all custom fields

When you need to iterate over all custom fields in a document, just use a `for` loop.

```python
for field in document.custom_fields:
    # do something
```

## Fetching custom field values

Its time to work with specific custom field values. **pypaperless** provides different possibilities to retrieve the actual value of a field.

### Without fallback (get)

> [!CAUTION]
> Note that `document.custom_fields.get(...)` will raise `ItemNotFoundError` if the given custom field doesn't exist in the document data. If that could happen and you prefer not to perform an existence check before, you should use `.default(...)`.

#### By `CustomField` instance itself

```python
specific_custom_field = await paperless.custom_fields(1)

field = document.custom_fields.get(specific_custom_field)
print(field.value)
#-> 42
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/custom_fields/1/`

#### By primary key

```python
custom_field_id = 1

field = document.custom_fields.get(custom_field_id)
print(field.value)
#-> 42
```

#### Type safety

Due to the dynamic data structure of the *Paperless-ngx* API, static typing for `CustomFieldValue` instances is not possible in your development environment. However, if you don't want to give up type safety during development, you can either use `typing.cast()` or the following approach:

```python
from pypaperless.models.common import CustomFieldIntegerValue

field = document.custom_fields.get(custom_field_id, expected_type=CustomFieldIntegerValue)
```

> [!TIP]
> A `TypeError` is raised if the type of the custom field does not correspond to the expected type.

### With fallback to `None` (default)

#### By `CustomField` instance itself

```python
specific_custom_field = await paperless.custom_fields(1)

if field := document.custom_fields.default(specific_custom_field):
    print(field.value)
    #-> 42
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/custom_fields/1/`

#### By primary key

```python
custom_field_id = 1

if field := document.custom_fields.default(custom_field_id):
    print(field.value)
    #-> 42
```

#### Type safety

Just like with [`get()`](#type-safety), this method ensures type safety as well, if you like.

```python
from pypaperless.models.common import CustomFieldIntegerValue

field = document.custom_fields.default(custom_field_id, expected_type=CustomFieldIntegerValue)
```

> [!TIP]
> A `TypeError` is raised if the type of the custom field does not correspond to the expected type.

## Adding custom fields to a document

If you want to add new custom fields to your documents, you have to create a draft a custom field value. The `CustomField` model provides a `draft_value` method for that purpose.

## Special custom field data types

There are many data types for custom fields in *Paperless-ngx*, for example, strings and integers. While both are very common, special data types are also available. **pypaperless** provides some extra functionality for these.

### Date

The value field of `CustomFieldDateValue` is converted into a `datetime.date` object, if possible. It's a string or `None` otherwise.

### Document reference

The value field of `CustomFieldDocumentLinkValue` is converted into a list of document ids (no `Document` objects at all). But you could request those documents if you need to.

### Monetary

When using monetary custom fields in *Paperless-ngx*, their actual value is something like `EUR123.45`. **pypaperless** implements some properties to easily let you access the values.

* `.amount`: Gets or sets the actual amount.
* `.currency`: Gets or sets the currency (EUR, USD, ...).

> [!WARNING]
> **pypaperless** does not check the validity of values provided by you. Instead, *Paperless-ngx* will raise API errors when you try to save invalid data.

### Select

The `CustomFieldSelectValue` ordinary value field is set to an internal id by *Paperless-ngx*. **pypaperless** ships with properties which resolve the real values for you.

* `.label`: Returns the label for `value` or falls back to `None`.
* `.labels`: Returns the list of labels of the `CustomField`.
