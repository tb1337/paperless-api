"""Provide `Profile` related models."""

from typing import ClassVar

from pydantic import BaseModel

from pypaperless.const import API_PATH

from .base import PaperlessModel


class ProfileSocialAccount(BaseModel):
    """Represent a social account linked to the Paperless user profile."""

    id: int | None = None
    provider: str | None = None
    name: str | None = None


class Profile(PaperlessModel):
    """Represent the Paperless user `Profile`."""

    _api_path: ClassVar[str] = API_PATH["profile"]

    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    auth_token: str | None = None
    social_accounts: list[ProfileSocialAccount] | None = None
    has_usable_password: bool | None = None
    is_mfa_enabled: bool | None = None
