"""Validation of required fields per entry type."""

from __future__ import annotations

from bibtidy import Entry, Library, parseString, validate, validateEntry
from bibtidy.core.validation import MISSING_REQUIRED, UNKNOWN_TYPE


def test_complete_article_is_valid() -> None:
    entry = Entry(
        "article",
        "k",
        {"author": "A", "title": "T", "journal": "J", "year": "2020"},
    )
    assert validateEntry(entry) == []


def test_missing_required_reported() -> None:
    entry = Entry("article", "k", {"author": "A", "title": "T"})
    issues = validateEntry(entry)
    assert len(issues) == 1
    issue = issues[0]
    assert issue.kind == MISSING_REQUIRED
    # journal/journaltitle and year/date are both unsatisfied.
    missing_flat = {name for group in issue.missing for name in group}
    assert "journal" in missing_flat
    assert "year" in missing_flat


def test_alternative_field_satisfies_requirement() -> None:
    # journaltitle satisfies the journal|journaltitle group; date satisfies year.
    entry = Entry(
        "article",
        "k",
        {"author": "A", "title": "T", "journaltitle": "J", "date": "2020"},
    )
    assert validateEntry(entry) == []


def test_author_or_editor_alternative() -> None:
    book = Entry("book", "k", {"editor": "E", "title": "T", "publisher": "P", "year": "1"})
    assert validateEntry(book) == []


def test_empty_field_does_not_satisfy() -> None:
    entry = Entry("article", "k", {"author": "A", "title": "T", "journal": "  ", "year": "2020"})
    issues = validateEntry(entry)
    assert len(issues) == 1
    assert any("journaltitle" in group or "journal" in group for group in issues[0].missing)


def test_unknown_type() -> None:
    entry = Entry("blogpost", "k", {"title": "T"})
    issues = validateEntry(entry)
    assert len(issues) == 1
    assert issues[0].kind == UNKNOWN_TYPE


def test_misc_has_no_required_fields() -> None:
    assert validateEntry(Entry("misc", "k", {})) == []


def test_validate_library_in_order() -> None:
    lib = parseString(
        "@article{good, author={A}, title={T}, journal={J}, year={2020}}"
        "@article{bad, title={T}}"
    )
    issues = validate(lib)
    assert len(issues) == 1
    assert issues[0].key == "bad"


def test_issue_str_is_readable() -> None:
    issues = validate(Library([Entry("article", "bad", {"title": "T"})]))
    text = str(issues[0])
    assert "bad" in text and "missing required" in text
