"""Provide `Config` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.config import Config

from . import mixins
from .base import ServiceBase


class ConfigService(ServiceBase, mixins.CallableMixin[Config]):
    """Represent a factory for Paperless `Config` models."""

    _api_path = API_PATH["config"]
    _resource = PaperlessResource.CONFIG

    _resource_cls = Config
