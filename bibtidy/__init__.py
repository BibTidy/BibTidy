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
    assignKeys,
    baseKey,
    merge,
    flagOverlaps,
    matches,
    parseFile,
    parseString,
    parseQuery,
    search,
    sortedEntries,
    sortLibrary,
    toString,
    validate,
    validateEntry,
    writeFile,
    TAGS_FIELD,
    GROUPS_FIELD,
    getTags,
    setTags,
    addTag,
    removeTag,
    getGroups,
    setGroups,
    addGroup,
    removeGroup,
    groupByTag,
    groupByCollection,
    MergeResult,
    Overlap,
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
