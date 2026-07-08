"""Citation-key generation: JabRef-style [auth][year] with a/b/c disambiguation."""
from __future__ import annotations

import re

from .model import Entry, Library

_LATEX_COMMAND = re.compile(r"\\[a-zA-Z]+|\\.")   # \'e, \textbf, ...
_NON_ALNUM = re.compile(r"[^0-9A-Za-z]+")


def _clean(text: str) -> str:
    return _NON_ALNUM.sub("", _LATEX_COMMAND.sub("", text))


def _firstAuthorLastName(entry: Entry) -> str:
    raw = entry.get("author") or entry.get("editor") or ""
    if not raw:
        return ""
    first = raw.split(" and ")[0].strip()
    if "," in first:
        last = first.split(",", 1)[0]
    else:
        tokens = first.split()
        last = tokens[-1] if tokens else ""
    return _clean(last)


def _year(entry: Entry) -> str:
    for source in (entry.get("year"), entry.get("date")):
        match = re.search(r"\d{4}", source or "")
        if match:
            return match.group(0)
    return ""


def baseKey(entry: Entry) -> str:
    """The un-disambiguated [auth][year] key for a single entry."""
    auth = _firstAuthorLastName(entry)
    auth = auth[:1].upper() + auth[1:] if auth else ""
    return f"{auth}{_year(entry)}" or "unknown"


def _suffix(index: int) -> str:
    out, index = "", index + 1
    while index:
        index, rem = divmod(index - 1, 26)
        out = chr(97 + rem) + out
    return out


def assignKeys(
    library: Library, *, overwrite: bool = True, reserved: set[str] | None = None
) -> dict[str, str]:
    """Assign unique keys in place; return {old_key: new_key} for changed entries.

    With overwrite=False, entries that already have a key keep it (only reserved),
    so keygen can fill blanks without disturbing existing keys.
    """
    used: set[str] = set(reserved or ())
    mapping: dict[str, str] = {}
    for entry in library:
        if not overwrite and entry.key:
            used.add(entry.key)
            continue
        base, candidate, i = baseKey(entry), baseKey(entry), 0
        while candidate in used:
            candidate = base + _suffix(i)
            i += 1
        used.add(candidate)
        if candidate != entry.key:
            mapping[entry.key] = candidate
        entry.key = candidate
    return mapping
