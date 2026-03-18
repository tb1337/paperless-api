"""Provide `MailAccount` related services."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.mails.accounts import MailAccount
from pypaperless.services import mixins
from pypaperless.services.base import ServiceBase


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
