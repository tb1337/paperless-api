# Basic Usage

## Documentation

* [Basic Usage](1_basic_usage.md) - This page ;)
* [Working with documents](2_documents.md)
* [Working with custom fields](3_custom_fields.md)
* [Permissions](4_permissions.md)

---

**On this page:**

- [Starting a session](#starting-a-session)
  - [Quickstart](#quickstart)
  - [URL rules](#url-rules)
  - [Custom session](#custom-session)
  - [Creating a token](#creating-a-token)
- [Resource features](#resource-features)
- [Requesting data](#requesting-data)
  - [Getting one item by primary key](#getting-one-item-by-primary-key)
  - [Retrieving a list of primary keys](#retrieving-a-list-of-primary-keys)
  - [Iterating over resource items](#iterating-over-resource-items)
  - [Iterating over pages](#iterating-over-pages)
  - [Reducing http requests](#reducing-http-requests)
- [Manipulating data](#manipulating-data)
  - [Creating new items](#creating-new-items)
  - [Updating existing items](#updating-existing-items)
  - [Deleting items](#deleting-items)

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

There are some rules for the *Paperless-ngx* url.

1. Isn't a scheme applied to it? `https` is automatically used.
2. If you explicitly start with `http`, the connection will be unencrypted (not recommended).
3. Only use the **base url** of your *Paperless-ngx*. Don't add `/api` to it.

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

**pypaperless** needs an API token to request and send data from and to *Paperless-ngx* for authentication purposes. It is recommended to create a technical user and assign a token to it via Django Admin, when you bootstrap any project with **pypaperless**. If you need to create that token by providing credentials, **pypaperless** ships with a little helper for that task.

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

> [!NOTE]
> Executed http requests: <br>
> `POST` `https://localhost:8000/api/token/`

## Resource features

| Resource       | Request  | Iterate | Create | Update | Delete | Permissions |
| -------------- | -------- | ------- | ------ | ------ | ------ | ----------- |
| config         | x        |
| correspondents | x        | x       | x      | x      | x      | x           |
| custom_fields  | x        | x       | x      | x      | x      |
| document_types | x        | x       | x      | x      | x      | x           |
| documents      | x        | x       | x      | x      | x      | x           |
| groups         | x        | x       |
| logs           | **n.a.** |
| mail_accounts  | x        | x       |        |        |        | x           |
| mail_rules     | x        | x       |        |        |        | x           |
| saved_views    | x        | x       |        |        |        | x           |
| share_links    | x        | x       | x      | x      | x      |
| statistics     | x        |
| status         | x        |
| storage_paths  | x        | x       | x      | x      | x      | x           |
| tags           | x        | x       | x      | x      | x      | x           |
| tasks          | x        | x\*     |        |        |
| users          | x        | x       |        |        |
| workflows      | x        | x       |        |        |

\*: Only `__aiter__` is supported.

`logs` are not implemented, as they return plain text. Since logs return plain text, support for this resource is currently not implemented.

## Requesting data

Retrieving data from *Paperless-ngx* is really easy, there are different possibilities to achieve that.

### Getting one item by primary key

This is the most common use case, since **pypaperless** always returns references to other resource items by their primary keys. You must resolve these references on your own. The returned objects are always `PaperlessModel`s.

```python
document = await paperless.documents(1337)
doc_type = await paperless.document_types(document.document_type) # 23

print(f"Document '{document.title}' is an {doc_type.name}.")
#-> Document 'Order #23: Desktop Table' is an Invoice.
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/1337/` <br>
> `GET` `https://localhost:8000/api/document_types/23/`

### Retrieving a list of primary keys

Since resource items are requested by their primary key, it could be useful to request a list of all available primary keys.

```python
item_keys = await paperless.documents.all()
#-> [1, 2, 3, ...]
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/?page=1`

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

> [!NOTE]
> The code above executes many http requests, depending on the count of your stored documents: <br>
> `GET` `https://localhost:8000/api/documents/?page=1` <br>
> `GET` `https://localhost:8000/api/documents/?page=2` <br>
> `...` <br>
> `GET` `https://localhost:8000/api/documents/?page=19`

### Iterating over pages

Instead of iterating over resource items, you may want to iterate over pagination results in some cases. The `Page` model itself delivers the possibility to check for the existence of previous and next pages, item counts, accessing the raw (`.results`) or processed data (`.items`), and so on.

```python
page_iter = aiter(paperless.documents.pages())
page = await anext(page_iter)
#-> page.current_page == 1
page = await anext(page_iter)
#-> page.current_page == 2
```

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/?page=1` <br>
> `GET` `https://localhost:8000/api/documents/?page=2`

### Reducing http requests

Requesting many pages can be time-consuming, so a better way to apply the filter (mentioned [here](#iterating-over-resource-items)) is to use the `reduce` context manager. Technically, it applies query parameters to the http request, which are interpreted as filters by *Paperless-ngx*.

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

> [!NOTE]
> Executed http requests: <br>
> `GET` `https://localhost:8000/api/documents/?page=1&correspondent__id=1`

> [!TIP]
> The `reduce` context works with all previously mentioned methods: `__aiter__`, `all` and `pages`.

> [!IMPORTANT]
> There are many filters available, **pypaperless** doesn't provide a complete list. I am working on it. At the moment, you must use the Django Rest framework http endpoint of *Paperless-ngx* in your browser and experiment with the **Filter** button on each resource.
>
> *Paperless-ngx* simply ignores filters which don't exist and treats them as no filter instead of raising errors, be careful.

## Manipulating data

**pypaperless** offers creation, update and deletion of resource items. These features are enabled where it makes (at least for me) sense, *Paperless-ngx* itself offers full CRUD functionality. Please check the [resource features](#resource-features) table at the top of this README. If you need CRUD for another resource, please let me know and open an [issue](https://github.com/tb1337/paperless-api/issues) with your specific use-case.

### Creating new items

The process of creating items consists of three parts: retrieving a new draft instance from **pypaperless**, apply data to it and call `save`. You can choose whether applying data to the draft via `kwargs` or by assigning it to the draft instance, or both. If you do not need to further use the created item, the draft instance can be safely discarded after saving, as it cannot be reused (database constraint violation).

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

> [!NOTE]
> Executed http requests: <br>
> `POST` `https://localhost:8000/api/correspondents/`

### Updating existing items

When it comes to updating data, you can choose between http `PATCH` (only changed fields) or `PUT` (all fields) methods. Usually updating only changed fields will do the trick. You can continue working with the class instance after updating, as the `update` method applies new data from *Paperless-ngx* to it.

```python
item = await paperless.documents(23)
item.title = "New document title"
success = await item.update()
success = await item.update(only_changed=False) # put all fields
#-> True
```

> [!NOTE]
> Executed http requests: <br>
> `PATCH` `http://localhost:8000/api/documents/23/` <br>
> **OR** <br>
> `PUT` `http://localhost:8000/api/documents/23/`

> [!TIP]
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

Last but not least, it is also possible to remove data from *Paperless-ngx*.

> [!CAUTION]
> This will permanently delete data from your database. There is no point of return. Be careful.

```python
item = await paperless.documents(23)
success = await item.delete()
#-> True
```

> [!NOTE]
> Executed http requests: <br>
> `DELETE` `http://localhost:8000/api/documents/23/`
