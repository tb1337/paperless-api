"""Fluent builder for Tantivy search queries (``/api/search/?query=…``).

Combine atoms with ``&`` (AND), ``|`` (OR) and ``~`` (NOT), then pass
``str(q)`` — or the builder itself — as the ``query`` argument to
:meth:`~pypaperless.services.search.SearchService.__call__`::

    from pypaperless.builders.search import SearchQuery

    q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
    result = await paperless.search(q)

Use :meth:`SearchQuery.field` and :meth:`SearchQuery.date_range` for
field-scoped and date-range terms.  Raw Tantivy query strings are also
accepted — just pass a ``str`` to the service instead of a builder object.
"""

from typing import Literal

# The following list is based on the schema defined in:
# https://github.com/paperless-ngx/paperless-ngx/blob/dev/src/documents/search/_schema.py
# -> build_schema()

type _SearchField = Literal[
    "id",
    "title",
    "content",
    "asn",
    "correspondent",
    "correspondent_id",
    "tag",
    "tag_id",
    "document_type",
    "document_type_id",
    "storage_path",
    "storage_path_id",
    "created",
    "modified",
    "added",
    "notes.note",
    "notes.user",
    "num_notes",
    "custom_fields.value",
    "custom_fields.name",
    "owner",
    "owner_id",
    "viewer_id",
    "checksum",
    "page_count",
    "original_filename",
]

type _SearchDateField = Literal["created", "modified", "added"]

# The following list is based on the _DATE_KEYWORDS constant defined in:
# https://github.com/paperless-ngx/paperless-ngx/blob/dev/src/documents/search/_query.py
# -> rewrite_natural_date_keywords()

type _SearchDateKeyword = Literal[
    "today",
    "yesterday",
    "this month",
    "previous month",
    "previous week",
    "previous quarter",
    "this year",
    "previous year",
]


class SearchQuery:
    """A single term or Tantivy query fragment.

    Use the ``&``, ``|``, ``~`` operators to combine atoms into boolean
    expressions.  Call :func:`str` on the result to obtain the query string
    accepted by ``/api/search/``.  Both raw strings and ``SearchQuery``
    objects are accepted by the service::

        q1 = SearchQuery("invoice")               # plain term
        q2 = SearchQuery.field("tag", "unpaid")   # tag:unpaid
        q3 = SearchQuery.date_range("created", "2020", "2022")

        result = await paperless.search(q1 & q2)  # "(invoice AND tag:unpaid)"

    """

    def __init__(self, term: str) -> None:
        """Initialise with a raw Tantivy query term."""
        self._term = term

    @classmethod
    def field(cls, field_name: _SearchField, value: str | _SearchDateKeyword) -> "SearchQuery":
        """Build a field-scoped term: ``field_name:value``.

        Args:
            field_name: The Paperless field to scope the search to, e.g.
                        ``"document_type"``, ``"tag"``, ``"correspondent"``.
            value:      The exact value to match within that field.

        Example::

            SearchQuery.field("tag", "unpaid")                  # → tag:unpaid
            SearchQuery.field("document_type", "invoice")       # → document_type:invoice
            SearchQuery.field("correspondent", "acme")          # → correspondent:acme
            SearchQuery.field("notes.note", "urgent")           # → notes.note:urgent
            SearchQuery.field("custom_fields.name", "amount")   # → custom_fields.name:amount

        """
        return cls(f"{field_name}:{value}")

    @classmethod
    def date_range(
        cls,
        field_name: _SearchDateField,
        start: str | _SearchDateKeyword,
        end: str | _SearchDateKeyword,
    ) -> "SearchQuery":
        """Build a date-range term: ``field_name:[start to end]``.

        Args:
            field_name: The date field, e.g. ``"created"``, ``"added"``,
                        ``"modified"``.
            start:      Range start (year, ISO date, or ``"today"`` /
                        ``"yesterday"``, ...).
            end:        Range end (same formats as *start*).

        Example::

            SearchQuery.date_range("created", "2005", "2009")
            # → created:[2005 to 2009]

            SearchQuery.date_range("added", "yesterday", "today")
            # → added:[yesterday to today]

        """
        return cls(f"{field_name}:[{start} to {end}]")

    def build(self) -> str:
        """Return the Tantivy query fragment for this expression."""
        return self._term

    def __str__(self) -> str:
        """Serialise to the query string expected by ``/api/search/``."""
        return self.build()

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}({self.build()!r})"

    def __and__(self, other: "SearchQuery") -> "_SearchQueryAnd":
        """Combine with *other* using logical AND."""
        return _SearchQueryAnd(self, other)

    def __or__(self, other: "SearchQuery") -> "_SearchQueryOr":
        """Combine with *other* using logical OR."""
        return _SearchQueryOr(self, other)

    def __invert__(self) -> "_SearchQueryNot":
        """Negate this expression."""
        return _SearchQueryNot(self)


class _SearchQueryAnd(SearchQuery):
    """Logical AND of two or more sub-expressions: ``(q0 AND q1 …)``.

    Prefer the ``&`` operator over instantiating this class directly::

        q = (
            SearchQuery("invoice")
            & SearchQuery.field("tag", "unpaid")
            & SearchQuery.date_range("created", "2020", "2022")
        )
        # str(q) → "(invoice AND tag:unpaid AND created:[2020 to 2022])"
    """

    def __init__(self, *queries: SearchQuery) -> None:
        """Initialise with two or more sub-expressions."""
        self._queries = queries

    def build(self) -> str:
        """Return the Tantivy query fragment for this AND expression."""
        return "(" + " AND ".join(q.build() for q in self._queries) + ")"

    def __and__(self, other: SearchQuery) -> "_SearchQueryAnd":
        """Flatten: extend the existing AND instead of nesting."""
        return _SearchQueryAnd(*self._queries, other)


class _SearchQueryOr(SearchQuery):
    """Logical OR of two or more sub-expressions: ``(q0 OR q1 …)``.

    Prefer the ``|`` operator over instantiating this class directly::

        q = SearchQuery.field("tag", "inbox") | SearchQuery.field("tag", "important")
        # str(q) → "(tag:inbox OR tag:important)"
    """

    def __init__(self, *queries: SearchQuery) -> None:
        """Initialise with two or more sub-expressions."""
        self._queries = queries

    def build(self) -> str:
        """Return the Tantivy query fragment for this OR expression."""
        return "(" + " OR ".join(q.build() for q in self._queries) + ")"

    def __or__(self, other: SearchQuery) -> "_SearchQueryOr":
        """Flatten: extend the existing OR instead of nesting."""
        return _SearchQueryOr(*self._queries, other)


class _SearchQueryNot(SearchQuery):
    """Logical NOT of a sub-expression: ``NOT q``.

    Prefer the ``~`` prefix operator over instantiating this class directly::

        q = ~SearchQuery.field("document_type", "letter")
        # str(q) → "NOT document_type:letter"
    """

    def __init__(self, query: SearchQuery) -> None:
        """Initialise with the sub-expression to negate."""
        self._query = query

    def build(self) -> str:
        """Return the Tantivy query fragment for this NOT expression."""
        return f"NOT {self._query.build()}"
