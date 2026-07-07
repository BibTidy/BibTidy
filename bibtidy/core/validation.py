"""Validation: report entries missing required fields for their type."""

from __future__ import annotations

from dataclasses import dataclass, field

from .entry_types import REQUIRED_FIELDS, Requirement
from .model import Entry, Library

UNKNOWN_TYPE = "unknown-type"
MISSING_REQUIRED = "missing-required"


@dataclass(frozen=True)
class ValidationIssue:
    """A single problem found with an entry.

    ``kind`` is either :data:`UNKNOWN_TYPE` (the entry type is not in the type
    table) or :data:`MISSING_REQUIRED` (one or more required field groups are
    unsatisfied). For the latter, ``missing`` lists the unsatisfied groups; a
    group with more than one name means "any one of these" was expected.
    """

    key: str
    entry_type: str
    kind: str
    missing: tuple[Requirement, ...] = field(default=())

    def __str__(self) -> str:
        if self.kind == UNKNOWN_TYPE:
            return f"{self.key} (@{self.entry_type}): unknown entry type"
        wants = ", ".join(" | ".join(group) for group in self.missing)
        return f"{self.key} (@{self.entry_type}): missing required field(s): {wants}"


def _is_satisfied(entry: Entry, group: Requirement) -> bool:
    """A requirement group is met if any alternative is present and non-empty."""
    return any((entry.get(name) or "").strip() for name in group)


def validate_entry(entry: Entry) -> list[ValidationIssue]:
    """Return the issues for a single entry (empty list if it is valid)."""
    requirements = REQUIRED_FIELDS.get(entry.entry_type)
    if requirements is None:
        return [ValidationIssue(entry.key, entry.entry_type, UNKNOWN_TYPE)]

    missing = tuple(g for g in requirements if not _is_satisfied(entry, g))
    if missing:
        return [ValidationIssue(entry.key, entry.entry_type, MISSING_REQUIRED, missing)]
    return []


def validate(library: Library) -> list[ValidationIssue]:
    """Return all validation issues across the library, in entry order."""
    issues: list[ValidationIssue] = []
    for entry in library:
        issues.extend(validate_entry(entry))
    return issues
