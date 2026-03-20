"""Provide `ProcessedMail` related services."""

from pypaperless.const import API_PATH, PaperlessResource
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

    _api_path = API_PATH["processed_mail"]
    _resource = PaperlessResource.PROCESSED_MAIL

    _resource_cls = ProcessedMail
