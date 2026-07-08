"""Tags & collections, stored as custom BibTeX fields (never `keywords`)."""
from __future__ import annotations

from collections.abc import Iterable

from .model import Entry, Library

TAGS_FIELD = "bibtidytags"
GROUPS_FIELD = "bibtidygroups"


def _get(entry: Entry, field: str) -> list[str]:
    return [p.strip() for p in (entry.get(field) or "").split(",") if p.strip()]


def _set(entry: Entry, field: str, values: Iterable[str]) -> None:
    canon = sorted({v.strip() for v in values if v.strip()})
    if canon:
        entry.set(field, ", ".join(canon))
    else:
        entry.fields.pop(field, None)


def getTags(entry: Entry) -> list[str]:
    """Return the list of ``bibtidytags`` on an entry, in file order."""
    return _get(entry, TAGS_FIELD)


def setTags(entry: Entry, tags: Iterable[str]) -> None:
    """Replace the ``bibtidytags`` field.

    Values are canonicalised on write: stripped, de-duplicated, and sorted
    alphabetically, so the on-disk representation is a stable fixed point.
    An empty iterable removes the field entirely.
    """
    _set(entry, TAGS_FIELD, tags)


def addTag(entry: Entry, tag: str) -> None:
    """Append ``tag`` to the entry's tag list (silently ignores duplicates)."""
    setTags(entry, [*getTags(entry), tag])


def removeTag(entry: Entry, tag: str) -> None:
    """Remove ``tag`` from the entry's tag list (no-op if absent)."""
    setTags(entry, [t for t in getTags(entry) if t != tag])


def getGroups(entry: Entry) -> list[str]:
    """Return the list of ``bibtidygroups`` on an entry, in file order."""
    return _get(entry, GROUPS_FIELD)


def setGroups(entry: Entry, groups: Iterable[str]) -> None:
    """Replace the ``bibtidygroups`` field, with the same canonicalisation as
    :func:`setTags`."""
    _set(entry, GROUPS_FIELD, groups)


def addGroup(entry: Entry, group: str) -> None:
    """Append ``group`` to the entry's group list (silently ignores duplicates)."""
    setGroups(entry, [*getGroups(entry), group])


def removeGroup(entry: Entry, group: str) -> None:
    """Remove ``group`` from the entry's group list (no-op if absent)."""
    setGroups(entry, [g for g in getGroups(entry) if g != group])


def groupBy(library: Library, field: str) -> dict[str, list[Entry]]:
    """Return a dict mapping each comma-separated value of ``field`` to the
    entries that carry it.

    Entries not containing ``field`` at all are absent from every value list.
    """
    out: dict[str, list[Entry]] = {}
    for entry in library:
        for label in _get(entry, field):
            out.setdefault(label, []).append(entry)
    return out


def groupByTag(library: Library) -> dict[str, list[Entry]]:
    """Partition the library by ``bibtidytags`` value."""
    return groupBy(library, TAGS_FIELD)


def groupByCollection(library: Library) -> dict[str, list[Entry]]:
    """Partition the library by ``bibtidygroups`` value."""
    return groupBy(library, GROUPS_FIELD)
