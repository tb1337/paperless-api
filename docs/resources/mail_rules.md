# Mail Rules

Mail rules define how Paperless-ngx processes incoming emails from a mail account. Each rule specifies filters (sender, subject, body) and actions to apply when a matching email is found.

## Model

| Field                                | Description                           |
| ------------------------------------ | ------------------------------------- |
| `id`                                 | Primary key                           |
| `name`                               | Display name                          |
| `account`                            | Associated mail account id            |
| `enabled`                            | Whether the rule is active            |
| `folder`                             | IMAP folder to watch                  |
| `filter_from`                        | Filter by sender address              |
| `filter_to`                          | Filter by recipient address           |
| `filter_subject`                     | Filter by subject line                |
| `filter_body`                        | Filter by body content                |
| `filter_attachment_filename_include` | Attachment name include filter        |
| `filter_attachment_filename_exclude` | Attachment name exclude filter        |
| `maximum_age`                        | Max age of emails to process (days)   |
| `action`                             | Action to take on matched emails      |
| `action_parameter`                   | Action parameter (e.g. target folder) |
| `assign_title_from`                  | How to derive the document title      |
| `assign_tags`                        | Tags to assign to imported documents  |
| `assign_correspondent`               | Correspondent id to assign            |
| `assign_document_type`               | Document type id to assign            |
| `assign_owner_from_rule`             | Assign rule owner to the document     |
| `order`                              | Processing order                      |
| `attachment_type`                    | Which attachments to import           |
| `consumption_scope`                  | What to consume from the email        |

## Fetch one

```python
rule = await paperless.mail_rules(3)
print(rule.name)         # "Invoice imports"
print(rule.account)      # 1  (mail account id)
print(rule.enabled)      # True
print(rule.filter_from)  # "billing@vendor.com"
```

## Iterate

```python
async for rule in paperless.mail_rules:
    print(rule.id, rule.name, "enabled:", rule.enabled)

# Only active rules
active = [r async for r in paperless.mail_rules.reduce() if r.enabled]
```

## Permissions

```python
async with paperless.mail_rules.with_permissions():
    rule = await paperless.mail_rules(3)
    print(rule.owner)        # owner user id
    print(rule.permissions)  # Permissions
```

See [Permissions](../concepts/permissions.md) for details.
