"""Provide `SavedView` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.saved_views import SavedView

from . import mixins
from .base import ResourceService


class SavedViewService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[SavedView],
    mixins.IterableService[SavedView],
):
    """Represent a factory for Paperless `SavedView` models."""

    _api_path = API_PATH["saved_views"]
    _resource = PaperlessResource.SAVED_VIEWS

    _resource_cls = SavedView
