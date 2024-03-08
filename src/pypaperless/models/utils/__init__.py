"""Utils for pypaperless models.

Since there are common use-cases in transforming dicts to dataclass et vice-versa,
we borrowed some snippets from aiohue instead of re-inventing the wheel.

pypaperless is meant to be the api library for a Home Assistant integration,
so it should be okay I think.

https://github.com/home-assistant-libs/aiohue/

Thanks for the excellent work, guys!
"""

# mypy: ignore-errors
# pylint: disable=all

import logging
from dataclasses import MISSING, asdict, fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from types import NoneType, UnionType
from typing import TYPE_CHECKING, Any, Union, get_args, get_origin, get_type_hints

import pypaperless.models.base as paperless_base

if TYPE_CHECKING:
    from pypaperless import Paperless


def _str_to_datetime(datetimestr: str) -> datetime:
    """Parse datetime from string."""
    return datetime.fromisoformat(datetimestr.replace("Z", "+00:00"))


def _str_to_date(datestr: str) -> date:
    """Parse date from string."""
    return date.fromisoformat(datestr)


def _dateobj_to_str(value: date | datetime) -> str:
    """Parse string from date objects."""
    return value.isoformat().replace("+00:00", "Z")


def object_to_dict_value(value: Any) -> Any:
    """Convert object values to their correspondending json values."""

    def _clean_value(_value_obj: Any) -> Any:
        if isinstance(_value_obj, dict):
            _value_obj = _clean_dict(_value_obj)
        if isinstance(_value_obj, list):
            _value_obj = _clean_list(_value_obj)
        if isinstance(_value_obj, Enum):
            _value_obj = _value_obj.value
        if isinstance(_value_obj, date | datetime):
            _value_obj = _dateobj_to_str(_value_obj)
        if is_dataclass(_value_obj):
            _value_obj = _clean_dict(asdict(_value_obj))
        return _value_obj

    def _clean_list(_list_obj: list) -> list[Any]:
        final = []
        for list_value in _list_obj:
            final.append(_clean_value(list_value))  # noqa: PERF401
        return final

    def _clean_dict(_dict_obj: dict) -> dict[str, Any]:
        final = {}
        for dict_key, dict_value in _dict_obj.items():
            final[dict_key] = _clean_value(dict_value)
        return final

    return _clean_value(value)


def dict_value_to_object(
    name: str,
    value: Any,
    value_type: Any,
    default: Any = MISSING,
    _api: "Paperless | None" = None,
) -> Any:
    """Try to parse a value from raw (json) data and type annotations.

    Since there are common use-cases in transforming dicts to dataclass et vice-versa,
    we borrowed some snippets from aiohue instead of re-inventing the wheel.

    pypaperless is meant to be the api library for a Home Assistant integration,
    so it should be okay I think.

    https://github.com/home-assistant-libs/aiohue/
    """
    # ruff: noqa: PLR0911, PLR0912
    if isinstance(value_type, str):
        # this shouldn't happen, but just in case
        value_type = get_type_hints(value_type, globals(), locals())

    if isinstance(value, dict) and hasattr(value_type, "from_dict"):
        # always prefer classes that have a from_dict
        return value_type.from_dict(value)

    if value is None and not isinstance(default, type(MISSING)):
        return default
    if value is None and value_type is NoneType:
        return None
    if is_dataclass(value_type) and isinstance(value, dict):
        if _api is not None and paperless_base.PaperlessModel in value_type.__mro__:
            return value_type.create_with_data(api=_api, data=value, fetched=True)
        return value_type(
            **{
                field.name: dict_value_to_object(
                    f"{value_type.__name__}.{field.name}",
                    value.get(field.name),
                    field.type,
                    field.default,
                    _api,
                )
                for field in fields(value_type)
            }
        )
    # get origin value type and inspect one-by-one
    origin: Any = get_origin(value_type)
    if origin in (list, tuple, set) and isinstance(value, list | tuple | set):
        return origin(
            dict_value_to_object(name, subvalue, get_args(value_type)[0], _api=_api)
            for subvalue in value
            if subvalue is not None
        )

    # handle dictionary where we should inspect all values
    if origin is dict:
        subkey_type = get_args(value_type)[0]
        subvalue_type = get_args(value_type)[1]
        return {
            dict_value_to_object(subkey, subkey, subkey_type, _api=_api): dict_value_to_object(
                f"{subkey}.value", subvalue, subvalue_type, _api=_api
            )
            for subkey, subvalue in value.items()
        }
    # handle Union type
    if origin is Union or origin is UnionType:
        # try all possible types
        sub_value_types = get_args(value_type)
        for sub_arg_type in sub_value_types:
            if value is NoneType and sub_arg_type is NoneType:
                return value
            if value == {} and sub_arg_type is NoneType:
                # handle case where optional value is received as empty dict from api
                return None
            # try them all until one succeeds
            try:
                return dict_value_to_object(name, value, sub_arg_type, _api=_api)
            except (KeyError, TypeError, ValueError):
                pass
        # if we get to this point, all possibilities failed
        # find out if we should raise or log this
        err = (
            f"Value {value} of type {type(value)} is invalid for {name}, "
            f"expected value of type {value_type}"
        )
        if NoneType not in sub_value_types:
            # raise exception, we have no idea how to handle this value
            raise TypeError(err)
        # failed to parse the (sub) value but None allowed, log only
        logging.getLogger(__name__).warning(err)
        return None
    if origin is type:
        return get_type_hints(value, globals(), locals())
    # handle Any as value type (which is basically unprocessable)
    if value_type is Any:
        return value
    # raise if value is None and the value is required according to annotations
    if value is None and value_type is not NoneType:
        message = f"`{name}` of type `{value_type}` is required."
        raise KeyError(message)

    try:
        if issubclass(value_type, Enum):
            return value_type(value)
        if issubclass(value_type, datetime):
            return _str_to_datetime(value)
        if issubclass(value_type, date):
            return _str_to_date(value)
    except TypeError:
        # happens if value_type is not a class
        pass

    # common type conversions (e.g. int as string)
    if value_type is float and isinstance(value, int):
        return float(value)
    if value_type is int and isinstance(value, str) and value.isnumeric():
        return int(value)

    # If we reach this point, we could not match the value with the type and we raise
    if not isinstance(value, value_type):
        message = f"Value {value} of type {type(value)} is invalid for {name}, \
            expected value of type {value_type}"
        raise TypeError(message)

    return value
