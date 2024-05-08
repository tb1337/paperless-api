"""Raw data constants for Paperless versions >= 2.6.0."""

# mypy: ignore-errors

V2_6_0_STATUS = {
    "pngx_version": "2.6.1",
    "server_os": "Linux-6.6.12-linuxkit-aarch64-with-glibc2.36",
    "install_type": "docker",
    "storage": {
        "total": 494384795648,
        "available": 103324229632,
    },
    "database": {
        "type": "sqlite",
        "url": "/usr/src/paperless/data/db.sqlite3",
        "status": "OK",
        "error": None,
        "migration_status": {
            "latest_migration": "paperless.0003_alter_applicationconfiguration_max_image_pixels",
            "unapplied_migrations": [],
        },
    },
    "tasks": {
        "redis_url": "redis://broker:6379",
        "redis_status": "OK",
        "redis_error": None,
        "celery_status": "OK",
        "index_status": "OK",
        "index_last_modified": "2024-03-06T07:10:55.370884+01:00",
        "index_error": None,
        "classifier_status": "OK",
        "classifier_last_trained": "2024-03-06T07:05:01.281804+00:00",
        "classifier_error": None,
    },
}
