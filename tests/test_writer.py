"""Canonical writer: field order, entry order, brace-only, layout."""

from __future__ import annotations

from bibtidy import Entry, Library, parseString, toString


def test_field_priority_then_alphabetical() -> None:
    entry = Entry(
        "article",
        "k",
        {
            "zzz": "1",
            "year": "2020",
            "author": "A",
            "title": "T",
            "aaa": "2",
            "journal": "J",
        },
    )
    lib = Library([entry])
    lines = toString(lib).splitlines()
    field_names = [ln.split("=")[0].strip() for ln in lines if "=" in ln]
    # Priority fields keep their listed order; unknown fields follow, sorted.
    assert field_names == ["author", "title", "journal", "year", "aaa", "zzz"]


def test_entries_sorted_by_key() -> None:
    lib = Library(
        [
            Entry("misc", "Charlie", {"year": "3"}),
            Entry("misc", "Alpha", {"year": "1"}),
            Entry("misc", "Bravo", {"year": "2"}),
        ]
    )
    out = toString(lib)
    assert out.index("Alpha") < out.index("Bravo") < out.index("Charlie")


def test_quotes_converted_to_braces() -> None:
    lib = parseString('@misc{k, title = "Quoted", year = 2020}')
    out = toString(lib)
    assert 'title = {Quoted}' in out
    assert '"' not in out


def test_layout_shape() -> None:
    lib = Library([Entry("article", "k", {"title": "T", "year": "2020"})])
    assert toString(lib) == (
        "@article{k,\n"
        "  title = {T},\n"
        "  year = {2020},\n"
        "}\n"
    )


def test_blank_line_between_entries() -> None:
    lib = Library([Entry("misc", "a", {"year": "1"}), Entry("misc", "b", {"year": "2"})])
    assert "}\n\n@misc{b," in toString(lib)


def test_empty_library() -> None:
    assert toString(Library()) == ""
