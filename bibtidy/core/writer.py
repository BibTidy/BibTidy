"""Canonical BibTeX writer.

Every save rewrites the *entire* library in one deterministic shape, so a file's
formatting never depends on its editing history:

* entries are ordered by citation key;
* fields are ordered by a fixed priority list, then alphabetically;
* values are always brace-delimited (any quoted value read is written braced);
* a fixed two-space indent, one field per line, blank line between entries.

The output is a fixed point of the parser: ``write(parse(write(x)))`` equals
``write(x)``.
"""

from __future__ import annotations

from pathlib import Path

from .model import Entry, Library

# Common fields in a deliberate reading order; everything else follows,
# alphabetically. Names are lower-case to match the model's normalisation.
_FIELD_PRIORITY: tuple[str, ...] = (
    "author",
    "editor",
    "title",
    "booktitle",
    "journal",
    "journaltitle",
    "school",
    "institution",
    "organization",
    "publisher",
    "howpublished",
    "series",
    "edition",
    "volume",
    "number",
    "chapter",
    "pages",
    "year",
    "month",
    "address",
    "doi",
    "isbn",
    "issn",
    "url",
    "urldate",
    "note",
    "keywords",
    "abstract",
)

_PRIORITY_INDEX: dict[str, int] = {name: i for i, name in enumerate(_FIELD_PRIORITY)}

INDENT = "  "


def _field_sort_key(name: str) -> tuple[int, str]:
    """Priority-listed fields first (in list order), then the rest alphabetically."""
    return (_PRIORITY_INDEX.get(name, len(_FIELD_PRIORITY)), name)


def _format_entry(entry: Entry) -> str:
    """Render a single entry in canonical form."""
    lines = [f"@{entry.entry_type}{{{entry.key},"]
    for name in sorted(entry.fields, key=_field_sort_key):
        lines.append(f"{INDENT}{name} = {{{entry.fields[name]}}},")
    lines.append("}")
    return "\n".join(lines)


def to_string(library: Library) -> str:
    """Return the whole library as canonical BibTeX text.

    Entries are sorted by citation key (ties broken by entry type, so ordering
    is total and stable even when keys collide).
    """
    entries = sorted(library, key=lambda e: (e.key, e.entry_type))
    blocks = [_format_entry(entry) for entry in entries]
    if not blocks:
        return ""
    return "\n\n".join(blocks) + "\n"


def write_file(library: Library, path: str | Path) -> None:
    """Write the library to ``path`` as canonical UTF-8 BibTeX."""
    Path(path).write_text(to_string(library), encoding="utf-8")
