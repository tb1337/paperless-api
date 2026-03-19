"""Tests for the SearchQuery DSL builder."""

import pytest

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
    assert str(SearchQuery.field("type", "invoice")) == "type:invoice"
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


def test_and_direct_instantiation() -> None:
    """_SearchQueryAnd can be instantiated directly with multiple queries."""
    q = _SearchQueryAnd(SearchQuery("x"), SearchQuery("y"), SearchQuery("z"))
    assert str(q) == "(x AND y AND z)"


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


def test_or_direct_instantiation() -> None:
    """_SearchQueryOr can be instantiated directly with multiple queries."""
    q = _SearchQueryOr(SearchQuery("x"), SearchQuery("y"))
    assert str(q) == "(x OR y)"


# ---------------------------------------------------------------------------
# NOT
# ---------------------------------------------------------------------------


def test_not_operator() -> None:
    """``~`` wraps an atom into a _SearchQueryNot."""
    q = ~SearchQuery.field("type", "letter")
    assert isinstance(q, _SearchQueryNot)
    assert str(q) == "NOT type:letter"


def test_not_of_compound() -> None:
    """``~`` can negate a compound expression."""
    inner = SearchQuery("a") | SearchQuery("b")
    q = ~inner
    assert str(q) == "NOT (a OR b)"


# ---------------------------------------------------------------------------
# Combined expressions
# ---------------------------------------------------------------------------


def test_combined_and_or_not() -> None:
    """Complex combined expression serialises correctly."""
    q = (
        SearchQuery("invoice")
        & SearchQuery.field("tag", "unpaid")
        & ~SearchQuery.field("type", "letter")
    )
    assert str(q) == "(invoice AND tag:unpaid AND NOT type:letter)"


def test_nested_and_in_or() -> None:
    """AND inside OR produces correctly parenthesised output."""
    inner = SearchQuery("a") & SearchQuery("b")
    q = inner | SearchQuery("c")
    assert str(q) == "((a AND b) OR c)"


def test_date_range_in_expression() -> None:
    """Date-range terms combine naturally with other atoms."""
    q = SearchQuery("warranty") & SearchQuery.date_range("created", "2020", "2022")
    assert str(q) == "(warranty AND created:[2020 to 2022])"


# ---------------------------------------------------------------------------
# str passthrough — service accepts both str and SearchQuery
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (SearchQuery("test"), "test"),
        (SearchQuery.field("tag", "x"), "tag:x"),
        (SearchQuery("a") & SearchQuery("b"), "(a AND b)"),
    ],
)
def test_str_conversion(query: SearchQuery, expected: str) -> None:
    """str() on any SearchQuery subclass yields the expected Whoosh string."""
    assert str(query) == expected
