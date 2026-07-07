"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Directory holding the sample ``.bib`` files."""
    return FIXTURES


@pytest.fixture(params=sorted(FIXTURES.glob("*.bib")), ids=lambda p: p.name)
def fixture_bib(request: pytest.FixtureRequest) -> Path:
    """Parametrised over every ``.bib`` fixture file."""
    return request.param
