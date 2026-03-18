"""Provide `MailRule` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.mails.rules import MailRule
from pypaperless.services import mixins
from pypaperless.services.base import ServiceBase


class MailRuleService(
    ServiceBase,
    mixins.CallableMixin[MailRule],
    mixins.IterableMixin[MailRule],
    mixins.SecurableMixin,
):
    """Represent a factory for Paperless `MailRule` models."""

    _api_path = API_PATH["mail_rules"]
    _resource = PaperlessResource.MAIL_RULES

    _resource_cls = MailRule
