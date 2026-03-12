# Custom Fields

Custom fields let you attach arbitrary typed metadata to documents. This page covers managing the field definitions themselves. For reading and writing field *values* on documents, see [Custom Fields concepts](../custom_fields.md).

## Models

### `CustomField`

| Field        | Description                 |
| ------------ | --------------------------- |
| `id`         | Primary key                 |
| `name`       | Display name                |
| `data_type`  | Field type (see below)      |
| `extra_data` | Type-specific configuration |

**`CustomFieldType` values:** `string`, `longtext`, `url`, `date`, `boolean`, `integer`, `float`, `monetary`, `documentlink`, `select`

### `CustomFieldDraft`

| Field        | Description                       |
| ------------ | --------------------------------- |
| `name`       | Display name *(required on save)* |
| `data_type`  | Field type *(required on save)*   |
| `extra_data` | Type-specific extras              |

## Fetch one

```python
field = await paperless.custom_fields(3)
print(field.name)       # "Invoice amount"
print(field.data_type)  # CustomFieldType.MONETARY
```

## Iterate

```python
async for field in paperless.custom_fields:
    print(field.id, field.name, field.data_type)

# Build a name → id lookup
field_map = {f.name: f.id async for f in paperless.custom_fields.reduce()}
```

## Create

```python
from pypaperless.models.custom_fields import CustomFieldType

draft = paperless.custom_fields.draft()
draft.name = "Invoice amount"
draft.data_type = CustomFieldType.MONETARY

pk = await paperless.custom_fields.save(draft)
```

For a `select` field, provide the allowed options via `extra_data`:

```python
from pypaperless.models.custom_fields import (
    CustomFieldDraft,
    CustomFieldExtraData,
    CustomFieldSelectOptions,
    CustomFieldType,
)

draft = paperless.custom_fields.draft()
draft.name = "Priority"
draft.data_type = CustomFieldType.SELECT
draft.extra_data = CustomFieldExtraData(
    select_options=[
        CustomFieldSelectOptions(label="Low"),
        CustomFieldSelectOptions(label="Medium"),
        CustomFieldSelectOptions(label="High"),
    ]
)

pk = await paperless.custom_fields.save(draft)
```

## Update

```python
field = await paperless.custom_fields(3)
field.name = "Invoice total"
changed = await paperless.custom_fields.update(field)
```

## Delete

```python
field = await paperless.custom_fields(3)
deleted = await paperless.custom_fields.delete(field)
```
