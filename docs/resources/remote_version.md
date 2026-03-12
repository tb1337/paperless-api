# Remote Version

The `remote_version` resource reports the latest available version of Paperless-ngx as published on GitHub, along with whether an update is available relative to the running instance.

## Model

| Field              | Description |
| ------------------ | ----------- |
| `version`          | Latest available version string  |
| `update_available` | `True` if a newer version exists |

## Fetch

This is a parameter-free call — there is no primary key:

```python
rv = await paperless.remote_version()

print(rv.version)           # "2.13.5"
print(rv.update_available)  # True / False

if rv.update_available:
    print(f"Update available: {rv.version}")
```
