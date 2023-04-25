# Paperless API

Async Python wrapper for the paperless-ngx REST API endpoint. Find out more here: https://paperless-ngx.readthedocs.io/en/latest/api.html

It is very simple and stupid. Maybe I will update it in the future to add some nice stuff.

## Examples

Request a list of correspondents and print them.

```python
import asyncio
import pypaperless


async def main():
    api = pypaperless.PaperlessAPI("http://127.0.0.1:9120", "SUPER_SECRET_API_TOKEN_HERE")
    # alternative: api = pypaperless.PaperlessAPI("http://127.0.0.1:9120", username="user", password="pass")

    correspondents = await api.get_correspondents()

    for data in correspondents:
        print(data.raw_data)

asyncio.run(main())
```

Same is possible for every other endpoint provided by the API, excepting logs.

```python
doctypes = await api.get_document_types()
tags = await api.get_tags()
views = await api.get_saved_views()
documents = await api.get_documents()
tasks = await apt.get_tasks()
```

Request a single item by id from an endpoint.
```python
doctype = await api.get_document_type(3)
tag = await api.get_tag(6)
document = await api.get_document(6)
task = await api.get_task(123)
by_task_id = await api.get_task_by_task_id("fdaa724b-xxxx-yyyy-aaf8-edc5c113c656")
```

Post a document to Paperless. Only the file is mandatory, title, creation date correspondent id, and document type id are optional. Tags are crurrently not supported.
```python
await api.post_document("./invoice.pdf",title="Invoice bedroom closet")
```

Search for a document and receive a list of results. Search syntax is the same as in Paperless: https://docs.paperless-ngx.com/usage/#basic-usage_searching.
```python
matching_documents = await api.search("bedroom*")
```
