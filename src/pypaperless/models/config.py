"""Provide `Config` related models and helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pypaperless.const import API_PATH, PaperlessResource

from .base import HelperBase, PaperlessModel
from .mixins import helpers

if TYPE_CHECKING:
    from pypaperless import Paperless


@dataclass(init=False)
class Config(
    PaperlessModel,
):
    """Represent a Paperless `Config`."""

    _api_path = API_PATH["config_single"]

    id: int | None = None
    user_args: str | None = None
    output_type: str | None = None
    pages: int | None = None
    language: str | None = None
    mode: str | None = None
    skip_archive_file: str | None = None
    image_dpi: int | None = None
    unpaper_clean: str | None = None
    deskew: bool | None = None
    rotate_pages: bool | None = None
    rotate_pages_threshold: float | None = None
    max_image_pixels: float | None = None
    color_conversion_strategy: str | None = None
    app_title: str | None = None
    app_logo: str | None = None

    def __init__(self, api: "Paperless", data: dict[str, Any]) -> None:
        """Initialize a `Config` instance."""
        super().__init__(api, data)

        self._api_path = self._api_path.format(pk=data.get("id"))


class ConfigHelper(
    HelperBase[Config],
    helpers.CallableMixin[Config],
):
    """Represent a factory for Paperless `Config` models."""

    _api_path = API_PATH["config"]
    _resource = PaperlessResource.CONFIG

    _resource_cls = Config
