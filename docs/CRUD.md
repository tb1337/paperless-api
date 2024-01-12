# Create, Update, Delete

If you plan to manipulate your Paperless data, continue reading. Manipulation is the process of inserting, updating and deleting data from and to your Paperless database.

In the following examples, we assume you already have initialized the `Paperless` object in your code.

- [Supported resources](#supported-resources)
- [Default operations](#default-operations)
  - [Update items](#update-items)
  - [Create items](#create-items)
  - [Delete items](#delete-items)
- [Special cases](#special-cases)
  - [Document Notes](#document-notes)
  - [Document Custom Fields](#document-custom-fields)

## Supported resources

_PyPaperless_ enables create/update/delete wherever it makes sense:

- correspondents
- custom_fields
- document_types
- documents
  - custom_fields
  - notes
  - _metadata_ is not supported
- share_links
- storage_paths
- tags

## Default operations

### Update items

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

### Create items

It absolutely makes sense to create new data in the Paperless database, especially documents. Therefore, item creation is implemented for many resources. It differs slightly from `update()` and `delete()`. _PyPaperless_ doesn't validate data, its meant to be the transportation layer between your code and Paperless only. To reduce common mistakes, it provides special classes for creating new items. Use them.

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
#>>> Correspondent(id=1337, name="Salty correspondent", ...)
```

Every `create()` call will send a `POST` http request to Paperless, containing the full serialized item.

### Delete items

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

## Special cases

There are some resources that differ from default operations. Luckily you wouldn't need that very often.

### Document Notes

Document notes are treated as a sub-resource by Paperless and got some special handling on requesting, creating and deleting.

> [!NOTE]
> Updating existing document notes is currently impossible due to Paperless api limitations.

**There are two ways of requesting document notes:**

```python
# request a document and access its notes property
document = await paperless.documents.one(23)
#>>> Document(..., notes=[
#>>>    DocumentNote(id=1, note="Sample note.", document=23, user=1, created=datetime.datetime()),
#>>>    ...
#>>> ], ...)

# request document notes by applying a document id or object
notes = await p.documents.notes.get(23)
notes = await p.documents.notes.get(document)
#>>> [
#>>>    DocumentNote(id=1, note="Sample note.", document=23, user=1, created=datetime.datetime()),
#>>>    ...
#>>> ]
```

**Lets create and delete document notes:**

```python
# add new note to a document
from pypaperless.models import DocumentNotePost

note = DocumentNotePost(note="New sample note.", document=23)
await p.documents.notes.create(note)  # we defined the document id in the Post model

# deleting document notes can be tricky, you need the
# DocumentNote object for it, which will be a very rare case
document_note = (await p.documents.notes.get(23)).pop()
await p.documents.notes.delete(document_note)
```

### Document Custom Fields

Custom Fields are managed in the Paperless configuration. _PyPaperless_ enables you to attach values for them to your documents. Currently, they are of _Any_ type, so you must pay attention to their actual values.

On calling the persistence method, the complete list of CustomFieldValues will replace the current one. That could lead to unintended changes: if you persist an empty list, all fields are removed from the document.

> [!CAUTION]
> You could overwrite or delete all of your Custom Field attachments to a document, so be careful. I want to overhaul the Custom Field feature somewhere in the future.

```python
# request a document and access its custom fields
document = await paperless.documents.one(42)
#>>> Document(..., custom_fields=[
#>>>    CustomFieldValue(field=1, value="I am a field value"),
#>>>    CustomFieldValue(field=2, value=True),
#>>>    ...
#>>> ], ...)

# you can do everything with that list, append, pop, etc.
# as long as list values are of type CustomFieldValue
fields = document.custom_fields
fields.pop()
fields.append(CustomFieldValue(field=2, value=False))

# persist changes. the list is taken as-is and replaces the current one
document = paperless.documents.custom_fields(document, fields)
#>>> Document(..., custom_fields=[ ...
#>>>    CustomFieldValue(field=2, value=False),
#>>>    ...
#>>> ], ...)

```
