# Tasks

Tasks represent Celery background jobs — primarily document consumption jobs. You can look up a task by its UUID (returned when uploading a document) or by its integer primary key, and iterate over all tasks.

## Model

| Field              | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `id`               | Integer primary key                                   |
| `task_id`          | Celery UUID string                                    |
| `task_name`        | Internal task name                                    |
| `task_file_name`   | File that triggered this task                         |
| `date_created`     | When the task was queued                              |
| `date_done`        | When the task finished                                |
| `type`             | Task type                                             |
| `status`           | `"PENDING"` / `"STARTED"` / `"SUCCESS"` / `"FAILURE"` |
| `result`           | Result or error message                               |
| `acknowledged`     | Whether the task has been dismissed                   |
| `related_document` | Document id created by this task                      |
| `owner`            | Owner user id                                         |

## Fetch by UUID

The primary use-case is monitoring a document upload by its task UUID:

```python
# task_uuid was returned by paperless.documents.save(draft, raw)
task = await paperless.tasks(task_uuid)

print(task.status)           # "PENDING" / "STARTED" / "SUCCESS" / "FAILURE"
print(task.related_document) # document pk once finished
```

## Fetch by primary key

```python
task = await paperless.tasks(1337)
print(task.task_file_name)  # "invoice.pdf"
```

## Poll until complete

```python
import asyncio

task_uuid = await paperless.documents.save(draft, raw)

while True:
    task = await paperless.tasks(task_uuid)
    if task.status in ("SUCCESS", "FAILURE"):
        break
    await asyncio.sleep(1)

if task.status == "SUCCESS":
    doc = await paperless.documents(task.related_document)
    print("Uploaded:", doc.title)
else:
    print("Upload failed:", task.result)
```

## Iterate

```python
async for task in paperless.tasks:
    print(task.task_id, task.status)

# Collect all pending tasks
pending = [t async for t in paperless.tasks if t.status == "PENDING"]
```
