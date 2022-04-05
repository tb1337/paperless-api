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
```
