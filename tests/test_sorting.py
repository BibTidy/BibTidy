"""Entry sorting and library mutation."""

from __future__ import annotations

from pathlib import Path

from bibtidy import Entry, Library, sortedEntries, sortLibrary, writeFile


class TestSortedEntries:
    def test_sort_by_year(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"year": "2020"}),
                Entry("article", "b", {"year": "2019"}),
                Entry("article", "c", {"year": "2021"}),
            ]
        )
        result = sortedEntries(lib, sortBy=("year",))
        assert [e.key for e in result] == ["b", "a", "c"]

    def test_sort_by_author(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"author": "Zebra"}),
                Entry("article", "b", {"author": "Alpha"}),
                Entry("article", "c", {"author": "Beta"}),
            ]
        )
        result = sortedEntries(lib, sortBy=("author",))
        assert [e.key for e in result] == ["b", "c", "a"]

    def test_sort_by_type(self) -> None:
        lib = Library(
            [
                Entry("misc", "a", {}),
                Entry("article", "b", {}),
                Entry("book", "c", {}),
            ]
        )
        result = sortedEntries(lib, sortBy=("type",))
        assert [e.key for e in result] == ["b", "c", "a"]

    def test_sort_by_key(self) -> None:
        lib = Library(
            [
                Entry("article", "c", {}),
                Entry("article", "a", {}),
                Entry("article", "b", {}),
            ]
        )
        result = sortedEntries(lib, sortBy=("key",))
        assert [e.key for e in result] == ["a", "b", "c"]

    def test_multi_key_tiebreak(self) -> None:
        lib = Library(
            [
                Entry("article", "b", {"year": "2020", "author": "Zebra"}),
                Entry("article", "a", {"year": "2020", "author": "Alpha"}),
                Entry("article", "c", {"year": "2019"}),
            ]
        )
        result = sortedEntries(lib, sortBy=("year", "author"))
        assert [e.key for e in result] == ["c", "a", "b"]

    def test_reverse(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"year": "2020"}),
                Entry("article", "b", {"year": "2021"}),
            ]
        )
        result = sortedEntries(lib, sortBy=("year",), reverse=True)
        assert [e.key for e in result] == ["b", "a"]

    def test_missing_field_sort_consistently(self) -> None:
        lib = Library(
            [
                Entry("article", "b", {"year": "2020"}),
                Entry("article", "a", {}),
            ]
        )
        result = sortedEntries(lib, sortBy=("year",))
        assert [e.key for e in result] == ["a", "b"]


class TestSortLibrary:
    def test_mutates_in_place(self) -> None:
        lib = Library([Entry("article", "c", {}), Entry("article", "a", {})])
        result = sortLibrary(lib, sortBy=("key",))
        assert lib.entries[0].key == "a"
        assert result is lib


class TestWriterOrderParameter:
    def test_persist_sort_via_order(self, tmp_path: Path) -> None:
        lib = Library(
            [
                Entry("article", "c", {"year": "2020"}),
                Entry("article", "a", {"year": "2020"}),
                Entry("article", "b", {"year": "2019"}),
            ]
        )
        path = tmp_path / "lib.bib"
        sortLibrary(lib, sortBy=("year", "key"))
        writeFile(lib, path, order=lib.entries)
        written = path.read_text()
        keys = [ln.split("{")[1].split(",")[0] for ln in written.splitlines() if ln.startswith("@")]
        assert keys == ["b", "a", "c"]

    def test_default_write_returns_to_key_order(self, tmp_path: Path) -> None:
        lib = Library(
            [
                Entry("article", "c", {}),
                Entry("article", "a", {}),
                Entry("article", "b", {}),
            ]
        )
        path = tmp_path / "lib.bib"
        sortLibrary(lib, sortBy=("year",))
        writeFile(lib, path, order=lib.entries)
        writeFile(lib, path)
        content = path.read_text()
        lines = content.splitlines()
        entry_keys = []
        for ln in lines:
            if ln.startswith("@"):
                entry_keys.append(ln.split("{")[1].split(",")[0])
        assert entry_keys == ["a", "b", "c"]