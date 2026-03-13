# Saved Views

Saved views are named document filter presets that can be pinned to the dashboard or sidebar in the Paperless-ngx web UI. They support fetching and iterating, with permission information available on request.

## Model

| Field               | Description                                     |
| ------------------- | ----------------------------------------------- |
| `id`                | Primary key                                     |
| `name`              | Display name                                    |
| `show_on_dashboard` | Pin to web UI dashboard                         |
| `show_in_sidebar`   | Show in web UI sidebar                          |
| `sort_field`        | Field to sort results by                        |
| `sort_reverse`      | Sort in descending order                        |
| `filter_rules`      | Active filter rules                             |
| `page_size`         | Number of documents per page                    |
| `display_mode`      | Layout mode (`"table"` / `"smallCards"` / etc.) |
| `display_fields`    | Visible column field names                      |

### `SavedViewFilterRule`

| Field       | Description            |
| ----------- | ---------------------- |
| `rule_type` | Filter type identifier |
| `value`     | Filter value           |

## Fetch one

```python
view = await paperless.saved_views(2)
print(view.name)               # "Inbox"
print(view.show_on_dashboard)  # True
print(view.filter_rules)       # [SavedViewFilterRule(...), ...]
```

## Iterate

```python
async for view in paperless.saved_views:
    print(view.id, view.name)

# Only views shown in the sidebar
sidebar_views = [
    v async for v in paperless.saved_views.filter()
    if v.show_in_sidebar
]
```

## Permissions

```python
async with paperless.saved_views.with_permissions():
    view = await paperless.saved_views(2)
    print(view.owner)        # owner user id
    print(view.permissions)  # Permissions
```

See [Permissions](../concepts/permissions.md) for details.
