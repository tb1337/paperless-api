"""Tests for custom field value types and the CustomFieldQuery DSL builder."""

import json
import operator as _op
import re
from datetime import date
from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from pypaperless import Paperless
from pypaperless.const import API_PATH
from pypaperless.models import CustomField, Tag
from pypaperless.models.custom_field_query import (
    CustomFieldQuery,
    CustomFieldQueryAnd,
    CustomFieldQueryNot,
    CustomFieldQueryOr,
)
from pypaperless.models.types import (
    CUSTOM_FIELD_TYPE_VALUE_MAP,
    CustomFieldDateValue,
    CustomFieldExtraData,
    CustomFieldIntegerValue,
    CustomFieldMonetaryValue,
    CustomFieldSelectValue,
    CustomFieldType,
)
from pypaperless.models.types import CustomFieldQuery as TypesCustomFieldQuery
from pypaperless.models.types import CustomFieldQueryAnd as TypesCustomFieldQueryAnd
from pypaperless.models.types import CustomFieldQueryNot as TypesCustomFieldQueryNot
from pypaperless.models.types import CustomFieldQueryOr as TypesCustomFieldQueryOr

from .const import PAPERLESS_TEST_URL
from .data import DATA_CUSTOM_FIELDS

# mypy: ignore-errors


# ---------------------------------------------------------------------------
# CustomField value types
# ---------------------------------------------------------------------------


async def test_draft_value_without_cache(paperless: Paperless) -> None:
    """draft_value() returns a plain object when the custom field cache is empty."""
    custom_field = CustomField.create_with_data(
        paperless,
        data={"id": 1337, "name": "Test", "data_type": CustomFieldType.INTEGER},
    )
    field_value = custom_field.draft_value(1337)
    for value_type in CUSTOM_FIELD_TYPE_VALUE_MAP.values():
        assert not isinstance(field_value, value_type)


async def test_draft_value_with_cache(httpx_mock: HTTPXMock, paperless: Paperless) -> None:
    """draft_value() returns a typed value when the custom field cache is populated."""
    httpx_mock.add_response(
        url=re.compile(
            r"^" + re.escape(f"{PAPERLESS_TEST_URL}{API_PATH['custom_fields']}") + r"\?.*$"
        ),
        method="GET",
        status_code=200,
        json=DATA_CUSTOM_FIELDS,
    )
    paperless.cache.custom_fields = await paperless.custom_fields.as_dict()

    custom_field = CustomField.create_with_data(
        client=paperless,
        data=DATA_CUSTOM_FIELDS["results"][5],
    )
    field_value = custom_field.draft_value(1337, expected_type=CustomFieldIntegerValue)
    assert isinstance(field_value, CustomFieldIntegerValue)


@pytest.mark.parametrize(
    "value_str",
    ["1900-01-02", "1900-01-02T03:04:05.133337Z"],
    ids=["date_string", "datetime_string"],
)
def test_date_value_parses_to_date(value_str: str) -> None:
    """CustomFieldDateValue accepts both ISO date strings and datetime strings, returning a date."""
    assert isinstance(CustomFieldDateValue(value=value_str).value, date)


def test_monetary_value_parsing() -> None:
    """CustomFieldMonetaryValue correctly parses and formats currency/amount."""
    field = CustomFieldMonetaryValue(value=None)
    assert field.value is None

    field = CustomFieldMonetaryValue(value="EUR1337.00")
    assert field.currency == "EUR"
    assert field.amount == 1337

    field.amount = 123.45678
    assert field.amount == 123.46  # rounded to cents

    field.extra_data = CustomFieldExtraData(default_currency="USD")
    assert field.value == "EUR123.46"

    field.value = "123.45"  # no explicit currency
    assert field.currency == "USD"  # falls back to default

    field.extra_data = CustomFieldExtraData()
    assert field.currency == ""

    field.currency = "EUR"
    assert field.value == "EUR123.45"

    field.currency = ""
    assert field.value == "123.45"

    field.value = None
    assert field.amount is None


def test_select_value_labels() -> None:
    """CustomFieldSelectValue resolves labels from select_options; returns None for missing data."""
    test = CustomFieldSelectValue(
        value="id2",
        extra_data={
            "select_options": [
                {"id": "id1", "label": "label1"},
                {"id": "id2", "label": "label2"},
            ]
        },
    )
    assert isinstance(test.labels, list)
    assert test.label == "label2"
    test.extra_data = None
    assert test.label is None


# ---------------------------------------------------------------------------
# CustomFieldQuery DSL
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "op", "value", "expected"),
    [
        ("Status", "exact", "open", ["Status", "exact", "open"]),
        ("Amount", "gte", 100, ["Amount", "gte", 100]),
        (42, "exists", True, [42, "exists", True]),
    ],
    ids=["str_field_str_value", "str_field_int_value", "int_field"],
)
def test_atom(field: Any, op: Any, value: Any, expected: Any) -> None:
    """Atom builds and serialises to the expected 3-element list for all field/value types."""
    q = CustomFieldQuery(field, op, value)
    assert q.build() == expected
    assert json.loads(str(q)) == expected


