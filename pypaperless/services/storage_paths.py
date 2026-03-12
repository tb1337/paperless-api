"""Provide `StoragePath` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.storage_paths import StoragePath, StoragePathDraft

from . import mixins
from .base import ServiceBase


class StoragePathService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[StoragePath],
    mixins.DraftableMixin[StoragePathDraft],
    mixins.IterableMixin[StoragePath],
    mixins.UpdatableMixin[StoragePath],
    mixins.DeletableMixin[StoragePath],
):
    """Represent a factory for Paperless `StoragePath` models."""

    _api_path = API_PATH["storage_paths"]
    _resource = PaperlessResource.STORAGE_PATHS

    _draft_cls = StoragePathDraft
    _resource_cls = StoragePath
