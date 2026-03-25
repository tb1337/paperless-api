"""Provide `ProcessedMail` related services."""

from pypaperless.const import EndpointPath, PaperlessResource
from pypaperless.models.mails.processed import ProcessedMail
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class ProcessedMailService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[ProcessedMail],
    mixins.IterableService[ProcessedMail],
):
    """Represent a factory for Paperless `ProcessedMail` models."""

    _api_path = EndpointPath.PROCESSED_MAIL
    _resource = PaperlessResource.PROCESSED_MAIL

    _resource_cls = ProcessedMail
