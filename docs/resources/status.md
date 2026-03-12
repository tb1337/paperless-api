# Status

The `status` resource reports the health of the Paperless-ngx server — database connectivity, storage availability, background task workers, and the ML classifier. It is a parameter-free singleton call.

## Model

| Field          | Description                   |
| -------------- | ----------------------------- |
| `pngx_version` | Running Paperless-ngx version |
| `server_os`    | Host operating system         |
| `install_type` | Installation method           |
| `storage`      | Storage usage info            |
| `database`     | Database status               |
| `tasks`        | Background task worker status |

### `StatusStorage`

| Field       | Description                |
| ----------- | -------------------------- |
| `total`     | Total storage in bytes     |
| `available` | Available storage in bytes |

### `StatusDatabase`

| Field              | Description                |
| ------------------ | -------------------------- |
| `type`             | Database engine            |
| `url`              | Connection URL             |
| `status`           | `"OK"` / `"ERROR"`         |
| `error`            | Error message if unhealthy |
| `migration_status` | Migration state            |

### `StatusTasks`

| Field                     | Description                        |
| ------------------------- | ---------------------------------- |
| `redis_url`               | Redis connection URL               |
| `redis_status`            | Redis health                       |
| `celery_status`           | Celery worker health               |
| `index_status`            | Full-text index health             |
| `classifier_status`       | ML classifier health               |
| `classifier_last_trained` | Last classifier training timestamp |
| `sanity_check_status`     | Last sanity check result           |

## Fetch

No primary key — call without arguments:

```python
status = await paperless.status()

print(status.pngx_version)  # "2.13.5"
print(status.server_os)     # "Linux"

# Check storage
if status.storage:
    gb_free = status.storage.available / 1024**3
    print(f"{gb_free:.1f} GB free")

# Check database health
if status.database:
    print(status.database.status)   # "OK"

# Check background workers
if status.tasks:
    print(status.tasks.celery_status)  # "OK"
    print(status.tasks.redis_status)   # "OK"

# Convenience method for any errors present
if status.has_errors():
    print("One or more components are unhealthy!")
```
