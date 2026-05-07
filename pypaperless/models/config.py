"""Provide `Config` related models."""

from enum import StrEnum
from typing import ClassVar, Self

from pypaperless.const import EndpointPath

from .base import PaperlessModel


class ArchiveFileGeneration(StrEnum):
    """Represent a subtype of `Config`."""

    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class ColorConversionStrategy(StrEnum):
    """Represent a subtype of `Config`."""

    UNCHANGED = "LeaveColorUnchanged"
    RGB = "RGB"
    INDEPENDENT = "UseDeviceIndependentColor"
    GRAY = "Gray"
    CMYK = "CMYK"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class LLMBackend(StrEnum):
    """Represent a subtype of `Config`."""

    OPENAI_LIKE = "openai-like"
    OLLAMA = "ollama"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class LLMEmbeddingBackend(StrEnum):
    """Represent a subtype of `Config`."""

    OPENAI_LIKE = "openai-like"
    HUGGINGFACE = "huggingface"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class OcrMode(StrEnum):
    """Represent a subtype of `Config`."""

    AUTO = "auto"
    FORCE = "force"
    REDO = "redo"
    OFF = "off"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class UnpaperClean(StrEnum):
    """Represent a subtype of `Config`."""

    CLEAN = "clean"
    FINAL = "clean-final"
    NONE = "none"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, *_: object) -> Self:
        """Return the UNKNOWN member for any unrecognised value."""
        return cls["UNKNOWN"]


class Config(PaperlessModel):
    """Represent a Paperless `Config`."""

    _api_path: ClassVar[str] = EndpointPath.CONFIG_SINGLE

    id: int | None = None
    user_args: str | None = None
    output_type: str | None = None
    pages: int | None = None
    language: str | None = None
    mode: OcrMode | None = None
    image_dpi: int | None = None
    unpaper_clean: UnpaperClean | None = None
    deskew: bool | None = None
    rotate_pages: bool | None = None
    rotate_pages_threshold: float | None = None
    max_image_pixels: float | None = None
    color_conversion_strategy: ColorConversionStrategy | None = None
    app_title: str | None = None
    app_logo: str | None = None
    archive_file_generation: ArchiveFileGeneration | None = None
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
    barcode_tag_split: bool | None = None
    ai_enabled: bool | None = None
    llm_embedding_backend: LLMEmbeddingBackend | None = None
    llm_embedding_model: str | None = None
    llm_endpoint: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    llm_backend: LLMBackend | None = None
