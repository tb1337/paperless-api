# PyPaperless

![Test Badge](https://github.com/tb1337/paperless-api/actions/workflows/test.yml/badge.svg) [![codecov](https://codecov.io/gh/tb1337/paperless-api/graph/badge.svg?token=IMXRBK3HRE)](https://codecov.io/gh/tb1337/paperless-api)

Little api client for [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)!

Find out more here:

- Project: https://docs.paperless-ngx.com
- REST API: https://docs.paperless-ngx.com/api/

## Features

- Depends on aiohttp, works in async environments.
- Token authentication only. **No credentials anymore.**
- Request single resource items.
- Iterate over all resource items or request them page by page.
- Create, update and delete resource items.
- Almost feature complete.
- _PyPaperless_ is designed to only transport data. Your code organizes it.

## Documentation

- [Starting a session](#starting-a-session)
  - [Quickstart](#quickstart)
  - [URL rules](#url-rules)
  - [Custom session](#custom-session)
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

### Starting a session

#### Quickstart

Just import the module and go on. Note that we must be async.

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

#### URL rules

There are some rules for the Paperless-ngx url.

1. Isn't a scheme applied to it? Use `https`.
2. Is `http` explicitly used in it? Okay, be unsafe :dizzy_face:.
3. Only use the **base url** of your Paperless-ngx. Don't add `/api` to it.

#### Custom session

You may want to use a customized session in some cases. The `PaperlessSession` object will pass optional kwargs to each request method call, it is utilizing an `aiohttp.ClientSession` under the hood.

```python
from pypaperless import Paperless, PaperlessSession

my_session = PaperlessSession("localhost:8000", "your-secret-token", ssl=False, ...)

paperless = Paperless(session=my_session)
```

You also can implement your own session class. The code of `PaperlessSession` isn't too big and easy to understand. Your custom class must at least implement `__init__` and `request` methods, or simply derive it from `PaperlessSession`.

```python
class MyCustomSession(PaperlessSession):
    # start overriding methods
```

### Resource features

| Resource       | Request | Iterate | Create |  Update | Delete |
| -------------- | ------- | ------- | ------ | ------- | ------ |
| config         | x       |         |        |         |
| correspondents | x       | x       | x      | x       | x      |
| custom_fields  | x       | x       | x      | x       | x      |
| document_types | x       | x       | x      | x       | x      |
| documents      | x       | x       | x      | x       | x      |
| groups         | x       | x       |        |         |
| logs           |         |         |        |         |
| mail_accounts  | x       | x       |        |         |
| mail_rules     | x       | x       |        |         |
| saved_views    | x       | x       |        |         |        |
| share_links    | x       | x       | x      | x       | x      |
| storage_paths  | x       | x       | x      | x       | x      |
| tags           | x       | x       | x      | x       | x      |
| tasks          | x       | x\*     |        |         |
| users          | x       | x       |        |         |
| workflows      | x       | x       |        |         |

\*: Only `__aiter__` is supported.

### Requesting data

Retrieving data from Paperless-ngx is really easy, there are different possibilities to achieve that.

#### Getting one item by primary key

You'll need to use that in the most cases, as _PyPaperless_ always returns references to other resource items by their primary keys. You must resolve these references on your own. The returned objects are always `PaperlessModel`s.

```python
document = await paperless.documents(1337)
doc_type = await paperless.document_types(document.document_type) # 23

print(f"Document '{document.title}' is an {doc_type.name}.")
#-> Document 'Order #23: Desktop Table' is an Invoice.
```

The code above executes two http requests:

`GET` `https://localhost:8000/api/documents/1337/` <br>
`GET` `https://localhost:8000/api/document_types/23/`

#### Retrieving a list of primary keys

Since resource items are requested by their primary key, it could be useful to request a list of all available primary keys.

```python
item_keys = await paperless.documents.all()
#-> [1, 2, 3, ...]
```

#### Iterating over resource items

Iteration enables you to execute mass operations of any kind. Like requesting single items, the iterator always returns `PaperlessModel`s.

```python
count = 0
async for item in paperless.documents:
    if item.correspondent == 1:
        count += 1
print(f"{count} documents are currently stored for correspondent 1.")
#-> 5 documents are currently stored for correspondent 1.
```

The code above executes many http requests, depending on your stored documents:

`GET` `https://localhost:8000/api/documents/?page=1` <br>
`GET` `https://localhost:8000/api/documents/?page=2` <br>
`...` <br>
`GET` `https://localhost:8000/api/documents/?page=19`

#### Iterating over pages

Instead of iterating over resource items, you may want to iterate over pagination results in some cases. The `Page` model itself delivers the possibility to check for the existence of previous and next pages, item counts, accessing the raw (`.results`) or processed data (`.items`), and so on.

```python
page_iter = aiter(paperless.documents.pages())
page = await anext(page_iter)
#-> page.current_page == 1
```

The code above executes one http request:

`GET` `https://localhost:8000/api/documents/?page=1`

#### Reducing http requests

Requesting many pages can be time-consuming, so a better way to apply the above filter is using the `reduce` context. Technically, it applies query parameters to the http request, which are interpreted as filters by Paperless-ngx.

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

The code above executes just one http request, but achieves the same:

`GET` `https://localhost:8000/api/documents/?page=1&correspondent__id=1`

> [!NOTE]
> There are many filters available, _PyPaperless_ doesn't provide a complete list. I am working on that. At the moment, you must use the Django Rest framework http endpoint of Paperless-ngx in your browser and play around with the **Filter** button on each resource.
>
> Paperless-ngx simply ignores filters which don't exist and treats them as no filter instead of raising errors, be careful.

> [!TIP]
> The `reduce` context works with all previously mentioned methods: `__aiter__`, `all` and `pages`.

### Manipulating data

_PyPaperless_ offers creation, update and deletion of resource items. These features are enabled where it makes sense, Paperless-ngx itself offers full CRUD functionality. Please check the [resource features](#resource-features) table at the top of this README. If you need CRUD for another resource, let me know and open an [issue](https://github.com/tb1337/paperless-api/issues) with your specific use-case.

#### Creating new items

The process of creating items consists of three parts: retrieving a new draft instance from _PyPaperless_, apply data to it and call `save`. You can choose whether applying data to the draft via `kwargs` or by assigning it to the draft instance, or both. Maybe you want to request the newly created item by the returned primary key and compare it against the data from the draft. If not, you can safely trash the draft instance after saving, as it cannot be saved twice (database constraint violation).

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

#### Updating existing items

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
    "content": ...,
    "correspondents": [...],
    "document_types": [...],
    "storage_paths": [...],
    ...
    // and all other fields
}
```

#### Deleting items

Lust but not least, it is also possible to remove data from Paperless-ngx.

```python
item = await paperless.documents(23)
success = await item.delete()
#-> True
```

The code above executes one http request:

`DELETE` `http://localhost:8000/api/documents/23/`

> [!CAUTION]
> This will permanently delete data from your database. There is no point of return. Be careful

### Special cases

## Thanks to

- The Paperless-ngx Team
- The Home Assistant Community
