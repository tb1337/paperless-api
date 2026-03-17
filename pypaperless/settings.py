"""PyPaperless client configuration."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .const import API_VERSION, ENV_PREFIX, ENV_URL


class PaperlessConfig(BaseSettings):
    """Configuration for the `Paperless` client.

    All fields can be supplied via environment variables with the ``PYPAPERLESS_`` prefix:

    - ``PYPAPERLESS_URL`` — Paperless-ngx base URL
    - ``PYPAPERLESS_TOKEN`` — API token
    - ``PYPAPERLESS_REQUEST_API_VERSION`` — API version to request (defaults to the built-in value)

    Example — from environment:
    ```python
    # export PYPAPERLESS_URL=https://paperless.example.com
    # export PYPAPERLESS_TOKEN=mytoken
    async with Paperless() as paperless:
        ...
    ```

    Example — explicit config object:
    ```python
    cfg = PaperlessConfig(url="https://paperless.example.com", token="mytoken")
    async with Paperless(config=cfg) as paperless:
        ...
    ```
    """

    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX)

    url: str = ""
    token: str | None = None
    request_api_version: int = API_VERSION

    @model_validator(mode="after")
    def _require_url(self) -> "PaperlessConfig":
        if not self.url:
            msg = (
                "PaperlessConfig requires a URL. "
                f"Pass url= explicitly or set the {ENV_URL} environment variable."
            )
            raise ValueError(msg)
        return self
