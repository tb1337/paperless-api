"""Utility functions for pypaperless."""

from datetime import date, datetime
from enum import Enum
from io import BytesIO
from typing import Any

from pydantic import BaseModel


def normalize_base_url(url: str) -> str:
    """Normalize a URL string for use as a Paperless API base URL."""
    url = url.rstrip("/")
    if "://" not in url:
        url = f"https://{url}"
    if not url.startswith(("https://", "http://")):
        url = f"https://{url}"
    return url


def process_form_data(data: dict[str, Any]) -> tuple[dict[str, Any], list[tuple[str, Any]]]:
    """Process form data and create httpx-compatible data/files tuples.

    Returns a tuple of (data_fields, file_fields) for httpx.
    """
    data_fields: dict[str, Any] = {}
    file_fields: list[tuple[str, Any]] = []

    def _add_file_value(name: str, value: tuple | bytes) -> None:
        if isinstance(value, tuple):
            if len(value) == 2:
                file_fields.append((name, (f"{value[1]}", BytesIO(value[0]))))
            else:
                file_fields.append((name, BytesIO(value[0])))
        else:
            file_fields.append((name, BytesIO(value)))

    def _add_data_value(name: str, value: Any) -> None:
        if name in data_fields:
            existing = data_fields[name]
            if isinstance(existing, list):
                existing.append(f"{value}")
            else:
                data_fields[name] = [existing, f"{value}"]
        else:
            data_fields[name] = f"{value}"

    def _add_form_value(name: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, dict):
            for dict_key, dict_value in value.items():
                _add_form_value(dict_key, dict_value)
            return
        if isinstance(value, list | set):
            for list_value in value:
                _add_form_value(name, list_value)
            return
        if isinstance(value, (tuple, bytes)):
            _add_file_value(name, value)
        else:
            _add_data_value(name, value)

    for key, value in data.items():
        _add_form_value(key, value)
    return data_fields, file_fields


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
