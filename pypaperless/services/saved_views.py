"""Provide `SavedView` service."""

from pypaperless.const import EndpointPath, PaperlessResource
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

    _api_path = EndpointPath.SAVED_VIEWS
    _resource = PaperlessResource.SAVED_VIEWS

    _resource_cls = SavedView
