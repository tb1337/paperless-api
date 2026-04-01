"""Fluent builder for the ``custom_field_query`` document filter.

Combine atoms with ``&`` (AND), ``|`` (OR) and ``~`` (NOT), then pass
``str(q)`` as the ``custom_field_query`` kwarg to :meth:`documents.filter`::

    from pypaperless.builders.custom_fields import CustomFieldQuery

    q = CustomFieldQuery("Amount", "gte", 100) & ~CustomFieldQuery("Archived", "exact", True)
    async with paperless.documents.filter(custom_field_query=str(q)) as docs:
        ...

Field can be referenced by integer id or name string.
See :class:`CustomFieldQuery` for the full list of supported operators.
"""

import json
from typing import Any, Literal

# The following list is based on the schema defined in:
# https://github.com/paperless-ngx/paperless-ngx/blob/dev/src/documents/filters.py
# -> CustomFieldQueryParser

type _QueryOperation = Literal[
    "exact",
    "in",
    "isnull",
    "exists",
    "icontains",
    "istartswith",
    "iendswith",
    "gt",
    "gte",
    "lt",
    "lte",
    "range",
    "contains",
]


class CustomFieldQuery:
    """A single custom-field filter atom: ``[field, op, value]``.

    Use the ``&``, ``|``, ``~`` operators to combine atoms into boolean
    expressions.  Call :func:`str` on the result to obtain the JSON string
    for :attr:`~pypaperless.models.filters.DocumentFilters.custom_field_query`.

    Args:
        field: Custom field referenced by its integer id or by its name string.
        op:    Comparison operator, e.g. ``"exact"``, ``"icontains"``,
               ``"gte"``, ``"exists"``.
        value: The value to compare against.  Use ``True``/``False`` for
               boolean operators; a plain scalar for most operators; a list
               for ``"in"`` and ``"range"``.

    Example::

        q = CustomFieldQuery("Status", "exact", "open")
        q = CustomFieldQuery(42, "gte", 100)
        q = CustomFieldQuery("Project", "exists", True)
        str(q)  # '["Status", "exact", "open"]'

    """

    def __init__(self, field: int | str, op: _QueryOperation, value: Any) -> None:
        """Initialise a query atom."""
        self._field = field
        self._op = op
        self._value = value

    def build(self) -> list[Any]:
        """Return the JSON-serialisable list for this expression."""
        return [self._field, self._op, self._value]

    def __str__(self) -> str:
        """Serialise to the JSON string expected by the API."""
        return json.dumps(self.build())

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}({self.build()!r})"

    def __and__(self, other: "CustomFieldQuery") -> "_CustomFieldQueryAnd":
        """Combine with *other* using logical AND."""
        return _CustomFieldQueryAnd(self, other)

    def __or__(self, other: "CustomFieldQuery") -> "_CustomFieldQueryOr":
        """Combine with *other* using logical OR."""
        return _CustomFieldQueryOr(self, other)

    def __invert__(self) -> "_CustomFieldQueryNot":
        """Negate this expression."""
        return _CustomFieldQueryNot(self)


class _CustomFieldQueryAnd(CustomFieldQuery):
    """Logical AND of two or more sub-expressions: ``["AND", [q0, q1, …]]``.

    Prefer the ``&`` operator over instantiating this class directly::

        q = (
            CustomFieldQuery("Status", "exact", "open")
            & CustomFieldQuery("Amount", "gte", 100)
            & CustomFieldQuery("Urgent", "exact", True)
        )
        # equivalent to:
        q = _CustomFieldQueryAnd(
            CustomFieldQuery("Status", "exact", "open"),
            CustomFieldQuery("Amount", "gte", 100),
            CustomFieldQuery("Urgent", "exact", True),
        )
    """

    def __init__(self, *queries: CustomFieldQuery) -> None:
        """Initialise with two or more sub-expressions."""
        self._queries = queries

    def build(self) -> list[Any]:
        """Return the JSON-serialisable list for this expression."""
        return ["AND", [q.build() for q in self._queries]]

    def __and__(self, other: CustomFieldQuery) -> "_CustomFieldQueryAnd":
        """Flatten: extend the existing AND instead of nesting."""
        return _CustomFieldQueryAnd(*self._queries, other)


class _CustomFieldQueryOr(CustomFieldQuery):
    """Logical OR of two or more sub-expressions: ``["OR", [q0, q1, …]]``.

    Prefer the ``|`` operator over instantiating this class directly::

        q = (
            CustomFieldQuery("Category", "exact", "A")
            | CustomFieldQuery("Category", "exact", "B")
        )
    """

    def __init__(self, *queries: CustomFieldQuery) -> None:
        """Initialise with two or more sub-expressions."""
        self._queries = queries

    def build(self) -> list[Any]:
        """Return the JSON-serialisable list for this expression."""
        return ["OR", [q.build() for q in self._queries]]

    def __or__(self, other: CustomFieldQuery) -> "_CustomFieldQueryOr":
        """Flatten: extend the existing OR instead of nesting."""
        return _CustomFieldQueryOr(*self._queries, other)


class _CustomFieldQueryNot(CustomFieldQuery):
    """Logical NOT of a sub-expression: ``["NOT", q]``.

    Prefer the ``~`` prefix operator over instantiating this class directly::

        q = ~CustomFieldQuery("Archived", "exact", True)
    """

    def __init__(self, query: CustomFieldQuery) -> None:
        """Initialise with the sub-expression to negate."""
        self._query = query

    def build(self) -> list[Any]:
        """Return the JSON-serialisable list for this expression."""
        return ["NOT", self._query.build()]
