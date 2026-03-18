# Saved Views

Saved views are named document filter presets that can be pinned to the dashboard or sidebar in the Paperless-ngx web UI. They support fetching and iterating, with permission information available on request.

## Model

See [`pypaperless/models/saved_views.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/saved_views.py) for all fields and [`pypaperless/models/types.py`](https://github.com/tb1337/paperless-api/blob/main/pypaperless/models/types.py) for enum and filter types, and the [Paperless-ngx API docs](https://docs.paperless-ngx.com/api/) for the upstream schema.

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
    v async for v in paperless.saved_views
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
