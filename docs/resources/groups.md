# Groups

Groups are Paperless-ngx user groups used for permission management. They are read-only from the API perspective — groups can only be fetched and iterated, not created or modified via pypaperless.

## Model

| Field         | Description                                      |
| ------------- | ------------------------------------------------ |
| `id`          | Primary key                                      |
| `name`        | Group name                                       |
| `permissions` | Django permission codenames granted to the group |

## Fetch one

```python
group = await paperless.groups(2)
print(group.name)         # "Administrators"
print(group.permissions)  # ["view_document", "change_document", ...]
```

## Iterate

```python
async for group in paperless.groups:
    print(group.id, group.name)

# Build a name → id lookup
group_map = {g.name: g.id async for g in paperless.groups.filter()}
```
