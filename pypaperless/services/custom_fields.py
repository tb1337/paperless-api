"""Provide `CustomField` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.custom_fields import CustomField, CustomFieldDraft

from . import mixins
from .base import ServiceBase


class CustomFieldService(
    ServiceBase,
    mixins.CallableMixin[CustomField],
    mixins.DraftableMixin[CustomFieldDraft],
    mixins.IterableMixin[CustomField],
    mixins.UpdatableMixin[CustomField],
    mixins.DeletableMixin[CustomField],
):
    """Represent a factory for Paperless `CustomField` models."""

    _api_path = API_PATH["custom_fields"]
    _resource = PaperlessResource.CUSTOM_FIELDS

    _draft_cls = CustomFieldDraft
    _resource_cls = CustomField
