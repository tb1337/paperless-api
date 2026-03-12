"""Provide `Profile` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.profile import Profile

from .base import ServiceBase


class ProfileService(ServiceBase):
    """Represent a factory for the Paperless `Profile` model."""

    _api_path = API_PATH["profile"]
    _resource = PaperlessResource.PROFILE

    _resource_cls = Profile

    async def __call__(self) -> Profile:
        """Request the `Profile` model data."""
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.create_with_data(self._client, res)

    async def update(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Profile:
        """Update the user profile partially via PATCH.

        Only the provided (non-None) fields are sent to the API.

        `email`: new e-mail address.
        `password`: new plain-text password.
        `first_name`: first name.
        `last_name`: last name.
        """
        payload: dict[str, object] = {}
        if email is not None:
            payload["email"] = email
        if password is not None:
            payload["password"] = password
        if first_name is not None:
            payload["first_name"] = first_name
        if last_name is not None:
            payload["last_name"] = last_name
        res = await self._client.request_json("patch", self._api_path, json=payload)
        return self._resource_cls.create_with_data(self._client, res)
