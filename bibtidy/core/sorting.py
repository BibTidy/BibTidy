"""Standalone entry sorting (in addition to the writer's built-in key order)."""
from __future__ import annotations

from collections.abc import Sequence

from .model import Entry, Library


def _value(entry: Entry, criterion: str) -> str:
    """The string to sort by for one criterion."""
    if criterion == "key":
        return entry.key.lower()
    if criterion == "type":
        return entry.entryType
    return (entry.get(criterion) or "").lower()


def sortedEntries(
    library: Library, sortBy: Sequence[str] = ("key",), reverse: bool = False
) -> list[Entry]:
    """Return the library's entries sorted by the given criteria.

    Sorting is case-insensitive and stable (entries comparing equal retain their
    original relative order). Missing fields sort as the empty string.

    Args:
        library: The library whose entries to sort.
        sortBy: Field names to sort by, in priority order (first used, later ones
            break ties). Special values ``"key"`` and ``"type"`` refer to the
            entry's citation key and BibTeX type respectively.
        reverse: If True, sort in descending order on all criteria.

    Returns:
        A new list of entries; the library itself is not modified.
    """
    return sorted(library, key=lambda e: tuple(_value(e, c) for c in sortBy), reverse=reverse)


def sortLibrary(
    library: Library, sortBy: Sequence[str] = ("key",), reverse: bool = False
) -> Library:
    """Sort the library's entries in place and return it.

    A fluent alias for ``library.entries = sortedEntries(library, sortBy)``.

    Args:
        library: The library to mutate.
        sortBy: Field names to sort by, in the same format as :func:`sortedEntries`.
        reverse: If True, sort in descending order.

    Returns:
        The same library instance (now mutated).
    """
    library.entries = sortedEntries(library, sortBy, reverse)
    return library
