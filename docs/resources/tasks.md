# Tasks

Tasks represent Celery background jobs - primarily document consumption jobs. You can look up a task by its UUID (returned when uploading a document) or by its integer primary key, and iterate over all tasks.

## Model

See [`pypaperless/models/tasks.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/tasks.py) for all fields and [`pypaperless/models/types.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/types.py) for enum and filter types, and the [Paperless-ngx API docs](https://docs.paperless-ngx.com/api/) for the upstream schema.

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

## Filter

```python
# Only tasks with a specific status
async for task in paperless.tasks.filter(status="SUCCESS"):
    print(task.task_id, task.result)

# Only unacknowledged consumption tasks
async for task in paperless.tasks.filter(acknowledged=False, type="ConsumptionTask"):
    print(task.task_id)
```

## Acknowledge tasks

```python
# Service action
count = await paperless.tasks.acknowledge([1, 2, 3])
print("Acknowledged:", count)

# Model shortcut
task = await paperless.tasks(1)
await task.acknowledge()
```

## Run task

```python
# Service action (by Celery task UUID)
rerun = await paperless.tasks.run("123e4567-e89b-12d3-a456-426614174000")
print(rerun.status)

# Model shortcut
task = await paperless.tasks(1)
rerun = await task.run()
```
