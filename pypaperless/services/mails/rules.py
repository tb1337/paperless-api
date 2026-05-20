"""Provide `MailRule` related services."""

from pypaperless.const import EndpointPath
from pypaperless.models.mails.rules import MailRule
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class MailRuleService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[MailRule],
    mixins.IterableService[MailRule],
):
    """Represent a factory for Paperless `MailRule` models."""

    _api_path = EndpointPath.MAIL_RULES

    _resource_cls = MailRule
