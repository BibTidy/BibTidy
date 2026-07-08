"""bibtidy — offline-first BibTeX manager.

Top-level convenience re-exports of the core library, so callers can simply::

    import bibtidy
    lib = bibtidy.parseFile("refs.bib")
    bibtidy.writeFile(lib, "refs.bib")
"""

from __future__ import annotations

from .core import (
    Entry,
    Library,
    ValidationIssue,
    parseFile,
    parseString,
    toString,
    validate,
    validateEntry,
    writeFile,
)

__all__ = [
    "Entry",
    "Library",
    "parseString",
    "parseFile",
    "toString",
    "writeFile",
    "validate",
    "validateEntry",
    "ValidationIssue",
]
