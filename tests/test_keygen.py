"""Citation key generation: [auth][year] with disambiguation."""

from __future__ import annotations

from bibtidy import Entry, Library, assignKeys, baseKey


class TestBaseKey:

    def test_last_comma_first(self) -> None:
        e = Entry("article", "x", {
            "author": "Smith, John and Doe, Jane",
            "year": "2024"
        })
        assert baseKey(e) == "Smith2024"

    def test_first_last(self) -> None:
        e = Entry("article", "x", {
            "author": "John Smith",
            "year": "2024"
        })
        assert baseKey(e) == "Smith2024"

    def test_editor_fallback(self) -> None:
        e = Entry("article", "x", {
            "editor": "Smith, John",
            "year": "2024"
        })
        assert baseKey(e) == "Smith2024"

    def test_year_from_date(self) -> None:
        e = Entry("article", "x", {
            "date": "2023-03-15",
            "author": "Smith, John"
        })
        assert baseKey(e) == "Smith2023"

    def test_year_from_year_field(self) -> None:
        e = Entry("article", "x", {
            "year": "2022",
            "author": "Smith, John"
        })
        assert baseKey(e) == "Smith2022"

    def test_latex_stripping(self) -> None:
        e = Entry("article", "x", {
            "author": r"{\'E}vry",
            "year": "2024"
        })
        assert baseKey(e) == "Evry2024"

    def test_braces_stripped(self) -> None:
        e = Entry("article", "x", {
            "author": "{Smith}, John",
            "year": "2024"
        })
        assert baseKey(e) == "Smith2024"

    def test_empty_author_empty_year(self) -> None:
        e = Entry("article", "x", {})
        assert baseKey(e) == "unknown"

    def test_author_first_letter_uppercase(self) -> None:
        e = Entry("article", "x", {
            "author": "john smith",
            "year": "2024"
        })
        assert baseKey(e) == "Smith2024"


class TestAssignKeys:

    def test_disambiguation_a_b_c(self) -> None:
        lib = Library()
        for _ in range(28):
            lib.add(Entry("article", "", {
                "author": "Smith, J",
                "year": "2024"
            }))
        assignKeys(lib)
        keys = [e.key for e in lib]
        assert keys[0] == "Smith2024"
        assert keys[1] == "Smith2024a"
        assert keys[25] == "Smith2024y"
        assert keys[26] == "Smith2024z"
        assert keys[27] == "Smith2024aa"

    def test_overwrite_true_by_default(self) -> None:
        lib = Library([Entry("article", "old", {
            "author": "Smith, John",
            "year": "2024"
        })])
        assignKeys(lib)
        assert lib.entries[0].key == "Smith2024"

    def test_overwrite_false_keeps_existing(self) -> None:
        lib = Library([Entry("article", "my-key", {
            "author": "Smith, John",
            "year": "2024"
        })])
        mapping = assignKeys(lib, overwrite=False)
        assert lib.entries[0].key == "my-key"
        assert mapping == {}

    def test_reserved_prevents_collision(self) -> None:
        lib = Library([Entry("article", "a", {
            "author": "Smith, John",
            "year": "2024"
        })])
        assignKeys(
            lib, reserved={"Smith2024"}
        )
        assert lib.entries[0].key == "Smith2024a"

    def test_returns_mapping(self) -> None:
        lib = Library([Entry("article", "old", {
            "author": "Smith, John",
            "year": "2024"
        })])
        mapping = assignKeys(lib)
        assert mapping == {
            "old": "Smith2024"
        }

    def test_unchanged_key_not_in_mapping(self) -> None:
        lib = Library([Entry("article", "Smith2024", {
            "author": "Smith, John",
            "year": "2024"
        })])
        mapping = assignKeys(lib)
        assert mapping == {}
