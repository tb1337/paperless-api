"""Utility functions for pypaperless."""

from datetime import date, datetime
from enum import Enum
from io import BytesIO
from typing import Any

from pydantic import BaseModel


def normalize_base_url(url: str) -> str:
    """Normalize a URL string for use as a Paperless API base URL."""
    url = url.rstrip("/")
    if not url.startswith(("https://", "http://")):
        url = f"https://{url}"
    return url


class _FormDataBuilder:
    """Build httpx-compatible (data, files) tuples from a raw form dict."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._files: list[tuple[str, Any]] = []

    def _add_file(self, name: str, value: tuple | bytes) -> None:
        """Append a file field to the files list."""
        if isinstance(value, tuple):
            if len(value) == 2:
                self._files.append((name, (f"{value[1]}", BytesIO(value[0]))))
            else:
                self._files.append((name, BytesIO(value[0])))
        else:
            self._files.append((name, BytesIO(value)))

    def _add_scalar(self, name: str, value: Any) -> None:
        """Append or accumulate a scalar data field."""
        if name in self._data:
            existing = self._data[name]
            if isinstance(existing, list):
                existing.append(f"{value}")
            else:
                self._data[name] = [existing, f"{value}"]
        else:
            self._data[name] = f"{value}"

    def _add(self, name: str, value: Any) -> None:
        """Recursively classify and dispatch a form value."""
        if value is None:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                self._add(k, v)
        elif isinstance(value, list | set):
            for item in value:
                self._add(name, item)
        elif isinstance(value, tuple | bytes):
            self._add_file(name, value)
        else:
            self._add_scalar(name, value)

    def build(self, data: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, Any]]]:
        """Process all entries and return the (data_fields, file_fields) tuple."""
        for key, value in data.items():
            self._add(key, value)
        return self._data, self._files


def process_form_data(data: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, Any]]]:
    """Process form data and create httpx-compatible data/files tuples.

    Returns a tuple of (data_fields, file_fields) for httpx.
    """
    return _FormDataBuilder().build(data)


def _dateobj_to_str(value: date | datetime) -> str:
    """Parse string from date objects."""
    return value.isoformat().replace("+00:00", "Z")


def object_to_dict_value(value: Any) -> Any:
    """Convert object values to their corresponding json values."""
    if isinstance(value, dict):
        return {k: object_to_dict_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [object_to_dict_value(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return _dateobj_to_str(value)
    if isinstance(value, BaseModel):
        return object_to_dict_value(value.model_dump(mode="json"))

    return value
