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
    barcode_tag_mapping: dict[str, str] | None = None
    barcodes_enabled: bool | None = None
    barcode_enable_tiff_support: bool | None = None
    barcode_string: str | None = None
    barcode_retain_split_pages: bool | None = None
    barcode_enable_asn: bool | None = None
    barcode_asn_prefix: str | None = None
    barcode_upscale: float | None = None
    barcode_dpi: int | None = None
    barcode_max_pages: int | None = None
    barcode_enable_tag: bool | None = None

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
