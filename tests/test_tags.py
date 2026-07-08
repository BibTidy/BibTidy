"""Tags & collections: get/set/add/remove and group-by helpers."""

from __future__ import annotations

from bibtidy import (
    Entry,
    Library,
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


class TestTagOperations:
    def test_get_tags_empty(self) -> None:
        e = Entry("article", "x", {})
        assert getTags(e) == []

    def test_get_tags_parses_values(self) -> None:
        e = Entry("article", "x", {TAGS_FIELD: "  tag1 , tag2 ,  tag3  "})
        assert getTags(e) == ["tag1", "tag2", "tag3"]

    def test_set_tags_canonicalizes(self) -> None:
        e = Entry("article", "x", {})
        setTags(e, ["zebra", "alpha", "beta"])
        assert e.fields[TAGS_FIELD] == "alpha, beta, zebra"

    def test_set_tags_deduplicates(self) -> None:
        e = Entry("article", "x", {})
        setTags(e, ["a", "b", "a"])
        assert e.fields[TAGS_FIELD] == "a, b"

    def test_set_tags_empty_clears_field(self) -> None:
        e = Entry("article", "x", {TAGS_FIELD: "old"})
        setTags(e, [])
        assert TAGS_FIELD not in e.fields

    def test_add_tag(self) -> None:
        e = Entry("article", "x", {})
        addTag(e, "alpha")
        addTag(e, "beta")
        addTag(e, "alpha")
        assert getTags(e) == ["alpha", "beta"]

    def test_remove_tag(self) -> None:
        e = Entry("article", "x", {TAGS_FIELD: "alpha, beta, gamma"})
        removeTag(e, "beta")
        assert getTags(e) == ["alpha", "gamma"]


class TestGroupOperations:
    def test_get_groups_parses_values(self) -> None:
        e = Entry("article", "x", {GROUPS_FIELD: "collection-a, collection-b"})
        assert getGroups(e) == ["collection-a", "collection-b"]

    def test_set_groups_canonicalizes(self) -> None:
        e = Entry("article", "x", {})
        setGroups(e, ["z", "a"])
        assert e.fields[GROUPS_FIELD] == "a, z"

    def test_set_groups_empty_clears(self) -> None:
        e = Entry("article", "x", {GROUPS_FIELD: "x"})
        setGroups(e, [])
        assert GROUPS_FIELD not in e.fields

    def test_add_group(self) -> None:
        e = Entry("article", "x", {})
        addGroup(e, "col1")
        addGroup(e, "col2")
        assert getGroups(e) == ["col1", "col2"]

    def test_remove_group(self) -> None:
        e = Entry("article", "x", {GROUPS_FIELD: "c1, c2"})
        removeGroup(e, "c1")
        assert getGroups(e) == ["c2"]


class TestGroupBy:
    def test_group_by_tag(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {TAGS_FIELD: "foo, bar"}),
                Entry("article", "b", {TAGS_FIELD: "bar"}),
                Entry("article", "c", {TAGS_FIELD: "baz"}),
            ]
        )
        groups = groupByTag(lib)
        assert set(groups.keys()) == {"foo", "bar", "baz"}
        assert groups["bar"] == [lib.entries[0], lib.entries[1]]

    def test_group_by_collection(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {GROUPS_FIELD: "grp"}),
                Entry("article", "b", {GROUPS_FIELD: "grp"}),
                Entry("article", "c", {}),
            ]
        )
        groups = groupByCollection(lib)
        assert groups == {"grp": [lib.entries[0], lib.entries[1]]}

    def test_entry_with_no_tags_absent_from_groups(self) -> None:
        lib = Library([Entry("article", "a", {}), Entry("article", "b", {TAGS_FIELD: "x"})])
        groups = groupByTag(lib)
        assert "x" in groups
        assert len(groups.get("", [])) == 0