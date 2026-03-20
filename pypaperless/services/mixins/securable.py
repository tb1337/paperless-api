"""SecurableService for PyPaperless services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Self


class SecurableService:
    """Provide `request_permissions` and `with_permissions()` for PyPaperless services."""

    _request_full_perms: bool = False

    @property
    def request_permissions(self) -> bool:
        """Return whether the service requests items with the `permissions` table, or not.

        Documentation: https://docs.paperless-ngx.com/api/#permissions
        """
        return self._request_full_perms

    @request_permissions.setter
    def request_permissions(self, value: bool) -> None:
        """Set whether the service requests items with the `permissions` table, or not.

        Documentation: https://docs.paperless-ngx.com/api/#permissions
        """
        self._request_full_perms = value

    @asynccontextmanager
    async def with_permissions(self: Self) -> AsyncGenerator[Self]:
        """Context manager that enables the full permissions payload for a block.

        The flag is reset automatically on exit, even if an exception is raised.
        Combine with :meth:`~pypaperless.services.mixins.iterable.IterableService.filter`
        or direct service calls.

        Example::

            async with paperless.documents.with_permissions() as docs:
                doc = await docs(42)
                print(doc.permissions.view.users)

                async for doc in docs:
                    print(doc.owner, doc.permissions)

        """
        self._request_full_perms = True
        try:
            yield self
        finally:
            self._request_full_perms = False
