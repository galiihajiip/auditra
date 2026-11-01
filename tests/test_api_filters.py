"""Tests for SQL filter builder and API contract (no dataset required)."""

import pytest

from api.filters import build_where, resolve_provinsi


def test_no_filters_is_noop():
    assert build_where() == ("1=1", [])


def test_values_are_bound_not_interpolated():
    where, params = build_where(lembaga="x' OR 1=1 --", metode="Tender", risk_min=30)
    assert "OR 1=1" not in where
    assert params == ["x' OR 1=1 --", "Tender", 30.0]


def test_provinsi_alias_resolved():
    assert resolve_provinsi("di yogyakarta") == "DAERAH ISTIMEWA YOGYAKARTA"
    assert resolve_provinsi("  JAWA BARAT ") == "JAWA BARAT"


def test_packages_geo_uses_prov_column():
    where, params = build_where(provinsi="PAPUA", packages_geo=True)
    assert "prov_name" in where and params == ["PAPUA"]


