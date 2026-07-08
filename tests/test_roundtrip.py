"""Idempotency: the M0 exit criterion.

``write`` must be a fixed point of ``parse``: writing, re-parsing and re-writing
yields byte-identical output. This is the strongest correctness signal for the
parser/writer pair.
"""

from __future__ import annotations

from bibtidy import parseFile, parseString, toString


def _canonical(text: str) -> str:
    return toString(parseString(text))


def test_write_is_idempotent_on_fixtures(fixture_bib) -> None:
    first = toString(parseFile(fixture_bib))
    second = toString(parseString(first))
    assert first == second


def test_roundtrip_preserves_entries(fixture_bib) -> None:
    lib1 = parseFile(fixture_bib)
    lib2 = parseString(toString(lib1))
    assert sorted(lib1.keys()) == sorted(lib2.keys())
    for entry in lib1:
        twin = lib2.get(entry.key)
        assert twin is not None
        assert twin.entryType == entry.entryType
        assert twin.fields == entry.fields


def test_second_write_zero_diff_raw_string() -> None:
    source = """
    @article{Beta,
       author = {Doe, John and Roe, Jane},
       title  = {Something {Important}},
       journal= {J. Testing},
       year   = 2021,
       pages  = {1--10},
    }
    @book{Alpha, title={Book}, publisher={P}, author={A}, year={1999}}
    """
    once = _canonical(source)
    twice = _canonical(once)
    assert once == twice
    # And entry order is key-sorted, not source order.
    assert once.index("Alpha") < once.index("Beta")
