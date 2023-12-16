<p align="right">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://docs.paperless-ngx.com/assets/logo_full_white.svg#only-dark">
    <source media="(prefers-color-scheme: light)" srcset="https://docs.paperless-ngx.com/assets/logo_full_black.svg#only-light">
    <img width="200" alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="https://docs.paperless-ngx.com/assets/logo_full_black.svg#only-light">
  </picture>
</p>

<!-- omit in toc -->

# PyPaperless

Little api client for [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)! Find out more here:

* Project: https://docs.paperless-ngx.com
* REST API: https://docs.paperless-ngx.com/api/

## Features

- Depends on aiohttp.
- Token authentication, _note that credentials aren't supported anymore_.
- list requests all object ids of resources.
- get methods for each resources. Accepts page parameters and Django filters and is thus very powerful.
- iterate for each paginated endpoint, you may want to apply some Django filters here, as well.
- create, update, delete methods for documents and their master data endpoints.
- Paperless makes use of pagination. We use that too. You have the full control over how much data to fetch.
- pypaperless is meant to be only the transportation layer. Store and reduce/aggregate data on your own.

## Examples

### Handling a session.

```python
import asyncio

from pypaperless import Paperless

paperless = Paperless("localhost:8000", "your-secret-token")

async def main():
  paperless.initialize()
  # do something
  paperless.close()

  # or just use it in a context
  async with paperless:
    # do something

asyncio.run(main())
```

### Actually request something

```python
# requests one page
documents = await paperless.documents.get(page=1)
for item in documents.items:
  print(f"document #{item.id} has the following content: {item.content}")
```

### Request all items of specific document types and iterate over them
```python
doc_types = [
  "3", # salary
  "8", # contract
  "11", # bank account
]

# iterates over all pages
async for item in paperless.documents.iterate(document_type__id__in=",".join(doc_types)):
  print(f"document #{item.id} has the following content: {item.content}")
```

### Request a specific item
```python
correspondent = await paperless.correspondents.one(23)
```

### Create a new correspondent
```python
from pypaperless.models import CorrespondentPost
from pypaperless.models.shared import MatchingAlgorithm

new_correspondent = CorrespondentPost(
  name="Salty Correspondent",
  match="Give me all your money",
  matching_algorithm=MatchingAlgorithm.ALL,
)
# watch out, the result is a Correspondent object...
created_correspondent = paperless.correspondents.create(new_correspondent)
print(created_correspondent.id) # >> 1337
```

### And delete that salty guy again, including all of his god damn documents!

> [!CAUTION]
> That code actually requests Paperless to physically delete that data! There is no point of return!
> ```python
> # ...
> async for item in paperless.documents.iterate(correspondent__id=1337):
>   await paperless.documents.delete(item)
>
> await paperless.correspondents.delete(created_correspondent)
> ```

## Thanks to

* The Paperless-ngx Team
* The Home Assistant Community
