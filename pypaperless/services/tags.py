"""Provide `Tag` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.tags import Tag, TagDraft

from . import mixins
from .base import ServiceBase


class TagService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Tag],
    mixins.DraftableMixin[TagDraft],
    mixins.IterableMixin[Tag],
    mixins.UpdatableMixin[Tag],
    mixins.DeletableMixin[Tag],
):
    """Represent a factory for Paperless `Tag` models."""

    _api_path = API_PATH["tags"]
    _resource = PaperlessResource.TAGS

    _draft_cls = TagDraft
    _resource_cls = Tag
