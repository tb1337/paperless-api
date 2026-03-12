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

### `WorkflowTrigger` *(key fields)*

| Field                      | Description                  |
| -------------------------- | ---------------------------- |
| `id`                       | Primary key                  |
| `type`                     | Trigger type                 |
| `sources`                  | Consumption sources          |
| `filter_filename`          | Filename pattern filter      |
| `filter_path`              | Path pattern filter          |
| `filter_mailrule`          | Mail rule id filter          |
| `filter_has_tags`          | Required tags                |
| `filter_has_correspondent` | Required correspondent       |
| `filter_has_document_type` | Required document type       |
| `schedule_offset_days`     | Scheduled trigger day offset |
| `schedule_is_recurring`    | Recurring schedule flag      |

### `WorkflowAction` *(key fields)*

| Field                  | Description                 |
| ---------------------- | --------------------------- |
| `id`                   | Primary key                 |
| `type`                 | Action type                 |
| `assign_title`         | Title template to assign    |
| `assign_tags`          | Tags to assign              |
| `assign_correspondent` | Correspondent id to assign  |
| `assign_document_type` | Document type id to assign  |
| `assign_storage_path`  | Storage path id to assign   |
| `assign_owner`         | Owner id to assign          |
| `remove_all_tags`      | Remove all existing tags    |
| `email`                | Email notification config   |
| `webhook`              | Webhook notification config |

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
active = [wf async for wf in paperless.workflows.reduce() if wf.enabled]
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
