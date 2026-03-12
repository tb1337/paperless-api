"""Provide `Correspondent` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.correspondents import Correspondent, CorrespondentDraft

from . import mixins
from .base import ServiceBase


class CorrespondentService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[Correspondent],
    mixins.DraftableMixin[CorrespondentDraft],
    mixins.IterableMixin[Correspondent],
    mixins.UpdatableMixin[Correspondent],
    mixins.DeletableMixin[Correspondent],
):
    """Represent a factory for Paperless `Correspondent` models."""

    _api_path = API_PATH["correspondents"]
    _resource = PaperlessResource.CORRESPONDENTS

    _draft_cls = CorrespondentDraft
    _resource_cls = Correspondent
