"""Library merging: concatenation, key collisions, and overlap detection."""

from __future__ import annotations

from bibtidy import Entry, Library, MergeResult, Overlap, merge, flagOverlaps


class TestMerge:
    def test_concatenation(self) -> None:
        lib1 = Library([Entry("article", "a", {}), Entry("article", "b", {})])
        lib2 = Library([Entry("book", "c", {})])
        result = merge([lib1, lib2])
        assert len(result.library) == 3

    def test_key_collisions_detected(self) -> None:
        lib1 = Library([Entry("article", "dup", {})])
        lib2 = Library([Entry("article", "dup", {})])
        result = merge([lib1, lib2])
        assert result.keyCollisions == ["dup"]

    def test_no_collisions(self) -> None:
        lib1 = Library([Entry("article", "a", {})])
        lib2 = Library([Entry("article", "b", {})])
        result = merge([lib1, lib2])
        assert result.keyCollisions == []


class TestFlagOverlaps:
    def test_exact_doi_match(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"doi": "10.1234/test"}),
                Entry("article", "b", {"doi": "10.1234/test"}),
            ]
        )
        overlaps = flagOverlaps(lib)
        doi_overlaps = [o for o in overlaps if o.reason == "doi"]
        assert len(doi_overlaps) == 1
        assert doi_overlaps[0].value == "10.1234/test"
        assert doi_overlaps[0].keys == ("a", "b")

    def test_exact_title_match(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"title": "Deep Learning"}),
                Entry("article", "b", {"title": "deep learning"}),
            ]
        )
        overlaps = flagOverlaps(lib)
        title_overlaps = [o for o in overlaps if o.reason == "title"]
        assert len(title_overlaps) == 1

    def test_distinct_entries_no_overlaps(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"title": "Title A", "doi": "10.000/A"}),
                Entry("article", "b", {"title": "Title B", "doi": "10.000/B"}),
            ]
        )
        overlaps = flagOverlaps(lib)
        assert overlaps == []

    def test_overlap_case_insensitive_doi(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"doi": "10.1234/TEST"}),
                Entry("article", "b", {"doi": "10.1234/test"}),
            ]
        )
        overlaps = flagOverlaps(lib)
        assert len(overlaps) == 1


class TestMergeResult:
    def test_result_type(self) -> None:
        result = merge([Library()])
        assert isinstance(result, MergeResult)
        assert isinstance(result.keyCollisions, list)
        assert isinstance(result.likelyDuplicates, list)

    def test_overlap_is_frozen_dataclass(self) -> None:
        overlap = Overlap(reason="doi", value="10.1234/test", keys=("a", "b"))
        assert overlap.reason == "doi"
        assert overlap.value == "10.1234/test"
        assert overlap.keys == ("a", "b")