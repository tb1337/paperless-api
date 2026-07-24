"""Dev-instance connection config for the maintenance scripts and run/debug.py.

Reads ``PYPAPERLESS_URL`` / ``PYPAPERLESS_TOKEN`` / ``PYPAPERLESS_TEST_DOC`` from
the git-ignored ``.env`` in the repo root. Copy ``.env.example`` to ``.env`` and
fill in your throwaway dev values to get started.

Example::

    from _dev_env import load_dev_env

    env = load_dev_env()
    client = PaperlessClient(env.url, env.token.get_secret_value())
"""

# ruff: noqa
# mypy: ignore-errors

import pathlib

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = pathlib.Path(__file__).resolve().parent.parent / ".env"


class _DevEnv(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PYPAPERLESS_", env_file=_ENV_FILE, extra="ignore")

    url: str
    token: SecretStr
    test_doc: int


def load_dev_env() -> _DevEnv:
    """Load the dev-instance settings from the repo-root ``.env``.

    Raises:
        pydantic.ValidationError: if ``.env`` is missing or incomplete.

    """
    return _DevEnv()
