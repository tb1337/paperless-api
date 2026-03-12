# Mail Accounts

Mail accounts are the IMAP mailbox configurations that Paperless-ngx polls for incoming documents. They support fetching and iterating, with permission information available on request.

## Model

| Field           | Description                           |
| --------------- | ------------------------------------- |
| `id`            | Primary key                           |
| `name`          | Display name                          |
| `imap_server`   | IMAP hostname                         |
| `imap_port`     | IMAP port                             |
| `imap_security` | Security mode (None / SSL / STARTTLS) |
| `username`      | IMAP username                         |
| `character_set` | Mailbox character set                 |
| `is_token`      | Whether OAuth token auth is used      |
| `account_type`  | Account type identifier               |
| `expiration`    | Token expiry date                     |

## Fetch one

```python
account = await paperless.mail_accounts(1)
print(account.name)        # "My Gmail"
print(account.imap_server) # "imap.gmail.com"
print(account.username)    # "user@gmail.com"
```

## Iterate

```python
async for account in paperless.mail_accounts:
    print(account.id, account.name)

# All accounts as a dict keyed by id
accounts = await paperless.mail_accounts.as_dict()
```

## Permissions

```python
paperless.mail_accounts.request_permissions = True
account = await paperless.mail_accounts(1)

print(account.owner)        # owner user id
print(account.permissions)  # PermissionTable

paperless.mail_accounts.request_permissions = False
```

See [Permissions](../concepts/permissions.md) for details.
