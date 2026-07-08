"""bibtidy core: data model, parser, canonical writer and validation.

This subpackage has no CLI or GUI dependencies; it is the reusable library that
the (future) CLI and GUI layers wrap.
"""

from __future__ import annotations

from .model import Entry, Library
from .parser import parseFile, parseString
from .validation import ValidationIssue, validate, validateEntry
from .writer import toString, writeFile

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
