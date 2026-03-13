# Processed Mail

The `processed_mail` resource is a read-only log of emails that have already been processed by a mail rule. Each entry records the outcome of the import attempt.

## Model

| Field       | Description                                      |
| ----------- | ------------------------------------------------ |
| `id`        | Primary key                                      |
| `owner`     | User id of the rule owner                        |
| `rule`      | Mail rule id that processed this email           |
| `folder`    | IMAP folder the email was found in               |
| `uid`       | IMAP UID of the email                            |
| `subject`   | Email subject line                               |
| `received`  | When the email was received                      |
| `processed` | When Paperless processed the email               |
| `status`    | Processing status (e.g. `"success"`, `"failed"`) |
| `error`     | Error message if processing failed               |

## Fetch one

```python
entry = await paperless.processed_mail(5)
print(entry.subject)   # "RE: Invoice #1234"
print(entry.status)    # "success"
print(entry.processed) # datetime(2024, 3, 15, 10, 30, ...)
```

## Iterate

```python
async for entry in paperless.processed_mail:
    if entry.status == "failed":
        print(f"Failed: {entry.subject} — {entry.error}")

# Collect all failures
failures = [
    e async for e in paperless.processed_mail.filter()
    if e.status == "failed"
]
```

## Permissions

```python
async with paperless.processed_mail.with_permissions():
    entry = await paperless.processed_mail(5)
    print(entry.owner)
```

See [Permissions](../concepts/permissions.md) for details.