@pytest.mark.parametrize(
    ("combine", "expected_cls", "expected_tag", "expected_operands"),
    [
        (_op.and_, CustomFieldQueryAnd, "AND", [["A", "exact", 1], ["B", "exact", 2]]),
        (_op.or_, CustomFieldQueryOr, "OR", [["A", "exact", 1], ["B", "exact", 2]]),
    ],
    ids=["AND", "OR"],
)
def test_binary_operator(
    combine: Any, expected_cls: Any, expected_tag: Any, expected_operands: Any
) -> None:
    """& and | each produce the correct compound node with both operands."""
    q1 = CustomFieldQuery("A", "exact", 1)
    q2 = CustomFieldQuery("B", "exact", 2)
    combined = combine(q1, q2)
    assert isinstance(combined, expected_cls)
    assert combined.build() == [expected_tag, expected_operands]


@pytest.mark.parametrize(
    ("combine", "expected_cls", "expected_tag"),
    [
        (_op.and_, CustomFieldQueryAnd, "AND"),
        (_op.or_, CustomFieldQueryOr, "OR"),
    ],
    ids=["AND", "OR"],
)
def test_binary_operator_flattens(combine: Any, expected_cls: Any, expected_tag: Any) -> None:
    """Chaining the same operator three times flattens into a single node."""
    q1 = CustomFieldQuery("X", "exact", 1)
    q2 = CustomFieldQuery("X", "exact", 2)
    q3 = CustomFieldQuery("X", "exact", 3)
    combined = combine(combine(q1, q2), q3)
    assert isinstance(combined, expected_cls)
    result = combined.build()
    assert result[0] == expected_tag
    assert len(result[1]) == 3


def test_not_operator() -> None:
    """~ produces a CustomFieldQueryNot wrapping the operand."""
    q = CustomFieldQuery("Archived", "exact", value=True)
    negated = ~q
    assert isinstance(negated, CustomFieldQueryNot)
    assert negated.build() == ["NOT", ["Archived", "exact", True]]


def test_combined_expression() -> None:
    """Complex expression (AND + NOT) builds the correct nested structure."""
    q = CustomFieldQuery("Status", "exact", "open") & ~CustomFieldQuery(
        "Archived", "exact", value=True
    )
    result = q.build()
    assert result[0] == "AND"
    assert result[1][1] == ["NOT", ["Archived", "exact", True]]


def test_str_is_valid_json() -> None:
    """str() on any expression always produces valid JSON."""
    q = CustomFieldQuery("A", "gte", 0) | CustomFieldQuery("B", "icontains", "foo")
    parsed = json.loads(str(q))
    assert parsed[0] == "OR"


@pytest.mark.parametrize(
    ("alias", "real"),
    [
        (TypesCustomFieldQuery, CustomFieldQuery),
        (TypesCustomFieldQueryAnd, CustomFieldQueryAnd),
        (TypesCustomFieldQueryNot, CustomFieldQueryNot),
        (TypesCustomFieldQueryOr, CustomFieldQueryOr),
    ],
    ids=["Query", "QueryAnd", "QueryNot", "QueryOr"],
)
def test_builder_exported_from_types(alias: Any, real: Any) -> None:
    """Builder classes are re-exported via pypaperless.models.types."""
    assert alias is real


def test_repr() -> None:
    """repr() returns a human-readable string with the class name and serialised expression."""
    q = CustomFieldQuery("Status", "exact", "open")
    r = repr(q)
    assert r.startswith("CustomFieldQuery(")
    assert "Status" in r


def test_date_value_accepts_date_object() -> None:
    """CustomFieldDateValue passes through a value that is already a date object."""
    d = date(2024, 1, 15)
    field = CustomFieldDateValue(value=d)
    assert field.value == d


def test_tag_with_nested_children(api: Paperless) -> None:
    """Tag._validate_children builds nested Tag instances from raw dict children."""
    tag_data = {
        "id": 1,
        "slug": "parent",
        "name": "Parent Tag",
        "color": "#000000",
        "text_color": "#ffffff",
        "children": [
            {
                "id": 2,
                "slug": "child",
                "name": "Child Tag",
                "color": "#000000",
                "text_color": "#ffffff",
                "children": [
                    {
                        "id": 3,
                        "slug": "grandchild",
                        "name": "Grandchild Tag",
                        "color": "#000000",
                        "text_color": "#ffffff",
                    }
                ],
            }
        ],
    }
    tag = Tag.create_with_data(api, data=tag_data)
    assert tag.name == "Parent Tag"
    assert isinstance(tag.children, list)
    child = tag.children[0]
    assert isinstance(child, Tag)
    assert child.name == "Child Tag"
    assert isinstance(child.children, list)
    assert isinstance(child.children[0], Tag)
    assert child.children[0].name == "Grandchild Tag"


def test_tag_with_empty_children(api: Paperless) -> None:
    """Tag._validate_children returns the falsy value unchanged (empty list / None)."""
    tag_empty = Tag.create_with_data(
        api,
        data={"id": 5, "slug": "leaf", "name": "Leaf Tag", "children": []},
    )
    # empty list — _validate_children early-returns the empty list
    assert tag_empty.children == []

    tag_none = Tag.create_with_data(
        api,
        data={"id": 6, "slug": "leaf2", "name": "Leaf Tag 2"},
    )
    assert tag_none.children is None
