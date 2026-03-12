# Users

Users are the Paperless-ngx user accounts. They are read-only from the API perspective — only fetching and iterating is supported.

## Model

| Field                   | Description                            |
| ----------------------- | -------------------------------------- |
| `id`                    | Primary key                            |
| `username`              | Login username                         |
| `email`                 | Email address                          |
| `first_name`            | First name                             |
| `last_name`             | Last name                              |
| `date_joined`           | Account creation date                  |
| `is_staff`              | Staff user flag                        |
| `is_active`             | Account active flag                    |
| `is_superuser`          | Superuser flag                         |
| `groups`                | Group ids the user belongs to          |
| `user_permissions`      | Directly assigned permission codenames |
| `inherited_permissions` | Permissions inherited from groups      |
| `is_mfa_enabled`        | Whether MFA is enabled                 |

## Fetch one

```python
user = await paperless.users(1)
print(user.username)    # "admin"
print(user.is_active)   # True
print(user.groups)      # [2, 5]
```

## Iterate

```python
async for user in paperless.users:
    print(user.id, user.username, user.email)

# Username → id lookup
user_map = {u.username: u.id async for u in paperless.users.reduce()}

# Find all superusers
admins = [u async for u in paperless.users.reduce() if u.is_superuser]
```
