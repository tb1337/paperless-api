# Handling a session

- [Connect to Paperless-ngx](#connect-to-paperless-ngx)
  - [Some rules](#some-rules)
  - [By url object](#by-url-object)
  - [By url string](#by-url-string)
  - [Force usage of http](#force-usage-of-http)
  - [More](#more)
    - [Customize aiohttp.ClientSession](#customize-aiohttpclientsession)
    - [Customize aiohttp.ClientSession.request](#customize-aiohttpclientsessionrequest-kwargs)
- [Start working with your data](#start-working-with-your-data)

Just import the module and go on.

```python
import asyncio

from pypaperless import Paperless

paperless = Paperless("localhost:8000", "your-secret-token")

# your main function here

asyncio.run(main())
```

## Connect to Paperless-ngx

*PyPaperless* makes use of *YARL* and applies some logic to the path when instantiating the Paperless object.

### Some rules

*PyPaperless* checks the passed urls and magically makes things work for you. Or not, in some cases. So be aware of the following rules:

1. Isn't a scheme applied to it? Apply `https`.
2. Is `http` explicitly used in it? Okay, continue with `http` :dizzy_face:.
3. Doesn't it end with `/api`? Append `/api`.

### By url object

```python
from yarl import URL

# your desired URL object
url = URL("homelab.lan").with_path("/path/to/paperless")
paperless = Paperless(url, "your-secret-token")
```

Connects to `https://homelab.lan/path/to/paperless/api`.

### By url string

If you don't want to create a YARL url object, simply pass a string to the Paperless object.

```python
paperless = Paperless("paperless.lan", "your-secret-token")
```

Connects to `https://paperless.lan/api`.

### Force usage of http

As mentioned above, `http` is also possible. Just call is explicitly.

```python
paperless = Paperless("http://paperless.lan", "your-secret-token")
```

Connects to `http://paperless.lan/api`.

It is not possible to force `http`-usage by just applying a port number. `paperless.lan:80` will result in connecting to it via `https`, even if it seems odd. Well, use `scheme://` which is a far more clear intention, and everything is fine.

### More

#### Customize `aiohttp.ClientSession`

If you want to use an already existing `aiohttp.ClientSession`, pass it to the Paperless object.

```python
import aiohttp

your_session = aiohttp.ClientSession()

paperless = Paperless("your-url", "your-token", session=your_session)
```

#### Customize `aiohttp.ClientSession.request` kwargs

You may want to pass custom data (f.e. ssl context) to the `request()` method, which is internally called by *PyPaperless* on each http-request. Pass it to the Paperless object.

```python
paperless = Paperless("your-url", "your-token", request_opts={...})
```

## Start working with your data

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
