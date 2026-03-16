# Session management

This page covers all configuration modes, custom HTTP clients, API version pinning and connection lifecycle details.

---

## Configuration modes

**pypaperless** can be configured in three ways:

### 1. Explicit parameters

Pass `url` and `token` directly to the constructor:

```python
paperless = Paperless("localhost:8000", "your-api-token")
```

### 2. `PaperlessConfig` object

Build a `PaperlessConfig` instance and pass it via the `config` keyword. Useful when you want to construct or validate settings separately:

```python
from pypaperless import Paperless, PaperlessConfig

cfg = PaperlessConfig(
    url="https://paperless.example.com",
    token="your-api-token",
    request_api_version=9,  # optional — defaults to the built-in value
)

async with Paperless(config=cfg) as paperless:
    ...
```

### 3. Environment variables

Set the `PYPAPERLESS_*` environment variables and call `Paperless()` with no arguments. Ideal for containers, CI pipelines and twelve-factor apps:

| Environment variable              | Field                | Required |
| --------------------------------- | -------------------- | :------: |
| `PYPAPERLESS_URL`                 | Base URL             |    ✓     |
| `PYPAPERLESS_TOKEN`               | API token            |          |
| `PYPAPERLESS_REQUEST_API_VERSION` | API version override |          |

```bash
export PYPAPERLESS_URL=https://paperless.example.com
export PYPAPERLESS_TOKEN=your-api-token
```

```python
async with Paperless() as paperless:
    ...
```

!!! note
    `PYPAPERLESS_URL` is required. If it is not set and no `url` argument is provided, a `ValidationError` is raised immediately.

---

## The `Paperless` constructor reference

```python
Paperless(
    url: str | None = None,
    token: str | None = None,
    *,
    config: PaperlessConfig | None = None,
    client: httpx.AsyncClient | None = None,
    request_api_version: int | None = None,
)
```

| Parameter             | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `url`                 | Hostname, IP address or full URL of your Paperless-ngx instance         |
| `token`               | API token obtained from Paperless-ngx settings                          |
| `config`              | A `PaperlessConfig` instance (alternative to `url` / `token`)           |
| `client`              | Optional custom HTTP client (see below)                                 |
| `request_api_version` | Pin a specific Paperless API version (defaults to the latest supported) |

---

## Lifecycle

### Context manager

The recommended approach — `initialize()` and `close()` are called automatically:

```python
async with Paperless("localhost:8000", "your-api-token") as paperless:
    # fully initialised here
    ...
# connection closed here
```

### Manual

```python
paperless = Paperless("localhost:8000", "your-api-token")
await paperless.initialize()

try:
    # use paperless
    pass
finally:
    await paperless.close()
```

### What `initialize()` does

1. Sends a `GET` request to `/api/schema/` to verify connectivity and authentication.
2. Reads the `x-api-version` and `x-version` response headers.
3. Sets `is_initialized = True`.

Any connectivity or authentication problem raises an exception before `is_initialized` becomes `True`. See [Exceptions](exceptions.md) for details.

---

## Custom HTTP client

You can supply your own `httpx.AsyncClient`. This is useful when you need to:

- Configure timeouts, retries or proxy settings
- Reuse an existing client for connection pooling
- Inject custom headers or SSL certificates

```python
import httpx
from pypaperless import Paperless

custom_client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    verify="/path/to/ca-bundle.pem",
    headers={"X-Custom-Header": "value"},
)

async with Paperless("localhost:8000", "your-api-token", client=custom_client) as paperless:
    ...
```

!!! note
    When you provide a `client`, pypaperless does **not** close it automatically when `close()` is called. You are responsible for managing its lifecycle.

---

## Pinning the API version

By default, pypaperless negotiates the API version from the `x-api-version` response header (currently targeting version **9**). You can override this:

```python
paperless = Paperless("localhost:8000", "your-api-token", request_api_version=8)
```

This can be useful when connecting to an older Paperless-ngx release that does not yet support the latest API version.

---

## Logging

pypaperless uses the standard Python `logging` module under the logger name `pypaperless`.

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

The library logs `INFO`-level messages for `initialize()` and `close()` events.

---

## Available resources

After initialisation, the following services are available on the `Paperless` instance:

| Attribute                  | Resource                    |
| -------------------------- | --------------------------- |
| `paperless.config`         | Application configuration   |
| `paperless.correspondents` | Correspondents              |
| `paperless.custom_fields`  | Custom fields               |
| `paperless.documents`      | Documents                   |
| `paperless.document_types` | Document types              |
| `paperless.groups`         | User groups                 |
| `paperless.mail_accounts`  | Mail accounts               |
| `paperless.mail_rules`     | Mail rules                  |
| `paperless.processed_mail` | Processed mail              |
| `paperless.saved_views`    | Saved views                 |
| `paperless.share_links`    | Share links                 |
| `paperless.statistics`     | Statistics                  |
| `paperless.remote_version` | Remote version info         |
| `paperless.status`         | System status               |
| `paperless.storage_paths`  | Storage paths               |
| `paperless.tags`           | Tags                        |
| `paperless.tasks`          | Background tasks            |
| `paperless.users`          | Users                       |
| `paperless.workflows`      | Workflows                   |
| `paperless.cache`          | Local cache (custom fields) |

See [Resources](resources.md) for the full feature matrix.
