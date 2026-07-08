"""Metadata query search: field:value terms, aliases, bare terms."""

from __future__ import annotations

from bibtidy import Entry, Library, matches, parseQuery, search


class TestParseQuery:
    def test_single_field_value(self) -> None:
        terms = parseQuery("author:smith")
        assert len(terms) == 1
        assert terms[0].field == "author"
        assert terms[0].value == "smith"

    def test_multiple_anded_terms(self) -> None:
        terms = parseQuery("author:smith year:2020")
        assert len(terms) == 2
        assert terms[1].value == "2020"

    def test_quoted_value_with_space(self) -> None:
        terms = parseQuery('title:"deep learning"')
        assert len(terms) == 1
        assert terms[0].value == "deep learning"

    def test_bare_term(self) -> None:
        terms = parseQuery("smith")
        assert terms[0].field is None
        assert terms[0].value == "smith"

    def test_tag_alias(self) -> None:
        terms = parseQuery("tag:reading-list")
        assert terms[0].field == "bibtidytags"

    def test_group_alias(self) -> None:
        terms = parseQuery("group:my-group")
        assert terms[0].field == "bibtidygroups"

    def test_collection_alias(self) -> None:
        terms = parseQuery("collection:my-col")
        assert terms[0].field == "bibtidygroups"

    def test_type_alias(self) -> None:
        terms = parseQuery("type:article")
        assert terms[0].field == "@type"

    def test_key_alias(self) -> None:
        terms = parseQuery("key:mykey")
        assert terms[0].field == "@key"


class TestMatches:
    def test_author_match(self) -> None:
        e = Entry("article", "x", {"author": "John Smith"})
        terms = parseQuery("author:smith")
        assert matches(e, terms)

    def test_year_match(self) -> None:
        e = Entry("article", "x", {"year": "2020"})
        terms = parseQuery("year:2020")
        assert matches(e, terms)

    def test_anded_terms_both_match(self) -> None:
        e = Entry("article", "x", {"author": "John Smith", "year": "2020"})
        terms = parseQuery("author:smith year:2020")
        assert matches(e, terms)

    def test_anded_terms_one_fails(self) -> None:
        e = Entry("article", "x", {"author": "John Smith", "year": "2019"})
        terms = parseQuery("author:smith year:2020")
        assert not matches(e, terms)

    def test_case_insensitive(self) -> None:
        e = Entry("article", "x", {"author": "JOHN SMITH"})
        terms = parseQuery("author:smith")
        assert matches(e, terms)

    def test_bare_term_matches_across_fields(self) -> None:
        e = Entry("article", "smith2020", {"author": "John Smith", "year": "2020"})
        terms = parseQuery("smith")
        assert matches(e, terms)

    def test_bare_term_matches_key(self) -> None:
        e = Entry("article", "my-key-xyz", {})
        terms = parseQuery("xyz")
        assert matches(e, terms)

    def test_tag_alias_match(self) -> None:
        e = Entry("article", "x", {"bibtidytags": "reading-list"})
        terms = parseQuery("tag:reading")
        assert matches(e, terms)

    def test_no_match(self) -> None:
        e = Entry("article", "x", {"author": "John Smith"})
        terms = parseQuery("year:2020")
        assert not matches(e, terms)


class TestSearch:
    def test_search_returns_list(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"author": "John Smith"}),
                Entry("article", "b", {"author": "Jane Doe"}),
            ]
        )
        results = search(lib, "author:smith")
        assert len(results) == 1
        assert results[0].key == "a"

    def test_search_multiple_matches(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"year": "2020"}),
                Entry("article", "b", {"year": "2020"}),
                Entry("article", "c", {"year": "2019"}),
            ]
        )
        results = search(lib, "year:2020")
        assert len(results) == 2

    def test_search_empty_result(self) -> None:
        lib = Library([Entry("article", "a", {"author": "John Smith"})])
        results = search(lib, "author:nonexistent")
        assert results == []

    def test_search_anded_terms(self) -> None:
        lib = Library(
            [
                Entry("article", "a", {"author": "Smith", "year": "2020"}),
                Entry("article", "b", {"author": "Smith", "year": "2019"}),
            ]
        )
        results = search(lib, "author:smith year:2020")
        assert len(results) == 1
        assert results[0].key == "a"