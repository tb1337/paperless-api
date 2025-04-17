# Usage

- [Starting a session](#starting-a-session)
  - [Quickstart](#quickstart)
  - [URL rules](#url-rules)
  - [Custom session](#custom-session)
  - [Creating a token](#creating-a-token)
- [Resource features](#resource-features)
- [Requesting data](#request-data)
  - [Getting one item by primary key](#getting-one-item-by-primary-key)
  - [Retrieving a list of primary keys](#retrieving-a-list-of-primary-keys)
  - [Iterating over resource items](#iterating-over-resource-items)
  - [Iterating over pages](#iterating-over-pages)
  - [Reducing http requests](#reducing-http-requests)
- [Manipulating data](#manipulating-data)
  - [Creating new items](#creating-new-items)
  - [Updating existing items](#updating-existing-items)
  - [Deleting items](#deleting-items)
- [Special cases](#special-cases)
  - [Document binary data](#document-binary-data)
  - [Document custom fields (NEW)](#document-custom-fields-new)
  - [Document metadata](#document-metadata)
  - [Document notes](#document-notes)
  - [Document searching](#document-searching)
  - [Document suggestions](#document-suggestions)
  - [Next available ASN](#next-available-asn)
  - [Permissions](#permissions)
    - [Toggle requesting permissions](#toggle-requesting-permissions)
    - [Create item with permissions](#create-item-with-permissions)
    - [Update permissions](#update-permissions)
  - [System Status](#system-status)

## Starting a session

### Quickstart

Just import the module and start using it. Note that we must be async.

```python
import asyncio

from pypaperless import Paperless

paperless = Paperless("localhost:8000", "your-secret-token")

# see main() examples

asyncio.run(main())
```

**main() Example 1**

```python
async def main():
    await paperless.initialize()
    # do something
    await paperless.close()
```

**main() Example 2**

```python
async def main():
    async with paperless:
        # do something
```

### URL rules

There are some rules for the Paperless-ngx url.

1. Isn't a scheme applied to it? `https` is automatically used.
2. If you explicitly start with `http`, the connection will be unencrypted (not recommended).
3. Only use the **base url** of your Paperless-ngx. Don't add `/api` to it.

### Custom session

You may want to use an existing `aiohttp.ClientSession` in some cases. Simply pass it to the `Paperless` object.

```python
import aiohttp
from pypaperless import Paperless

my_session = aiohttp.ClientSession()
# ...

paperless = Paperless("localhost:8000", "your-secret-token", session=my_session)
```

### Creating a token

_PyPaperless_ needs an API token to request and send data from and to Paperless-ngx for authentication purposes. It is recommended to create a technical user and assign a token to it via Django Admin, when you bootstrap any project with _PyPaperless_. If you need to create that token by providing credentials, _PyPaperless_ ships with a little helper for that task.

```python
token = Paperless.generate_api_token(
    "localhost:8000",
    "test_user",
    "your-password-here",
)
```

As for `Paperless` itself, you can provide a custom `aiohttp.ClientSession` object.

```python
url = "localhost:8000"
my_session = aiohttp.ClientSession()

token = Paperless.generate_api_token(
    "localhost:8000",
    "test_user",
    "not-so-secret-password-anymore",
    session=my_session,
)
```

> [!CAUTION]
> Hardcoding credentials or tokens is never good practise. Use that with caution.

The code above executes one http request:

`POST` `https://localhost:8000/api/token/`

## Resource features

| Resource       | Request  | Iterate | Create |  Update | Delete | Permissions |
| -------------- | -------- | ------- | ------ | ------- | ------ | ----------- |
| config         | x        |         |        |         |
| correspondents | x        | x       | x      | x       | x      | x           |
| custom_fields  | x        | x       | x      | x       | x      |
| document_types | x        | x       | x      | x       | x      | x           |
| documents      | x        | x       | x      | x       | x      | x           |
| groups         | x        | x       |        |         |
| logs           | **n.a.** |
| mail_accounts  | x        | x       |        |         |        | x           |
| mail_rules     | x        | x       |        |         |        | x           |
| saved_views    | x        | x       |        |         |        | x           |
| share_links    | x        | x       | x      | x       | x      |
| status | x |
| storage_paths  | x        | x       | x      | x       | x      | x           |
| tags           | x        | x       | x      | x       | x      | x           |
| tasks          | x        | x\*     |        |         |
| users          | x        | x       |        |         |
| workflows      | x        | x       |        |         |

\*: Only `__aiter__` is supported.

`logs` are not implemented, as they return plain text. Since logs return plain text, support for this resource is currently not implemented.

## Requesting data

Retrieving data from Paperless-ngx is really easy, there are different possibilities to achieve that.

### Getting one item by primary key

This is the most common use case, since _PyPaperless_ always returns references to other resource items by their primary keys. You must resolve these references on your own. The returned objects are always `PaperlessModel`s.

```python
document = await paperless.documents(1337)
doc_type = await paperless.document_types(document.document_type) # 23

print(f"Document '{document.title}' is an {doc_type.name}.")
#-> Document 'Order #23: Desktop Table' is an Invoice.
```

The code above executes two http requests:

`GET` `https://localhost:8000/api/documents/1337/` <br>
`GET` `https://localhost:8000/api/document_types/23/`

### Retrieving a list of primary keys

Since resource items are requested by their primary key, it could be useful to request a list of all available primary keys.

```python
item_keys = await paperless.documents.all()
#-> [1, 2, 3, ...]
```

The code above executes one http request:

`GET` `https://localhost:8000/api/documents/?page=1`

### Iterating over resource items

Iteration enables you to execute mass operations of any kind. Like requesting single items, the iterator always returns `PaperlessModel`s.

```python
count = 0
async for item in paperless.documents:
    if item.correspondent == 1:
        count += 1
print(f"{count} documents are currently stored for correspondent 1.")
#-> 5 documents are currently stored for correspondent 1.
```

The code above executes many http requests, depending on the count of your stored documents:

`GET` `https://localhost:8000/api/documents/?page=1` <br>
`GET` `https://localhost:8000/api/documents/?page=2` <br>
`...` <br>
`GET` `https://localhost:8000/api/documents/?page=19`

### Iterating over pages

Instead of iterating over resource items, you may want to iterate over pagination results in some cases. The `Page` model itself delivers the possibility to check for the existence of previous and next pages, item counts, accessing the raw (`.results`) or processed data (`.items`), and so on.

```python
page_iter = aiter(paperless.documents.pages())
page = await anext(page_iter)
#-> page.current_page == 1
page = await anext(page_iter)
#-> page.current_page == 2
```

The code above executes two http requests:

`GET` `https://localhost:8000/api/documents/?page=1` <br>
`GET` `https://localhost:8000/api/documents/?page=2`

### Reducing http requests

Requesting many pages can be time-consuming, so a better way to apply the filter (mentioned [here](#iterating-over-resource-items)) is to use the `reduce` context manager. Technically, it applies query parameters to the http request, which are interpreted as filters by Paperless-ngx.

```python
filters = {
    "correspondent__id": 1,
}
async with paperless.documents.reduce(**filters) as filtered:
    async for item in filtered:
        count += 1
# ...
#-> 5 documents are currently stored for correspondent 1.
```

The code above executes just one http request, and achieves the same:

`GET` `https://localhost:8000/api/documents/?page=1&correspondent__id=1`

> [!TIP]
> The `reduce` context works with all previously mentioned methods: `__aiter__`, `all` and `pages`.

> [!NOTE]
> There are many filters available, _PyPaperless_ doesn't provide a complete list. I am working on that. At the moment, you must use the Django Rest framework http endpoint of Paperless-ngx in your browser and experiment with the **Filter** button on each resource.
>
> Paperless-ngx simply ignores filters which don't exist and treats them as no filter instead of raising errors, be careful.

## Manipulating data

_PyPaperless_ offers creation, update and deletion of resource items. These features are enabled where it makes (at least for me) sense, Paperless-ngx itself offers full CRUD functionality. Please check the [resource features](#resource-features) table at the top of this README. If you need CRUD for another resource, please let me know and open an [issue](https://github.com/tb1337/paperless-api/issues) with your specific use-case.

### Creating new items

The process of creating items consists of three parts: retrieving a new draft instance from _PyPaperless_, apply data to it and call `save`. You can choose whether applying data to the draft via `kwargs` or by assigning it to the draft instance, or both. If you do not need to further use the created item, the draft instance can be safely discarded after saving, as it cannot be reused (database constraint violation).

```python
from pypaperless.models.common import MatchingAlgorithmType

draft = paperless.correspondents.draft(
    name="New correspondent",
    is_insensitive=True, # this works
)
draft.matching_algorithm = MatchingAlgorithmType.ANY
draft.match = 'any word "or small strings" match'
draft.is_insensitive = False # and this, too!

new_pk = await draft.save()
#-> 42
```

The code above executes one http request:

`POST` `https://localhost:8000/api/correspondents/`

### Updating existing items

When it comes to updating data, you can choose between http `PATCH` (only changed fields) or `PUT` (all fields) methods. Usually updating only changed fields will do the trick. You can continue working with the class instance after updating, as the `update` method applies new data from Paperless-ngx to it.

```python
item = await paperless.documents(23)
item.title = "New document title"
success = await item.update()
success = await item.update(only_changed=False) # put all fields
#-> True
```

The code above executes two http requests:

`PATCH` `http://localhost:8000/api/documents/23/` <br>
`PUT` `http://localhost:8000/api/documents/23/`

> [!NOTE]
> The actual payload of the request is completely different here, and I recommend you to use `PATCH` whenever possible. It is cleaner and much safer, as it only updates fields which have _actually_ changed.

**PATCH**

```json
{
  "title": "New document title"
}
```

**PUT**

```json
{
  "title": "New document title",
  "content": "...",
  "correspondents": ["..."],
  "document_types": ["..."],
  "storage_paths": ["..."],
  "...": "..."
  // and every other field
}
```

### Deleting items

Last but not least, it is also possible to remove data from Paperless-ngx.

> [!CAUTION]
> This will permanently delete data from your database. There is no point of return. Be careful.

```python
item = await paperless.documents(23)
success = await item.delete()
#-> True
```

The code above executes one http request:

`DELETE` `http://localhost:8000/api/documents/23/`

## Special cases

Some Paperless-ngx resources provide more features as others, especially when it comes to `Documents`.

### Document binary data

You can access the binary data by using the following methods. They all return a `DownloadedDocument` class instance, which holds the binary data and provides some more useful attributes, like content type, disposition type and filename.

**Example 1: Provide a primary key**

```python
download = await paperless.documents.download(23)
preview = await paperless.documents.preview(23)
thumbnail = await paperless.documents.thumbnail(23)
```

**Example 2: Already fetched item**

```python
document = await paperless.documents(23)

download = await document.get_download()
preview = await document.get_preview()
thumbnail = await document.get_thumbnail()
```

The examples above result in the following http requests:

`GET` `https://localhost:8000/api/documents/23/download/` <br>
`GET` `https://localhost:8000/api/documents/23/preview/` <br>
`GET` `https://localhost:8000/api/documents/23/thumb/`

### Document custom fields (NEW)

When classifying your documents, you may want to add custom fields to them. Working with their values could be tricky and required you to loop through lists of field primary keys and their values. You also had to look up the custom fields by their primary key and parse the values according to their data types.

This is a typical `CustomFieldInstance` object provided by the Paperless-ngx API:

```python
{
    # inside document object
    "custom_fields": [
        {
            "value": 42,
            "field": 11
        },
    ],
}
```

This provides no details about the custom field except for its primary key.

**Provide a cache for all custom fields**

The benefit of this cache mechanism is that you don't have to request custom fields from the API multiple times. In addition, _PyPaperless_ makes use of this cache while mapping JSON objects to their classes in your Python program. You could use that cache in your code, as well.

```python
# initialize the cache to let PyPaperless resolve custom fields automatically
paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

# fetch a document by primary key
document = await paperless.documents(1337)

doc_custom_fields = list(document.custom_fields)

```

Main difference between providing a cache or not:

```python
# without cache - no mapping, only basic information
print(doc_custom_fields[0])
#-> CustomFieldValue(field=11, value=42, name=None, data_type=None, extra_data=None)

# with cache - note the difference in the class type!
print(doc_custom_fields[0])
#-> CustomFieldIntegerValue(field=11, value=42, name='Any Number Field', data_type=<CustomFieldType.INTEGER: 'integer'>, extra_data={'select_options': [None], 'default_currency': None})
```

**Example 2: Lookup a specific custom field by `CustomField` instance**

```python
# select a custom field to access its value
specific_custom_field = await paperless.custom_fields(1)

# and work with it
if specific_custom_field in document.custom_fields:
    field = document.custom_fields.get(specific_custom_field)
    # do something with: field.value
```

**Example 3: Lookup a specific custom field by its primary key**

```python
custom_field_id = 1

field = document.custom_fields.get(custom_field_id)
# do something with: field.value
```

> [!NOTE]
> Note that `document.custom_fields.get(...)` will raise an exception if the given custom field doesn't exist in the document data. If that could happen and you prefer not to perform an existence check before, you should use `.default(...)`.

**Example 4: Lookup a specific custom field or fallback to `None`**

```python
if field := document.custom_fields.default(23):
    # do something with: field.value
```

**Example 5: Loop through all custom fields**
```python
for field in document.custom_fields:
    # do something with: field.value
```

**Special custom field data types**

There are many data types for custom fields in Paperless-ngx, for example, strings and integers. While both are very common, special data types are also available. _PyPaperless_ provides some extra functionality for uncommon data types.

* `CustomFieldDateValue.value`: The value is converted into a `datetime.datetime` object, if possible. It's a string or `None` otherwise.
* `CustomFieldDocumentLinkValue.value`: The value is a list of document ids (no `Document` objects at all)
* `CustomFieldSelectValue.labels`: Returns the list of labels of the `CustomField`.
* `CustomFieldSelectValue.label`: Returns the label for `value` (which is a reference to a label) or falls back to `None`.

### Document metadata

Paperless-ngx stores some metadata about your documents. If you wish to access that, there are two ways to access it.

**Example 1: Provide a primary key**

```python
metadata = await paperless.documents.metadata(23)
```

**Example 2: Already fetched item**

```python
document = await paperless.documents(23)
metadata = await document.get_metadata()
```

Both codes above execute one http request:

`GET` `https://localhost:8000/api/documents/23/metadata/`

### Document notes

Documents can be commented with so-called notes. Paperless-ngx supports requesting, creating and deleting those notes. _PyPaperless_ includes built-in support for it, too.

**Getting notes**

Document notes are always available as `list[DocumentNote]` after requesting them.

```python
# by primary key
list_of_notes = await paperless.documents.notes(23)

# by already fetched item
document = await paperless.documents(23)
list_of_notes = await document.notes()
```

The code above executes one http request:

`GET` `https://localhost:8000/api/documents/23/notes/`

**Creating notes**

You can add new notes. Updating existing notes isn't possible due to Paperless-ngx API limitations.

```python
# by primary key
draft = paperless.documents.notes.draft(23)

# by already fetched item
document = await paperless.documents(23)

draft = document.notes.draft()
draft.note = "Lorem ipsum"

new_note_pk, document_pk = await draft.save()
#-> 42, 23
```

The code above executes one http request:

`POST` `https://localhost:8000/api/documents/23/notes/`

**Deleting notes**

Sometimes it may be necessary to delete document notes.

> [!CAUTION]
> This will permanently delete data from your database. There is no way to recover deleted data. Be careful.

```python
a_note = list_of_notes.pop() # document note with example pk 42
success = await a_note.delete()
#-> True
```

The code above executes one http request:

`DELETE` `https://localhost:8000/api/documents/23/notes/?id=42`

### Document searching

If you want to search for documents, Paperless-ngx offers two possibilities to achieve that. _PyPaperless_ implements two iterable shortcuts for that.

**Search query**

Search query documentation: https://docs.paperless-ngx.com/usage/#basic-usage_searching

```python
async for document in paperless.documents.search("type:invoice"):
    # do something
```

The code above executes many http requests, depending on the count of your matched documents:

`GET` `https://localhost:8000/api/documents/?page=1&query=type%3Ainvoice` <br>
`GET` `https://localhost:8000/api/documents/?page=2&query=type%3Ainvoice` <br>
`...` <br>
`GET` `https://localhost:8000/api/documents/?page=19&query=type%3Ainvoice`

**More like**

Search for similar documents like the permitted document primary key.

```python
async for document in paperless.documents.more_like(23):
    # do something
```

The code above executes many http requests, depending on the count of your matched documents:

`GET` `https://localhost:8000/api/documents/?page=1&more_like_id=23` <br>
`GET` `https://localhost:8000/api/documents/?page=2&more_like_id=23` <br>
`...` <br>
`GET` `https://localhost:8000/api/documents/?page=19&more_like_id=23`

**Search results**

While iterating over search results, `Document` models are extended with another field: `search_hit`. Lets take a closer look at it.

```python
async for document in paperless.documents.more_like(23):
    print(f"{document.id} matched query by {document.search_hit.score}.")
#-> 42 matched query by 13.37.
```

To make life easier, you have the possibility to check whether a `Document` model has been initialized from a search or not:

```python
document = await paperless.documents(23) # no search
if document.has_search_hit:
    print("result of a search query")
else:
    print("not a result from a query")
#-> not a result from a query
```

### Document suggestions

One of the key functionalities of Paperless-ngx is _classification_: it is the workflow of assigning classifiers to your documents, like correspondents or tags. Paperless does that by auto-assigning or suggesting them to you. These suggestions can be accessed by _PyPaperless_, as well.

**Example 1: Provide a primary key**

```python
suggestions = await paperless.documents.suggestions(23)
```

**Example 2: Already fetched item**

```python
document = await paperless.documents(23)
suggestions = await document.get_suggestions()
```

Both codes above execute one http request:

`GET` `https://localhost:8000/api/documents/23/suggestions/`

The returned `DocumentSuggestions` instance stores a list of suggested resource items for each classifier: correspondents, tags, document_types, storage_paths and dates.

### Next available ASN

Simply returns the next available archive serial number as `int`.

```python
next_asn = await paperless.documents.get_next_asn()
#-> 1337
```

The code above executes one http request:

`GET` `https://localhost:8000/api/documents/next_asn/`

### Permissions

Some resources of Paperless-ngx support retrieving and updating of object-level permissions. When requesting data from Paperless-ngx, it delivers two permission fields by default: `owner` and `user_can_change`. You have to explicitly call the API to return the permissions table by a toggle parameter.

#### Toggle requesting permissions

If you want to access the permissions table, you have to enable it one by one for each resource.

```python
paperless.documents.request_permissions = True
document = await paperless.documents(23)

if document.has_permissions:
    print(document.permissions)
#-> PermissionTableType(
#       view=PermissionSetType(users=[...], groups=[...],
#       change=PermissionSetType(...)])
#   )

    for viewing_users in document.permissions.view.users:
        # do something with the user
```

Requesting permissions stays enabled until it gets disabled again.

```python
paperless.documents.request_permissions = False
document = await paperless.documents(23)

print(document.has_permissions)
#-> False
```

#### Create item with permissions

When creating new resource items, you can apply permissions by setting a `PermissionTableType` to the optional `set_permissions` field.

> [!NOTE]
> Both `PermissionTableType` and `PermissionSetType` automatically initialize empty lists for their fields unless you provided a value.

```python
from pypaperless.models.common import PermissionSetType, PermissionTableType

draft = paperless.correspondents.draft()

draft.name = "Correspondent with perms"
draft.set_permissions = PermissionTableType(
    view=PermissionSetType(
        users=[23],
    ),
)
# ...
```

#### Update permissions

If you want to change the permissions of a resource item, you have to enable requesting them before fetching it. The `permissions` field gets available then, ready for modifications.

```python
paperless.documents.request_permissions = True
document = await paperless.documents(23)

if document.has_permissions:
    document.permissions.view.users.append(5)
    await document.update()

```

### System Status

As of release 2.6.0, Paperless-ngx supports displaying information about the current system health.

```python
info = await paperless.status()
```

The code above executes one http request:

`GET` `https://localhost:8000/api/status/`
