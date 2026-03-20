"""Provide `Profile` service."""

from pypaperless.const import API_PATH, PaperlessResource
from pypaperless.models.profile import Profile

from .base import ResourceService


class ProfileService(ResourceService):
    """Represent a factory for the Paperless `Profile` model."""

    _api_path = API_PATH["profile"]
    _resource = PaperlessResource.PROFILE

    _resource_cls = Profile

    async def __call__(self) -> Profile:
        """Fetch the current user's Paperless profile.

        Example::

            profile = await paperless.profile()
            print(profile.email, profile.first_name)

        """
        res = await self._client.request_json("get", self._api_path)
        return self._resource_cls.from_data(self._client, res)

    async def update(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Profile:
        """Update the current user's profile partially via ``PATCH``.

        Only fields that are explicitly provided (non-``None``) are sent to the
        API.  Returns a refreshed :class:`~pypaperless.models.profile.Profile`.

        Args:
            email:      New e-mail address.
            password:   New plain-text password.
            first_name: First name.
            last_name:  Last name.

        Example::

            profile = await paperless.profile.update(
                email="new@example.com",
                first_name="Ada",
            )

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
        return self._resource_cls.from_data(self._client, res)
