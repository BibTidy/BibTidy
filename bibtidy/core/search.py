"""Metadata query search: e.g. `author:smith year:2020 tag:reading-list`."""
from __future__ import annotations

import shlex

from dataclasses import dataclass

from .model import Entry, Library
from .tags import GROUPS_FIELD, TAGS_FIELD

_ALIASES = {
    "tag": TAGS_FIELD,
    "tags": TAGS_FIELD,
    "group": GROUPS_FIELD,
    "collection": GROUPS_FIELD,
    "type": "@type",
    "key": "@key",
}


@dataclass(frozen=True)
class Term:
    """A single parsed query term.

    Attributes:
        field: The field to search, or None for a bare term that matches across
            the key, type and all field values.
        value: The value to look for (always lowercase).
    """

    field: str | None
    value: str


def parseQuery(query: str) -> list[Term]:
    """Split a query string into a list of search terms.

    Terms are space-separated; values containing spaces or shell metacharacters
    can be quoted. A term of the form ``field:value`` is parsed as a specific-field
    search; anything else is a bare term that matches across the full entry text.
    Aliases (``tag``, ``group``, ``type``, ``key``) are resolved to their storage
    names automatically.

    Args:
        query: e.g. ``'author:smith year:2020 "deep learning"'``

    Returns:
        A list of :class:`Term` objects, in the order they appeared in ``query``.
    """
    terms: list[Term] = []
    for token in shlex.split(query):
        field, sep, value = token.partition(":")
        if sep:
            terms.append(Term(_ALIASES.get(field.lower(), field.lower()), value.lower()))
        else:
            terms.append(Term(None, token.lower()))
    return terms


def _text(entry: Entry, field: str) -> str:
    """The lowercase text of an entry's field for searching."""
    if field == "@type":
        return entry.entryType
    if field == "@key":
        return entry.key.lower()
    return (entry.get(field) or "").lower()


def _termMatches(entry: Entry, term: Term) -> bool:
    """Return True if the entry matches a single term."""
    if term.field is None:
        haystack = " ".join(
            [entry.key.lower(), entry.entryType, *(v.lower() for v in entry.fields.values())]
        )
        return term.value in haystack
    return term.value in _text(entry, term.field)


def matches(entry: Entry, terms: list[Term]) -> bool:
    """Return True if an entry matches every term (AND semantics)."""
    return all(_termMatches(entry, t) for t in terms)


def search(library: Library, query: str) -> list[Entry]:
    """Return every entry in the library that satisfies ``query``.

    The query is parsed with :func:`parseQuery`; all terms must match (AND).
    Searching is substring-based and case-insensitive.

    Args:
        library: The library to search.
        query: e.g. ``'author:puys year:2020 tag:reading-list'``

    Returns:
        A list of matching entries, in their original library order.
    """
    terms = parseQuery(query)
    return [entry for entry in library if matches(entry, terms)]
