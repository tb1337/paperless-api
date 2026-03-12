# Profile

The `profile` resource exposes the Paperless-ngx user profile for the currently authenticated token. It is a parameter-free singleton call and supports partial updates via `update()`.

## Model

### `Profile`

| Field                 | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `email`               | User e-mail address                                        |
| `password`            | Password placeholder (masked by the API)                   |
| `first_name`          | First name                                                 |
| `last_name`           | Last name                                                  |
| `auth_token`          | The API token for the current user (read-only)             |
| `social_accounts`     | Linked social / OAuth accounts                             |
| `has_usable_password` | Whether a usable password is set (read-only)               |
| `is_mfa_enabled`      | Whether multi-factor authentication is enabled (read-only) |

### `ProfileSocialAccount`

| Field      | Description                        |
| ---------- | ---------------------------------- |
| `id`       | Social account id                  |
| `provider` | OAuth provider identifier string   |
| `name`     | Display name of the linked account |

## Fetch

No primary key — call without arguments:

```python
profile = await paperless.profile()

print(profile.email)               # "admin@example.com"
print(profile.first_name)          # "Admin"
print(profile.auth_token)          # "3e9505078d32d8ad4ecea00fa0eec8e426622b52"
print(profile.has_usable_password) # True
print(profile.is_mfa_enabled)      # False

for account in profile.social_accounts or []:
    print(account.provider, account.name)
```

## Update

Use `update()` to partially update the profile. Only the supplied keyword arguments are sent to the API:

```python
updated = await paperless.profile.update(
    first_name="Jane",
    last_name="Doe",
    email="jane@example.com",
)

print(updated.first_name)  # "Jane"
```

Supported keyword arguments:

| Argument     | Description             |
| ------------ | ----------------------- |
| `email`      | New e-mail address      |
| `password`   | New plain-text password |
| `first_name` | New first name          |
| `last_name`  | New last name           |

`update()` returns a refreshed `Profile` instance reflecting the server response.
