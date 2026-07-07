"""Hand-rolled BibTeX parser.

A single sequential scan over the source text, rather than a global regular
expression, so that ``key = {value}`` patterns appearing *inside* a field value
(URLs, notes, abstracts) can never be mistaken for real fields. This is what
makes the parse/write round-trip trustworthy.

Scope (v1): standard ``@type{key, field = value, ...}`` entries with brace- or
quote-delimited values, nested braces, backslash escapes and bare (numeric or
macro-token) values. ``@string`` / ``@preamble`` / ``@comment`` blocks are
skipped, not expanded; ``crossref`` / ``xdata`` inheritance is not resolved.
Input is assumed UTF-8; values are kept as-is apart from whitespace being
collapsed to single spaces (a stable fixed point for idempotent rewriting).
"""

from __future__ import annotations

import re
from pathlib import Path

from .model import Entry, Library

# Block types that are valid BibTeX but explicitly out of scope for v1. They are
# recognised only so their body can be skipped cleanly instead of derailing the
# scan.
_SKIPPED_BLOCKS = frozenset({"string", "preamble", "comment"})

_WHITESPACE_RUN = re.compile(r"\s+")


def _normalise_value(raw: str) -> str:
    """Collapse whitespace runs to single spaces and strip the ends."""
    return _WHITESPACE_RUN.sub(" ", raw).strip()


class _Scanner:
    """Cursor over the source text with the small primitives the parser needs."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.i = 0
        self.n = len(text)

    def skip_whitespace(self) -> None:
        """Advance the cursor past any run of whitespace."""
        while self.i < self.n and self.text[self.i].isspace():
            self.i += 1

    def read_delimited(self, close: str) -> str:
        """Read a ``{...}`` or ``"..."`` value; ``self.i`` sits just past the open.

        Brace depth is tracked (so a ``"`` inside braces does not close a quoted
        value); a backslash escapes the next character so LaTeX literals like
        ``\\{`` do not unbalance the count. Returns the raw inner text.
        """
        start = self.i
        depth = 1 if close == "}" else 0
        escaped = False
        while self.i < self.n:
            char = self.text[self.i]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "{":
                depth += 1
            elif char == "}":
                if close == "}":
                    depth -= 1
                    if depth == 0:
                        value = self.text[start:self.i]
                        self.i += 1
                        return value
                else:
                    depth -= 1
            elif char == '"' and close == '"' and depth == 0:
                value = self.text[start:self.i]
                self.i += 1
                return value
            self.i += 1
        # Unterminated value: return whatever we captured.
        return self.text[start:self.i]

    def read_bare(self) -> str:
        """Read an unquoted value (number or macro token) up to ``,`` or ``}``."""
        start = self.i
        while self.i < self.n and self.text[self.i] not in ",}":
            self.i += 1
        return self.text[start:self.i]


def _parse_entry_body(scanner: _Scanner, entry: Entry) -> None:
    """Parse ``field = value`` pairs until the entry's closing brace."""
    text = scanner.text
    while scanner.i < scanner.n:
        scanner.skip_whitespace()
        if scanner.i >= scanner.n:
            break
        char = text[scanner.i]
        if char == "}":
            scanner.i += 1  # consume the closing brace; entry complete
            return
        if char == ",":
            scanner.i += 1  # separator between fields
            continue

        # Read the field name up to '='. If there is no '=' before the entry
        # ends, the entry is malformed from here on — stop.
        eq = text.find("=", scanner.i)
        end = text.find("}", scanner.i)
        if eq == -1 or (end != -1 and end < eq):
            scanner.i = end + 1 if end != -1 else scanner.n
            return
        name = text[scanner.i:eq].strip()
        scanner.i = eq + 1
        scanner.skip_whitespace()

        if scanner.i >= scanner.n:
            break
        delim = text[scanner.i]
        if delim == "{":
            scanner.i += 1
            raw = scanner.read_delimited("}")
        elif delim == '"':
            scanner.i += 1
            raw = scanner.read_delimited('"')
        else:
            raw = scanner.read_bare()

        if name:
            entry.set(name, _normalise_value(raw))


def parse_string(text: str) -> Library:
    """Parse BibTeX ``text`` into a :class:`Library`."""
    scanner = _Scanner(text)
    library = Library()

    while True:
        at = text.find("@", scanner.i)
        if at == -1:
            break
        scanner.i = at + 1

        # Entry / block type: a run of letters immediately after '@'.
        start = scanner.i
        while scanner.i < scanner.n and text[scanner.i].isalpha():
            scanner.i += 1
        entry_type = text[start:scanner.i].lower()
        if not entry_type:
            continue

        scanner.skip_whitespace()
        if scanner.i >= scanner.n or text[scanner.i] != "{":
            continue  # a stray '@' — resume scanning
        scanner.i += 1  # consume the opening brace

        if entry_type in _SKIPPED_BLOCKS:
            scanner.read_delimited("}")
            continue

        # Citation key: everything up to the first ',' (or the brace for a
        # field-less entry).
        scanner.skip_whitespace()
        key_start = scanner.i
        while scanner.i < scanner.n and text[scanner.i] not in ",} \t\r\n":
            scanner.i += 1
        key = text[key_start:scanner.i].strip()
        if not key:
            continue

        entry = Entry(entry_type, key)

        scanner.skip_whitespace()
        if scanner.i < scanner.n and text[scanner.i] == ",":
            scanner.i += 1
            _parse_entry_body(scanner, entry)
        elif scanner.i < scanner.n and text[scanner.i] == "}":
            scanner.i += 1  # field-less entry, e.g. @misc{key}

        library.add(entry)

    return library


def parse_file(path: str | Path) -> Library:
    """Read a UTF-8 ``.bib`` file and parse it into a :class:`Library`."""
    text = Path(path).read_text(encoding="utf-8")
    return parse_string(text)
