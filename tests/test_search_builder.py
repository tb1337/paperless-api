"""Tests for the SearchQuery DSL builder."""

from pypaperless.builders import SearchQuery
from pypaperless.builders.search import _SearchQueryAnd, _SearchQueryNot, _SearchQueryOr

# ---------------------------------------------------------------------------
# Atom
# ---------------------------------------------------------------------------


def test_atom_build() -> None:
    """A plain atom builds to its term string."""
    q = SearchQuery("invoice")
    assert q.build() == "invoice"
    assert str(q) == "invoice"


def test_atom_repr() -> None:
    """repr() contains the class name and the term."""
    q = SearchQuery("invoice")
    assert "SearchQuery" in repr(q)
    assert "invoice" in repr(q)


# ---------------------------------------------------------------------------
# Factory class-methods
# ---------------------------------------------------------------------------


def test_field_factory() -> None:
    """SearchQuery.field() produces a ``field:value`` term."""
    assert str(SearchQuery.field("tag", "unpaid")) == "tag:unpaid"
    assert str(SearchQuery.field("document_type", "invoice")) == "document_type:invoice"
    assert str(SearchQuery.field("correspondent", "acme")) == "correspondent:acme"


def test_date_range_factory() -> None:
    """SearchQuery.date_range() produces a ``field:[start to end]`` term."""
    q = SearchQuery.date_range("created", "2005", "2009")
    assert str(q) == "created:[2005 to 2009]"

    q2 = SearchQuery.date_range("added", "yesterday", "today")
    assert str(q2) == "added:[yesterday to today]"


# ---------------------------------------------------------------------------
# AND
# ---------------------------------------------------------------------------


def test_and_operator() -> None:
    """``&`` combines two atoms into a _SearchQueryAnd."""
    q = SearchQuery("invoice") & SearchQuery.field("tag", "unpaid")
    assert isinstance(q, _SearchQueryAnd)
    assert str(q) == "(invoice AND tag:unpaid)"


def test_and_flatten() -> None:
    """Chaining ``&`` flattens into a single level (no extra parentheses)."""
    q = SearchQuery("a") & SearchQuery("b") & SearchQuery("c")
    assert isinstance(q, _SearchQueryAnd)
    assert str(q) == "(a AND b AND c)"


# ---------------------------------------------------------------------------
# OR
# ---------------------------------------------------------------------------


def test_or_operator() -> None:
    """``|`` combines two atoms into a _SearchQueryOr."""
    q = SearchQuery.field("tag", "inbox") | SearchQuery.field("tag", "important")
    assert isinstance(q, _SearchQueryOr)
    assert str(q) == "(tag:inbox OR tag:important)"


def test_or_flatten() -> None:
    """Chaining ``|`` flattens into a single level (no extra parentheses)."""
    q = SearchQuery("a") | SearchQuery("b") | SearchQuery("c")
    assert isinstance(q, _SearchQueryOr)
    assert str(q) == "(a OR b OR c)"


# ---------------------------------------------------------------------------
# NOT
# ---------------------------------------------------------------------------


def test_not_operator() -> None:
    """``~`` wraps an atom into a _SearchQueryNot."""
    q = ~SearchQuery.field("document_type", "letter")
    assert isinstance(q, _SearchQueryNot)
    assert str(q) == "NOT document_type:letter"


# ---------------------------------------------------------------------------
# Tantivy field renames and new JSON sub-fields
# ---------------------------------------------------------------------------


def test_renamed_fields() -> None:
    """document_type and storage_path use the correct Tantivy field names."""
    assert str(SearchQuery.field("document_type", "invoice")) == "document_type:invoice"
    assert str(SearchQuery.field("document_type_id", "5")) == "document_type_id:5"
    assert str(SearchQuery.field("storage_path", "archive")) == "storage_path:archive"
    assert str(SearchQuery.field("storage_path_id", "3")) == "storage_path_id:3"


def test_notes_subfields() -> None:
    """JSON sub-field syntax for notes produces ``notes.note:`` and ``notes.user:`` terms."""
    assert str(SearchQuery.field("notes.note", "urgent")) == "notes.note:urgent"
    assert str(SearchQuery.field("notes.user", "alice")) == "notes.user:alice"


def test_custom_fields_subfields() -> None:
    """JSON sub-field syntax for custom_fields produces the correct dotted terms."""
    assert str(SearchQuery.field("custom_fields.value", "42")) == "custom_fields.value:42"
    assert str(SearchQuery.field("custom_fields.name", "amount")) == "custom_fields.name:amount"
