# Workflows

Workflows automate document processing in Paperless-ngx. Each workflow has one or more **triggers** (conditions that activate it) and one or more **actions** (what to do when triggered). Triggers and actions are accessible as sub-resources via `paperless.workflows.triggers` and `paperless.workflows.actions`.

## Models

### `Workflow`

| Field      | Description                    |
| ---------- | ------------------------------ |
| `id`       | Primary key                    |
| `name`     | Display name                   |
| `order`    | Execution priority             |
| `enabled`  | Whether the workflow is active |
| `triggers` | Trigger ids / objects          |
| `actions`  | Action ids / objects           |

### `WorkflowTrigger`

| Field                              | Description                                     |
| ---------------------------------- | ----------------------------------------------- |
| `id`                               | Primary key                                     |
| `type`                             | Trigger type                                    |
| `sources`                          | Consumption sources                             |
| `filter_filename`                  | Filename pattern filter                         |
| `filter_path`                      | Path pattern filter                             |
| `filter_mailrule`                  | Mail rule id filter                             |
| `filter_has_tags`                  | Required tags (document must have all of these) |
| `filter_has_all_tags`              | Required tags (all must match)                  |
| `filter_has_not_tags`              | Excluded tags (none may match)                  |
| `filter_custom_field_query`        | Custom field query expression                   |
| `filter_has_correspondent`         | Required correspondent id                       |
| `filter_has_not_correspondents`    | Excluded correspondent ids                      |
| `filter_has_document_type`         | Required document type id                       |
| `filter_has_not_document_types`    | Excluded document type ids                      |
| `filter_has_storage_path`          | Required storage path id                        |
| `filter_has_not_storage_paths`     | Excluded storage path ids                       |
| `schedule_offset_days`             | Scheduled trigger day offset                    |
| `schedule_is_recurring`            | Whether the schedule repeats                    |
| `schedule_recurring_interval_days` | Interval in days for recurring schedules        |
| `schedule_date_field`              | Date field used for schedule evaluation         |
| `schedule_date_custom_field`       | Custom field id used as the schedule date       |

### `WorkflowAction`

| Field                         | Description                                |
| ----------------------------- | ------------------------------------------ |
| `id`                          | Primary key                                |
| `type`                        | Action type                                |
| `assign_title`                | Title template to assign                   |
| `assign_tags`                 | Tags to assign                             |
| `assign_correspondent`        | Correspondent id to assign                 |
| `assign_document_type`        | Document type id to assign                 |
| `assign_storage_path`         | Storage path id to assign                  |
| `assign_owner`                | Owner user id to assign                    |
| `assign_view_users`           | User ids to grant view permission          |
| `assign_view_groups`          | Group ids to grant view permission         |
| `assign_change_users`         | User ids to grant change permission        |
| `assign_change_groups`        | Group ids to grant change permission       |
| `assign_custom_fields`        | Custom field ids to assign                 |
| `assign_custom_fields_values` | Values for the assigned custom fields      |
| `remove_all_tags`             | Remove all existing tags                   |
| `remove_tags`                 | Tag ids to remove                          |
| `remove_all_correspondents`   | Remove all existing correspondents         |
| `remove_correspondents`       | Correspondent ids to remove                |
| `remove_all_document_types`   | Remove all existing document types         |
| `remove_document_types`       | Document type ids to remove                |
| `remove_all_storage_paths`    | Remove all existing storage paths          |
| `remove_storage_paths`        | Storage path ids to remove                 |
| `remove_all_custom_fields`    | Remove all existing custom fields          |
| `remove_custom_fields`        | Custom field ids to remove                 |
| `remove_all_owners`           | Remove all existing owners                 |
| `remove_owners`               | Owner ids to remove                        |
| `remove_all_permissions`      | Remove all existing permissions            |
| `remove_view_users`           | User ids to revoke view permission from    |
| `remove_view_groups`          | Group ids to revoke view permission from   |
| `remove_change_users`         | User ids to revoke change permission from  |
| `remove_change_groups`        | Group ids to revoke change permission from |
| `email`                       | Email notification config                  |
| `webhook`                     | Webhook notification config                |

## Workflows

### Fetch one

```python
workflow = await paperless.workflows(1)
print(workflow.name)     # "Auto-tag invoices"
print(workflow.enabled)  # True
```

### Iterate

```python
async for wf in paperless.workflows:
    print(wf.id, wf.name, "enabled:", wf.enabled)

# Only active workflows
active = [wf async for wf in paperless.workflows.filter() if wf.enabled]
```

## Triggers

Triggers are accessed via `paperless.workflows.triggers`:

```python
# Fetch a trigger by id
trigger = await paperless.workflows.triggers(3)
print(trigger.type)            # WorkflowTriggerType.CONSUMPTION
print(trigger.filter_filename) # "invoice_*.pdf"

# Iterate all triggers
async for trigger in paperless.workflows.triggers:
    print(trigger.id, trigger.type)
```

## Actions

Actions are accessed via `paperless.workflows.actions`:

```python
# Fetch an action by id
action = await paperless.workflows.actions(5)
print(action.type)                 # WorkflowActionType.ASSIGNMENT
print(action.assign_tags)          # [1, 3]
print(action.assign_correspondent) # 7

# Iterate all actions
async for action in paperless.workflows.actions:
    print(action.id, action.type)

# All actions as a dict keyed by id
actions_dict = await paperless.workflows.actions.as_dict()
```
