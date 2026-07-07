"""bibtidy core: data model, parser, canonical writer and validation.

This subpackage has no CLI or GUI dependencies; it is the reusable library that
the (future) CLI and GUI layers wrap.
"""

from __future__ import annotations

from .model import Entry, Library
from .parser import parse_file, parse_string
from .validation import ValidationIssue, validate, validate_entry
from .writer import to_string, write_file

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
