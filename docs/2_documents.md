# Working with documents

Some *Paperless-ngx* resources provide more features as others, especially when it comes to `Documents`. Lets take a closer look!

## Documentation

* [Basic Usage](1_basic_usage.md)
* [Working with documents](2_documents.md) - This page ;)
* [Working with custom fields](3_custom_fields.md)
* [Permissions](4_permissions.md)

---

**On this page:**

- [Binary image/pdf data](#binary-imagepdf-data)
- [Lookup specific documents](#lookup-specific-documents)
  - [1. Search query](#1-search-query)
  - [2. More like](#2-more-like)
  - [Search results](#search-results)
- [Metadata](#metadata)
- [Notes](#notes)
- [Suggestions](#suggestions)
- [Next available ASN](#next-available-asn)

## Binary image/pdf data

You can access the binary image/pdf data by using the following methods. They all return a `DownloadedDocument` class instance, which holds the actual binary data and provides some more useful attributes, like content type, disposition type and filename.

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

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/download/` <br>
> `GET` `https://localhost:8000/api/documents/23/preview/` <br>
> `GET` `https://localhost:8000/api/documents/23/thumb/`

## Lookup specific documents

If you want to search for documents, *Paperless-ngx* offers two possibilities to achieve that. **pypaperless** implements two iterable shortcuts for that.

### 1. Search query

Search query documentation: https://docs.paperless-ngx.com/usage/#basic-usage_searching

```python
async for document in paperless.documents.search("type:invoice"):
    # do something
```

> [!NOTE] Executed http requests
> The code above executes many http requests, depending on the count of your matched documents:
>
> `GET` `https://localhost:8000/api/documents/?page=1&query=type%3Ainvoice` <br>
> `GET` `https://localhost:8000/api/documents/?page=2&query=type%3Ainvoice` <br>
> `...` <br>
> `GET` `https://localhost:8000/api/documents/?page=19&query=type%3Ainvoice`

### 2. More like

Search for similar documents like the permitted document primary key.

```python
async for document in paperless.documents.more_like(23):
    # do something
```

> [!NOTE] Executed http requests
> The code above executes many http requests, depending on the count of your matched documents:
>
> `GET` `https://localhost:8000/api/documents/?page=1&more_like_id=23` <br>
> `GET` `https://localhost:8000/api/documents/?page=2&more_like_id=23` <br>
> `...` <br>
> `GET` `https://localhost:8000/api/documents/?page=19&more_like_id=23`

### Search results

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

## Metadata

*Paperless-ngx* stores some metadata about your documents. If you wish to access them, there are two ways to achieve that.

**Example 1: Provide a primary key**

```python
metadata = await paperless.documents.metadata(23)
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/metadata/`

**Example 2: Already fetched item**

```python
document = await paperless.documents(23)
metadata = await document.get_metadata()
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/` <br>
> `GET` `https://localhost:8000/api/documents/23/metadata/`

## Notes

Documents can be commented with so-called notes. *Paperless-ngx* supports requesting, creating and deleting those. **pypaperless** includes built-in support for it, too.

**Getting notes**

Document notes are always available as `list[DocumentNote]` after requesting them.

There are two ways of requesting document notes:

```python
# by primary key
list_of_notes = await paperless.documents.notes(23)
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/notes/`

or

```python
# by already fetched item
document = await paperless.documents(23)
list_of_notes = await document.notes()
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/` <br>
> `GET` `https://localhost:8000/api/documents/23/notes/`

**Creating notes**

You can add new notes. Updating existing notes isn't possible due to *Paperless-ngx* API limitations.

There are two ways of creating a new note draft:

```python
# by document primary key
draft = paperless.documents.notes.draft(23)
```

or

```python
# by already fetched document
document = await paperless.documents(23)

draft = document.notes.draft()
```

After creating the draft, do your work with it and tell *Paperless-ngx* to store it:

```python
draft.note = "Lorem ipsum"

new_note_pk, document_pk = await draft.save()
#-> 42, 23
```

> [!NOTE] Executed http requests
> `POST` `https://localhost:8000/api/documents/23/notes/`

**Deleting notes**

Sometimes it may be necessary to delete document notes.

> [!CAUTION]
> This will permanently delete data from your database. There is no way to recover deleted data. Be careful.

```python
a_note = list_of_notes.pop() # document note with example pk 42
success = await a_note.delete()
#-> True
```

> [!NOTE] Executed http requests
> `DELETE` `https://localhost:8000/api/documents/23/notes/?id=42`

## Suggestions

One of the key functionalities of *Paperless-ngx* is _classification_: it is the workflow of assigning classifiers to your documents, like correspondents or tags. *Paperless-ngx* does that by auto-assigning or suggesting them to you. These suggestions can be accessed by **pypaperless**, as well.

**Example 1: Provide a primary key**

```python
suggestions = await paperless.documents.suggestions(23)
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/suggestions/`

**Example 2: Already fetched item**

```python
document = await paperless.documents(23)
suggestions = await document.get_suggestions()
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/23/` <br>
> `GET` `https://localhost:8000/api/documents/23/suggestions/`

The returned `DocumentSuggestions` instance stores a list of suggested resource items for each classifier: correspondents, tags, document_types, storage_paths and dates.

This is what the raw data looks like:

```json
{
  "correspondents": [
    11
  ],
  "tags": [1, 33, 7],
  "document_types": [
    15
  ],
  "storage_paths": [
    2
  ],
  "dates": [
    "2023-01-02",
    "2024-03-04",
    "2025-05-06"
  ]
}
```

## Next available ASN

Simply returns the next available archive serial number as `int`.

```python
next_asn = await paperless.documents.get_next_asn()
#-> 1337
```

> [!NOTE] Executed http requests
> `GET` `https://localhost:8000/api/documents/next_asn/`
