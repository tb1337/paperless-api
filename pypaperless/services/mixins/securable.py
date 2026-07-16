"""SecurableService for PyPaperless services."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Self

# Task-local identities of services with the full-permissions payload enabled.
# Values are immutable sets that are replaced (never mutated) on entry and
# restored via token reset on exit, so concurrent asyncio tasks using
# with_permissions() on the same service cannot interfere with each other.
_SCOPED_FULL_PERMS: ContextVar[frozenset[int]] = ContextVar(
    "_SCOPED_FULL_PERMS", default=frozenset()
)


class SecurableService:
    """Provide `request_permissions` and `with_permissions()` for PyPaperless services."""

    _request_full_perms: bool = False

    @property
    def request_permissions(self) -> bool:
        """Return whether the service requests items with the `permissions` table, or not.

        Documentation: https://docs.paperless-ngx.com/api/#permissions
        """
        return self._request_full_perms or id(self) in _SCOPED_FULL_PERMS.get()

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
        It is task-local — concurrent asyncio tasks cannot interfere with each
        other.  Combine with
        :meth:`~pypaperless.services.mixins.iterable.IterableService.filter`
        or direct service calls.

        Example::

            async with paperless.documents.with_permissions() as docs:
                doc = await docs(42)
                print(doc.permissions.view.users)

                async for doc in docs:
                    print(doc.owner, doc.permissions)

        """
        token = _SCOPED_FULL_PERMS.set(_SCOPED_FULL_PERMS.get() | {id(self)})
        try:
            yield self
        finally:
            _SCOPED_FULL_PERMS.reset(token)
