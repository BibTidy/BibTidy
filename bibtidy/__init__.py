"""bibtidy — offline-first BibTeX manager.

Top-level convenience re-exports of the core library, so callers can simply::

    import bibtidy
    lib = bibtidy.parse_file("refs.bib")
    bibtidy.write_file(lib, "refs.bib")
"""

from __future__ import annotations

from .core import (
    Entry,
    Library,
    ValidationIssue,
    parse_file,
    parse_string,
    to_string,
    validate,
    validate_entry,
    write_file,
)

__all__ = [
    "Entry",
    "Library",
    "parse_string",
    "parse_file",
    "to_string",
    "write_file",
    "validate",
    "validate_entry",
    "ValidationIssue",
]
