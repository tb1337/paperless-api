"""Provide `MailAccount`, `MailRule` and `ProcessedMail` services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.mails import MailAccount, MailRule, ProcessedMail

from . import mixins
from .base import ServiceBase


class MailAccountService(
    ServiceBase,
    mixins.CallableMixin[MailAccount],
    mixins.IterableMixin[MailAccount],
    mixins.SecurableMixin,
):
    """Represent a factory for Paperless `MailAccount` models."""

    _api_path = API_PATH["mail_accounts"]
    _resource = PaperlessResource.MAIL_ACCOUNTS

    _resource_cls = MailAccount


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


class ProcessedMailService(
    ServiceBase,
    mixins.SecurableMixin,
    mixins.CallableMixin[ProcessedMail],
    mixins.IterableMixin[ProcessedMail],
):
    """Represent a factory for Paperless `ProcessedMail` models."""

    _api_path = API_PATH["processed_mail"]
    _resource = PaperlessResource.PROCESSED_MAIL

    _resource_cls = ProcessedMail
