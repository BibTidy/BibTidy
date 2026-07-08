"""Parser behaviour, including the field-inside-value robustness case."""

from __future__ import annotations

from bibtidy import parseString


def test_basic_entry() -> None:
    lib = parseString("@article{key, author = {Doe, J.}, year = {2020}}")
    assert len(lib) == 1
    entry = lib.require("key")
    assert entry.entryType == "article"
    assert entry.get("author") == "Doe, J."
    assert entry.get("year") == "2020"


def test_type_and_field_names_lowercased() -> None:
    lib = parseString("@ARTICLE{k, Author = {X}, TITLE = {Y}}")
    entry = lib.require("k")
    assert entry.entryType == "article"
    assert entry.get("author") == "X"
    assert entry.get("title") == "Y"


def test_nested_braces_preserved() -> None:
    lib = parseString("@article{k, title = {Lazart: {A} Symbolic {Approach}}}")
    assert lib.require("k").get("title") == "Lazart: {A} Symbolic {Approach}"


def test_quoted_value_with_inner_brace() -> None:
    lib = parseString('@misc{k, title = "A { brace } inside", year = 2022}')
    entry = lib.require("k")
    assert entry.get("title") == "A { brace } inside"
    assert entry.get("year") == "2022"


def test_bare_numeric_value() -> None:
    lib = parseString("@misc{k, year = 2023, volume = 12}")
    entry = lib.require("k")
    assert entry.get("year") == "2023"
    assert entry.get("volume") == "12"


def test_field_pattern_inside_value_is_not_a_field() -> None:
    # The critical robustness case the hand-rolled scanner exists for: a value
    # that itself contains `word = {...}` must stay a single field value.
    lib = parseString(
        "@article{k, note = {see url = {https://x/y=1} here}, year = {2020}}"
    )
    entry = lib.require("k")
    assert entry.get("note") == "see url = {https://x/y=1} here"
    assert entry.get("year") == "2020"
    assert "url" not in entry.fields


def test_at_sign_inside_value_does_not_start_entry() -> None:
    lib = parseString("@misc{k, author = {a@b.com and c@d.com}, year = {2020}}")
    assert len(lib) == 1
    assert lib.require("k").get("author") == "a@b.com and c@d.com"


def test_whitespace_collapsed() -> None:
    lib = parseString("@misc{k, title = {Multi\n     line\n   title}}")
    assert lib.require("k").get("title") == "Multi line title"


def test_escaped_brace_does_not_unbalance() -> None:
    lib = parseString(r"@misc{k, title = {a \{ b \} c}, year = {2020}}")
    entry = lib.require("k")
    assert entry.get("title") == r"a \{ b \} c"
    assert entry.get("year") == "2020"


def test_skipped_blocks_ignored() -> None:
    text = (
        "@string{ p = {ACM} }\n"
        "@comment{ ignore me }\n"
        "@preamble{ {\\newcommand{\\x}{y}} }\n"
        "@article{real, author = {A}, title = {T}, journal = {J}, year = {2020}}\n"
    )
    lib = parseString(text)
    assert lib.keys() == ["real"]


def test_fieldless_entry() -> None:
    lib = parseString("@book{onlykey}")
    assert lib.keys() == ["onlykey"]
    assert lib.require("onlykey").fields == {}


def test_junk_between_entries_ignored() -> None:
    text = "blah blah\n@misc{a, year={1}}\nrandom noise\n@misc{b, year={2}}"
    lib = parseString(text)
    assert lib.keys() == ["a", "b"]


def test_stray_at_sign() -> None:
    lib = parseString("email me @ home @misc{k, year={2020}}")
    assert lib.keys() == ["k"]


def test_empty_input() -> None:
    assert len(parseString("")) == 0
    assert len(parseString("   \n\n  ")) == 0


def test_unterminated_braced_value() -> None:
    # Missing closing brace: capture what we can rather than crash.
    lib = parseString("@misc{k, title = {never closed")
    assert lib.keys() == ["k"]
    assert lib.require("k").get("title") == "never closed"


def test_unterminated_quoted_value() -> None:
    lib = parseString('@misc{k, title = "never closed')
    assert lib.require("k").get("title") == "never closed"


def test_field_without_equals_stops_entry() -> None:
    # A malformed trailing token with no '=' just ends the entry cleanly.
    lib = parseString("@misc{k, year = {2020}, garbage }")
    entry = lib.require("k")
    assert entry.get("year") == "2020"
    assert "garbage" not in entry.fields


def test_empty_braced_value() -> None:
    lib = parseString("@misc{k, note = {}, year = {2020}}")
    assert lib.require("k").get("note") == ""


def test_at_with_no_type() -> None:
    lib = parseString("@ {not a type} @misc{k, year={1}}")
    assert lib.keys() == ["k"]


def test_type_with_no_brace() -> None:
    lib = parseString("@article no brace here @misc{k, year={1}}")
    assert lib.keys() == ["k"]


def test_fixtures_parse(fixture_bib) -> None:
    from bibtidy import parseFile

    lib = parseFile(fixture_bib)
    assert len(lib) >= 1
