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

| Field              | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `type`             | Database engine                                        |
| `url`              | Connection URL                                         |
| `status`           | `"OK"` / `"ERROR"`                                     |
| `error`            | Error message if unhealthy                             |
| `migration_status` | `StatusDatabaseMigration` object (see below)           |

### `StatusDatabaseMigration`

| Field                  | Description                       |
| ---------------------- | --------------------------------- |
| `latest_migration`     | Name of the latest applied migration |
| `unapplied_migrations` | List of pending migration names  |

### `StatusTasks`

| Field                     | Description                                   |
| ------------------------- | --------------------------------------------- |
| `redis_url`               | Redis connection URL                          |
| `redis_status`            | Redis health (`"OK"` / `"ERROR"`)              |
| `redis_error`             | Redis error message if unhealthy              |
| `celery_url`              | Celery broker URL                             |
| `celery_status`           | Celery worker health (`"OK"` / `"ERROR"`)      |
| `celery_error`            | Celery error message if unhealthy             |
| `index_status`            | Full-text index health (`"OK"` / `"ERROR"`)   |
| `index_last_modified`     | Timestamp of last index modification         |
| `index_error`             | Index error message if unhealthy              |
| `classifier_status`       | ML classifier health (`"OK"` / `"ERROR"`)     |
| `classifier_last_trained` | Last classifier training timestamp           |
| `classifier_error`        | Classifier error message if unhealthy        |
| `sanity_check_status`     | Last sanity check result (`"OK"` / `"ERROR"`) |
| `sanity_check_last_run`   | Timestamp of last sanity check               |
| `sanity_check_error`      | Sanity check error message if unhealthy      |

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
