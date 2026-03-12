"""Provide `Config` related models."""

from typing import ClassVar

from pypaperless.const import API_PATH

from .base import PaperlessModel


class Config(PaperlessModel):
    """Represent a Paperless `Config`."""

    _api_path: ClassVar[str] = API_PATH["config_single"]

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
