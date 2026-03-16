"""Tests for enum types: UNKNOWN fallback values."""

import pytest

from pypaperless.const import PaperlessResource
from pypaperless.models.types import (
    CustomFieldType,
    MatchingAlgorithm,
    ShareLinkFileVersion,
    StatusType,
    TaskStatus,
    TaskType,
    WorkflowActionType,
    WorkflowTriggerScheduleDateField,
    WorkflowTriggerSource,
    WorkflowTriggerType,
)

# mypy: ignore-errors

_NEVER_STR = "!never_existing_type!"
_NEVER_INT = 99952342


@pytest.mark.parametrize(
    ("enum_cls", "bad_value"),
    [
        (PaperlessResource, _NEVER_STR),
        (CustomFieldType, _NEVER_STR),
        (MatchingAlgorithm, _NEVER_INT),
        (ShareLinkFileVersion, _NEVER_STR),
        (StatusType, _NEVER_STR),
        (TaskType, _NEVER_STR),
        (TaskStatus, _NEVER_STR),
        (WorkflowActionType, _NEVER_INT),
        (WorkflowTriggerType, _NEVER_INT),
        (WorkflowTriggerScheduleDateField, _NEVER_STR),
        (WorkflowTriggerSource, _NEVER_INT),
    ],
    ids=[
        "PaperlessResource",
        "CustomFieldType",
        "MatchingAlgorithm",
        "ShareLinkFileVersion",
        "StatusType",
        "TaskType",
        "TaskStatus",
        "WorkflowActionType",
        "WorkflowTriggerType",
        "WorkflowTriggerScheduleDateField",
        "WorkflowTriggerSource",
    ],
)
def test_enum_unknown_fallback(enum_cls: type, bad_value: object) -> None:
    """Every custom enum must return UNKNOWN for unrecognised values instead of raising."""
    assert enum_cls(bad_value) == enum_cls.UNKNOWN
