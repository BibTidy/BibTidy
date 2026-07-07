"""Idempotency: the M0 exit criterion.

``write`` must be a fixed point of ``parse``: writing, re-parsing and re-writing
yields byte-identical output. This is the strongest correctness signal for the
parser/writer pair.
"""

from __future__ import annotations

from bibtidy import parse_file, parse_string, to_string


def _canonical(text: str) -> str:
    return to_string(parse_string(text))


def test_write_is_idempotent_on_fixtures(fixture_bib) -> None:
    first = to_string(parse_file(fixture_bib))
    second = to_string(parse_string(first))
    assert first == second


def test_roundtrip_preserves_entries(fixture_bib) -> None:
    lib1 = parse_file(fixture_bib)
    lib2 = parse_string(to_string(lib1))
    assert sorted(lib1.keys()) == sorted(lib2.keys())
    for entry in lib1:
        twin = lib2.get(entry.key)
        assert twin is not None
        assert twin.entry_type == entry.entry_type
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
