"""Utils for pypaperless models."""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel

import pypaperless.models.base as paperless_base


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
    if isinstance(value, (paperless_base.PaperlessModelData, BaseModel)):
        serialized = (
            value.serialize()
            if isinstance(value, paperless_base.PaperlessModelData)
            else value.model_dump(mode="json")
        )
        return object_to_dict_value(serialized)

    return value
