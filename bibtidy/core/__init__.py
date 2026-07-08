"""bibtidy core: data model, parser, canonical writer and validation.

This subpackage has no CLI or GUI dependencies; it is the reusable library that
the (future) CLI and GUI layers wrap.
"""

from __future__ import annotations

from .keygen import assignKeys, baseKey
from .merge import MergeResult, Overlap, flagOverlaps, merge
from .model import Entry, Library
from .parser import parseFile, parseString
from .search import matches, parseQuery, search
from .sorting import sortLibrary, sortedEntries
from .tags import (
    TAGS_FIELD,
    GROUPS_FIELD,
    addGroup,
    addTag,
    getGroups,
    getTags,
    groupByCollection,
    groupByTag,
    removeGroup,
    removeTag,
    setGroups,
    setTags,
)
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
    "baseKey",
    "assignKeys",
    "sortedEntries",
    "sortLibrary",
    "parseQuery",
    "matches",
    "search",
    "TAGS_FIELD",
    "GROUPS_FIELD",
    "getTags",
    "setTags",
    "addTag",
    "removeTag",
    "getGroups",
    "setGroups",
    "addGroup",
    "removeGroup",
    "groupByTag",
    "groupByCollection",
    "merge",
    "flagOverlaps",
    "MergeResult",
    "Overlap",
]
