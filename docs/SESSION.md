# Handling a session

Just import the module and go on.

```python
import asyncio

from pypaperless import Paperless

paperless = Paperless("localhost:8000", "your-secret-token")

# your main function here

asyncio.run(main())
```

Now you can utilize the Paperless object.

**Example 1**

```python
async def main():
  paperless.initialize()
  # do something
  paperless.close()
```

**Example 2**

```python
async def main():
  async with paperless:
    # do something
```

You may want to request or manipulate data. Read more about that here:

* [Request data](REQUEST.md)
* [Create, update, delete data](CRUD.md)
