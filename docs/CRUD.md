# Create, Update, Delete

If you plan to manipulate your Paperless data, continue reading. Manipulation is the process of inserting, updating and deleting data from and to your Paperless database.

In the following examples, we assume you already have initialized the `Paperless` object in your code.

- [Supported resources](#supported-resources)
- [Update items](#update-items)
- [Create items](#create-items)
- [Delete items](#delete-items)

## Supported resources

*PyPaperless* enables create/update/delete wherever it makes sense:

* correspondents
* custom_fields
* document_types
* documents
    * custom_fields
    * *metadata* is not supported
    * *notes* are currently not supported ([#23](https://github.com/tb1337/paperless-api/issues/23))
* share_links
* storage_paths
* tags

## Update items

The Paperless api enables us to change almost everything via REST. Personally, I use that to validate document titles, as I have declared naming conventions to document types. I try to apply the correct title to the document, and if that fails for some reason, it gets a _TODO_ tag applied. So I can edit manually later on.

> [!TIP]
> You may have other use-cases. Feel free to share them with me by opening an [issue](https://github.com/tb1337/paperless-api/issues).

Updating is as easy as requesting items. Gather any resource item object, update its attributes and call the `update()` method of the endpoint.

**Example 1**

```python
document = await paperless.documents.one(42)
document.title = "42 - The Answer"
document.content = """
The Answer to the Ultimate Question of Life,
the Universe, and Everything.
"""
document = await paperless.documents.update(document)
#>>> Document(id=42, title="42 - The Answer", content="...", ...)
```

**Example 2**

```python
filters = {
    "title__istartswith": "invoice",
}
async for item in paperless.documents.iterate(**filters):
    item.title = item.title.replace("invoice", "bill")
    await paperless.documents.update(item)
```

Every `update()` call will send a `PUT` http request to Paperless, containing the full serialized item. That behaviour will be refactored in the future. Only changed attributes will be sent via `PATCH` http requests. ([#24](https://github.com/tb1337/paperless-api/issues/24))

## Create items

It absolutely makes sense to create new data in the Paperless database, especially documents. Therefore, item creation is implemented for many resources. It differs slightly from `update()` and `delete()`. *PyPaperless* doesn't validate data, its meant to be the transportation layer between your code and Paperless only. To reduce common mistakes, it provides special classes for creating new items. Use them.

For every creatable resource exists a *Resource*Post class. Instantiate that class with some data and call the `create()` method of your endpoint. There you go.

**Example for documents**

```python
from pypaperless.models import DocumentPost

# or read the contents of a file, whatver you want
content = b"..."

# there are more attributes available, check type hints
new_document = DocumentPost(document=content)
task_id = await paperless.documents.create(new_document)
#>>> abcdefabcd-efab-cdef-abcd-efabcdefabcd
```

> [!TIP]
> You can access the current OCR status of your new document when requesting the `tasks` endpoint with that id.

**Example for other resources**

```python
from pypaperless.models import CorrespondentPost
from pypaperless.models.shared import MatchingAlgorithm

new_correspondent = CorrespondentPost(
  name="Salty correspondent",
  match="Give me all your money",
  matching_algorithm=MatchingAlgorithm.ALL,
)
# watch out, the result is a Correspondent object...
created_correspondent = paperless.correspondents.create(new_correspondent)
print(created_correspondent.id)
# >> 1337
```

Every `create()` call will send a `POST` http request to Paperless, containing the full serialized item.

## Delete items

In some cases, you want to delete items. Its almost the same as updating, just call the `delete()` method. Lets delete that salty guy again, including all of his documents!

> [!CAUTION]
> This will permanently delete data from your Paperless database. There is no point of return.

```python
# ...
filters = {
    "correspondent__id": new_correspondent.id
}
async for item in paperless.documents.iterate(**filters):
    await paperless.documents.delete(item)

await paperless.correspondents.delete(created_correspondent)
```

Every `delete()` call will send a `DELETE` http request to Paperless without any payload.
