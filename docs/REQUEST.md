# Requesting data

It's all about accessing data, that's obviously the reason you downloaded *PyPaperless*.

In the following examples, we assume you already have initialized the `Paperless` object in your code.

- [Basic requests](#basic-requests)
    - [Requesting a list of pk's](#requesting-a-list-of-pks)
    - [Requesting an item](#requesting-an-item)
    - [Requesting paginated items of a resource](#requesting-paginated-items-of-a-resource)
    - [Iterating over all resource items](#iterating-over-all-resource-items)
- [Filtered requests](#filtered-requests)
    - [Requesting filtered pages of a resource](#requesting-filtered-pages-of-a-resource)
    - [Iterating over filtered resource items](#iterating-over-filtered-resource-items)
- [Further information](#further-information)

## Basic requests

The following examples should solve the most use-cases.

### Requesting a list of pk's

Paperless returns a JSON key *all* on every paginated request, which represents a list of all pk's matching our filtered request. The `list()` method requests page one unfiltered, resulting in getting a complete list.

```python
correspondent_pks = await paperless.correspondents.list()
#>>> [1, 2, 3, ...]
```

It's the same for each resource. Let's try with documents:

```python
document_pks = await paperless.documents.list()
#>>> [5, 23, 42, 1337, ...]
```

### Requesting an item

You may want to actually access the data of Paperless resources. Lets do it!

```python
# request document with pk 23
document = await paperless.documents.one(23)
#>>> Document(id=23, ...)
```

### Requesting paginated items of a resource

Accessing single resources by pk would result in too many requests, so you can access the paginated results, too.

```python
# request page 1
documents = await paperless.documents.get()
#>>> PaginatedResult(current_page=1, next_page=2, items=[Document(...), ...])

# request page 2
documents = await paperless.documents.get(page=2)
#>>> PaginatedResult(current_page=2, next_page=3, items=[Document(...), ...])
```

If you are requesting the last page, the `next_page` property would be `None`.

### Iterating over all resource items

Sometimes, dealing with pages makes no sense for you, so you may want to iterate over all items at once.

> ![NOTE]
> Iterating over all documents could take some time, depending on how many items you have stored in your database.

```python
async for item in paperless.documents.iterate():
    print(item.title)
    #>>> 'New Kitchen Invoice'
```

## Filtered requests

Sometimes, you want to filter results in order to access them faster, or to apply context to your requests, or both. In case of documents, iterating over them can be very time-consuming. The Paperless api provides filter query attributes for each resource. There are **many** filters, so I cannot list them all. The easiest way to find them out is accessing the Api Root of your local Paperless installation, by adding `/api/` to the url.

For example: `http://localhost:8000/api/`

Once the list of all api endpoints is available, choose your resource by clicking the link next to the name. If a **Filter** button is displayed on the top of the next page, filtering is supported by the resource. Click the button to access all available filters, apply a dummy filter and click on the **Apply** button.
The website now displays something like that under the heading resource name:
`GET /api/documents/?id__in=&id=&title__istartswith=&title__iendswith=&title__icontains=...`

The names of the query parameters are available as keywords in the `get()`and `ìterate()` methods.

### Requesting filtered pages of a resource

Filters are passed as keywords to the `get()` method.

```python
filters = {
    "title__istartswith": "invoice",
    "content__icontains": "cheeseburger",
}
filtered_documents = await paperless.documents.get(**filters)
#>>> PaginatedResult(current_page=1, next_page=None, items=[Document(...), ...])
```

### Iterating over filtered resource items

Iterating is also possible with filters and works the same way as requesting filtered pages.

```python
# we assume you have declared the same filter dict as above
async for item in paperless.documents.iterate(**filters):
    print(item.title)
    #>>> 'Invoice for yummy cheeseburgers'
```

> ![NOTE]
> Paperless simply ignores filters which don't exist. You could end up iterating over all of your documents, which will take time in the worst case. Use filters carefully and check twice.

## Further information

Each `list()` and `get()` call results in a single `GET` http request. When using `iterate()`, 1-n `GET` http requests will be sent until all pages are requested.
