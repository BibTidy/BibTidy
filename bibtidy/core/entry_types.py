"""BibLaTeX-style entry types and their required fields.

A "requirement" is a group of interchangeable field names: the requirement is
satisfied when *any* one of the alternatives is present and non-empty (e.g. an
``@article`` needs ``journaltitle`` **or** ``journal``; a ``@book`` needs
``author`` **or** ``editor``). A plain required field is just a one-element
group.

The table leans towards BibLaTeX's extended type system so modern references
(preprints, software, datasets, online resources) are first-class, while still
accepting the classic BibTeX field spellings.
"""

from __future__ import annotations

# Each entry maps an entry type to a tuple of requirement groups.
Requirement = tuple[str, ...]

_DATE: Requirement = ("year", "date")
_AUTHOR_OR_EDITOR: Requirement = ("author", "editor")
_JOURNAL: Requirement = ("journaltitle", "journal")
_INSTITUTION: Requirement = ("institution", "school")

REQUIRED_FIELDS: dict[str, tuple[Requirement, ...]] = {
    "article": (("author",), ("title",), _JOURNAL, _DATE),
    "book": (_AUTHOR_OR_EDITOR, ("title",), ("publisher",), _DATE),
    "mvbook": (_AUTHOR_OR_EDITOR, ("title",), ("publisher",), _DATE),
    "inbook": (("author",), ("title",), ("booktitle",), ("publisher",), _DATE),
    "incollection": (("author",), ("title",), ("booktitle",), ("publisher",), _DATE),
    "inproceedings": (("author",), ("title",), ("booktitle",), _DATE),
    "conference": (("author",), ("title",), ("booktitle",), _DATE),
    "proceedings": (("title",), _DATE),
    "collection": (("editor",), ("title",), _DATE),
    "booklet": (("title",),),
    "standard": (("title",), _DATE),
    "online": (_AUTHOR_OR_EDITOR, ("title",), ("url",), _DATE),
    "electronic": (_AUTHOR_OR_EDITOR, ("title",), ("url",), _DATE),
    "report": (("author",), ("title",), ("type",), _INSTITUTION, _DATE),
    "techreport": (("author",), ("title",), _INSTITUTION, _DATE),
    "thesis": (("author",), ("title",), ("type",), _INSTITUTION, _DATE),
    "phdthesis": (("author",), ("title",), ("school",), _DATE),
    "mastersthesis": (("author",), ("title",), ("school",), _DATE),
    "software": (_AUTHOR_OR_EDITOR, ("title",), _DATE),
    "dataset": (_AUTHOR_OR_EDITOR, ("title",), _DATE),
    "patent": (("author",), ("title",), ("number",), _DATE),
    "manual": (("title",), _DATE),
    "unpublished": (("author",), ("title",), ("note",)),
    # @misc has no strictly required fields in BibLaTeX; kept explicit so it is a
    # *known* type (no "unknown-type" issue) rather than silently absent.
    "misc": (),
}


def isKnownType(entryType: str) -> bool:
    """Return whether ``entryType`` (case-insensitive) is in the type table."""
    return entryType.lower() in REQUIRED_FIELDS
