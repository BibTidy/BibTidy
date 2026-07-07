"""Core data model: :class:`Entry` and :class:`Library`.

These are intentionally thin containers. All BibTeX semantics (how text becomes
entries, how entries become canonical text, what a valid entry is) live in the
sibling modules ``parser``, ``writer`` and ``validation`` — the model just holds
the parsed data.
"""

from __future__ import annotations

from collections.abc import Iterator


class Entry:
    """A single BibTeX entry: a type, a citation key, and ordered fields.

    ``entry_type`` and field names are normalised to lower case so that lookups
    and comparisons are case-insensitive (BibTeX itself is). Field *values* are
    preserved as parsed. Field insertion order is kept; the canonical writer is
    responsible for re-ordering on output.
    """

    __slots__ = ("entry_type", "key", "fields")

    def __init__(
        self,
        entry_type: str,
        key: str,
        fields: dict[str, str] | None = None,
    ) -> None:
        self.entry_type: str = entry_type.lower()
        self.key: str = key
        self.fields: dict[str, str] = {}
        if fields:
            for name, value in fields.items():
                self.set(name, value)

    def get(self, field: str, default: str | None = None) -> str | None:
        """Return the value of ``field`` (case-insensitive) or ``default``."""
        return self.fields.get(field.lower(), default)

    def set(self, field: str, value: str) -> None:
        """Set ``field`` (name lower-cased) to ``value``."""
        self.fields[field.lower()] = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entry):
            return NotImplemented
        return (
            self.entry_type == other.entry_type
            and self.key == other.key
            and self.fields == other.fields
        )

    def __repr__(self) -> str:
        return f"Entry(type={self.entry_type!r}, key={self.key!r}, fields={self.fields!r})"


class Library:
    """An ordered collection of :class:`Entry` objects.

    Duplicate citation keys are permitted at this stage (real de-duplication is a
    later milestone); :meth:`duplicate_keys` surfaces any collisions.
    """

    __slots__ = ("entries",)

    def __init__(self, entries: list[Entry] | None = None) -> None:
        self.entries: list[Entry] = list(entries) if entries else []

    def add(self, entry: Entry) -> None:
        """Append ``entry`` to the library."""
        self.entries.append(entry)

    def get(self, key: str) -> Entry | None:
        """Return the first entry whose citation key is ``key``, else ``None``."""
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def require(self, key: str) -> Entry:
        """Return the first entry with citation key ``key`` or raise ``KeyError``."""
        entry = self.get(key)
        if entry is None:
            raise KeyError(key)
        return entry

    def keys(self) -> list[str]:
        """Return the citation keys in insertion order (duplicates included)."""
        return [entry.key for entry in self.entries]

    def duplicate_keys(self) -> list[str]:
        """Return citation keys that appear more than once, in first-seen order."""
        seen: set[str] = set()
        dupes: dict[str, None] = {}
        for key in self.keys():
            if key in seen:
                dupes[key] = None
            seen.add(key)
        return list(dupes)

    def __iter__(self) -> Iterator[Entry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return f"Library({len(self.entries)} entries)"
