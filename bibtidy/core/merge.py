"""Merge libraries; report key collisions and provisional likely-duplicate overlaps."""
from __future__ import annotations

import re

from dataclasses import dataclass, field

from .model import Entry, Library

_NON_ALNUM = re.compile(r"[^0-9a-z]+")


@dataclass(frozen=True)
class Overlap:
    """An entry pair that shares a strong identifying attribute.

    Attributes:
        reason: The kind of match: ``"doi"`` (exact DOI) or ``"title"``
            (alphanumeric-normalised title).
        value: The matching value (e.g. the DOI string).
        keys: The citation keys of the colliding entries, in first-seen order.
    """

    reason: str
    value: str
    keys: tuple[str, ...]


@dataclass
class MergeResult:
    """The outcome of merging one or more libraries.

    Attributes:
        library: The concatenated library (entries kept as-is from each input).
        keyCollisions: Citation keys that appeared in more than one input library,
            in first-seen order.
        likelyDuplicates: Entry pairs that share a strong identifier (DOI or title)
            and may be the same work. This is a provisional stub; see :func:`flagOverlaps`.
    """

    library: Library
    keyCollisions: list[str] = field(default_factory=list)
    likelyDuplicates: list[Overlap] = field(default_factory=list)


def _normDoi(entry: Entry) -> str:
    return (entry.get("doi") or "").strip().lower()


def _normTitle(entry: Entry) -> str:
    return _NON_ALNUM.sub("", (entry.get("title") or "").lower())


def flagOverlaps(library: Library) -> list[Overlap]:
    """Flag entries that share a strong identifier.

    PROVISIONAL pre-M3 stub: only exact DOI and exact normalised-title are checked.
    The real DOI + fuzzy-title dedup algorithm is designed and implemented in M3.

    Two entries are flagged if they share the same non-empty DOI (case-insensitive)
    or the same title after stripping non-alphanumeric characters and lowercasing.
    """
    overlaps: list[Overlap] = []
    for reason, keyfn in (("doi", _normDoi), ("title", _normTitle)):
        buckets: dict[str, list[str]] = {}
        for entry in library:
            value = keyfn(entry)
            if value:
                buckets.setdefault(value, []).append(entry.key)
        overlaps += [
            Overlap(reason, v, tuple(k)) for v, k in buckets.items() if len(k) > 1
        ]
    return overlaps


def merge(libraries: list[Library]) -> MergeResult:
    """Concatenate ``libraries`` into a single :class:`MergeResult`.

    Entries are added to the result library in input order, with all fields
    preserved. Citation key collisions (entries with the same key from different
    libraries) and likely-duplicate overlaps (same DOI or same normalised title)
    are surfaced alongside the merged library.

    Args:
        libraries: The libraries to merge.

    Returns:
        A :class:`MergeResult` with the concatenated library and reports.
    """
    merged = Library()
    for lib in libraries:
        for entry in lib:
            merged.add(entry)
    return MergeResult(merged, merged.duplicateKeys(), flagOverlaps(merged))
