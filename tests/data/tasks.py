"""Tasks snapshot."""

_TASK_1 = {
    "id": 1,
    "task_id": "11112222-aaaa-bbbb-cccc-333344445555",
    "task_type": "consume_file",
    "task_type_display": "Consume File",
    "trigger_source": "api_upload",
    "trigger_source_display": "API Upload",
    "status": "started",
    "status_display": "Started",
    "date_created": "2023-12-16T13:06:29.107815+00:00",
    "date_started": "2023-12-16T13:06:29.500000+00:00",
    "date_done": None,
    "duration_seconds": None,
    "wait_time_seconds": 0.39,
    "input_data": {"filename": "a.png"},
    "result_data": None,
    "related_document_ids": [],
    "acknowledged": False,
    "owner": 1,
}

_TASK_2 = {
    "id": 2,
    "task_id": "ffffeeee-9999-8888-7777-ddddccccbbbb",
    "task_type": "consume_file",
    "task_type_display": "Consume File",
    "trigger_source": "folder_consume",
    "trigger_source_display": "Folder Consume",
    "status": "success",
    "status_display": "Success",
    "date_created": "2023-12-16T13:06:26.117158+00:00",
    "date_started": "2023-12-16T13:06:26.500000+00:00",
    "date_done": "2023-12-16T13:06:29.859669+00:00",
    "duration_seconds": 3.36,
    "wait_time_seconds": 0.38,
    "input_data": {"filename": "b.png"},
    "result_data": {"document_id": 1780},
    "related_document_ids": [1780],
    "acknowledged": False,
    "owner": 1,
}

_TASK_3 = {
    "id": 3,
    "task_id": "abcdef12-3456-7890-abcd-ef1234567890",
    "task_type": "sanity_check",
    "task_type_display": "Sanity Check",
    "trigger_source": "scheduled",
    "trigger_source_display": "Scheduled",
    "status": "success",
    "status_display": "Success",
    "date_created": "2023-12-16T13:04:28.175624+00:00",
    "date_started": "2023-12-16T13:04:28.500000+00:00",
    "date_done": "2023-12-16T13:04:32.318797+00:00",
    "duration_seconds": 3.82,
    "wait_time_seconds": 0.32,
    "input_data": {},
    "result_data": None,
    "related_document_ids": [],
    "acknowledged": True,
    "owner": 1,
}

DATA_TASKS = {
    "count": 3,
    "next": None,
    "previous": None,
    "results": [_TASK_1, _TASK_2, _TASK_3],
}

DATA_TASKS_ACTIVE = [_TASK_1]

DATA_TASKS_SUMMARY = [
    {
        "task_type": "consume_file",
        "total_count": 2,
        "pending_count": 0,
        "success_count": 1,
        "failure_count": 0,
        "avg_duration_seconds": 3.36,
        "avg_wait_time_seconds": 0.385,
        "last_run": "2023-12-16T13:06:32.318797+00:00",
        "last_success": "2023-12-16T13:06:32.318797+00:00",
        "last_failure": None,
    },
    {
        "task_type": "sanity_check",
        "total_count": 1,
        "pending_count": 0,
        "success_count": 1,
        "failure_count": 0,
        "avg_duration_seconds": 3.82,
        "avg_wait_time_seconds": 0.32,
        "last_run": "2023-12-16T13:04:32.318797+00:00",
        "last_success": "2023-12-16T13:04:32.318797+00:00",
        "last_failure": None,
    },
]
