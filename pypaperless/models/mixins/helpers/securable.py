"""SecurableMixin for PyPaperless helpers."""


class SecurableMixin:
    """Provide the `request_full_permissions` property for PyPaperless helpers."""

    _request_full_perms: bool = False

    @property
    def request_permissions(self) -> bool:
        """Return whether the helper requests items with the `permissions` table, or not.

        Documentation: https://docs.paperless-ngx.com/api/#permissions
        """
        return self._request_full_perms

    @request_permissions.setter
    def request_permissions(self, value: bool) -> None:
        """Set whether the helper requests items with the `permissions` table, or not.

        Documentation: https://docs.paperless-ngx.com/api/#permissions
        """
        self._request_full_perms = value
