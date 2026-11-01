"""Tests for SQL filter builder and API contract (no dataset required)."""

import pytest

from api.filters import build_where, resolve_provinsi


def test_no_filters_is_noop():
    assert build_where() == ("1=1", [])


