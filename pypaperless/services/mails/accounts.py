"""Provide `MailAccount` related services."""

from typing import cast

from pypaperless.const import EndpointPath
from pypaperless.models.mails.accounts import MailAccount
from pypaperless.services import mixins
from pypaperless.services.base import ResourceService


class MailAccountService(
    ResourceService,
    mixins.SecurableService,
    mixins.CallableService[MailAccount],
    mixins.IterableService[MailAccount],
):
    """Represent a factory for Paperless `MailAccount` models."""

    _api_path = EndpointPath.MAIL_ACCOUNTS

    _resource_cls = MailAccount

    async def test(self) -> dict[str, object]:
        """Test all configured mail account connections.

        Returns a dict with per-account test results from Paperless.

        Example::

            results = await paperless.mail_accounts.test()

        """
        return cast(
            "dict[str, object]",
            await self._runtime.transport.post(EndpointPath.MAIL_ACCOUNTS_TEST, json={}),
        )

    async def process(self, pk: int) -> None:
        """Trigger processing of unread mail for the given account.

        Args:
            pk: Primary key of the mail account to process.

        Example::

            await paperless.mail_accounts.process(1)

        """
        res = await self._runtime.transport.request_raw(
            "post",
            EndpointPath.MAIL_ACCOUNTS_PROCESS.format(pk=pk),
            json={},
        )
        res.raise_for_status()
