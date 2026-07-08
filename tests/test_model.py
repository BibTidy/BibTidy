"""Data model behaviour."""

from __future__ import annotations

from bibtidy import Entry, Library


def test_entry_equality_and_repr() -> None:
    a = Entry("Article", "k", {"Title": "T"})
    b = Entry("article", "k", {"title": "T"})
    assert a == b
    assert a != Entry("article", "k", {"title": "U"})
    assert a != "not an entry"
    assert "k" in repr(a)


def test_entry_get_default() -> None:
    entry = Entry("misc", "k")
    assert entry.get("missing") is None
    assert entry.get("missing", "fallback") == "fallback"


def test_library_get_and_len_and_iter() -> None:
    lib = Library([Entry("misc", "a"), Entry("misc", "b")])
    assert len(lib) == 2
    assert [e.key for e in lib] == ["a", "b"]
    assert lib.require("a").key == "a"
    assert lib.get("missing") is None
    assert "2 entries" in repr(lib)


def test_duplicate_keys() -> None:
    lib = Library([Entry("misc", "a"), Entry("misc", "a"), Entry("misc", "b")])
    assert lib.duplicateKeys() == ["a"]
    assert Library([Entry("misc", "x")]).duplicateKeys() == []
