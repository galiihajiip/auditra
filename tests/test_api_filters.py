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


def test_dashboard_bundle_preserves_503(monkeypatch):
    from fastapi import HTTPException
    from fastapi.testclient import TestClient

    from api.main import app
    from api.routers import dashboard

    def not_ready():
        raise HTTPException(status_code=503, detail="warming")

    monkeypatch.setattr(dashboard, "require_store", not_ready)
    r = TestClient(app).get("/api/dashboard/bundle")
    assert r.status_code == 503  # was 500 → frontend warm-up retry never fired


@pytest.mark.parametrize("qs", ["page=0", "page_size=501", "risk_min=abc"])
def test_packages_rejects_bad_params(qs):
    from fastapi.testclient import TestClient

    from api.main import app

    assert TestClient(app).get(f"/api/packages?{qs}").status_code == 422


class _FakeStore:
    def fetch_packages_page(self, provinsi, lembaga, metode, risk_min, page, page_size, q="", sort="rpi", direction="desc"):
        self.last = (q, sort, direction, page_size)
        rows = [{"id": 1, "RPI": 79.5, "risk_label": "KRITIS", "paket": 'Paket "A", lengkap', "lembaga": "Lembaga X", "metode": "Penunjukan Langsung", "pagu": 15375000000.0, "lokasi": "DKI Jakarta"}]
        return {"data": rows, "total": 1, "page": page, "page_size": page_size, "total_pages": 1}


def test_export_csv_contract(monkeypatch):
    from fastapi.testclient import TestClient

    from api.main import app
    from api.routers import packages

    store = _FakeStore()
    monkeypatch.setattr(packages, "require_store", lambda: store)
    r = TestClient(app).get("/api/packages/export.csv?q=Binsat&sort=pagu&direction=asc")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    assert store.last == ("Binsat", "pagu", "asc", 5000)
    body = r.content.decode("utf-8-sig").splitlines()
    assert body[0] == "id_sirup,rpi,kategori,paket,lembaga,metode,pagu_rp,lokasi"
    assert '"Paket ""A"", lengkap"' in body[1]  # koma dan kutip di-escape


@pytest.mark.parametrize("qs", ["sort=hack", "direction=up", "q=" + "x" * 101])
def test_packages_rejects_bad_search_params(qs):
    from fastapi.testclient import TestClient

    from api.main import app

    assert TestClient(app).get(f"/api/packages?{qs}").status_code == 422


def test_search_and_sort_on_real_data():
    """Bila dataset ada: kata kunci menyaring, ID SIRUP persis cocok, dan urutan pagu bekerja."""
    from api.deps import require_store

    try:
        store = require_store()
    except Exception:
        pytest.skip("dataset tidak tersedia")
    base = store.fetch_packages_page("ALL", "ALL", "ALL", 0, 1, 20)
    assert base["total"] > 0
    first = base["data"][0]
    by_id = store.fetch_packages_page("ALL", "ALL", "ALL", 0, 1, 20, q=str(first["id"]))
    assert any(r["id"] == first["id"] for r in by_id["data"])
    word = str(first["paket"]).split()[0]
    by_name = store.fetch_packages_page("ALL", "ALL", "ALL", 0, 1, 20, q=word)
    assert 0 < by_name["total"] <= base["total"]
    asc = store.fetch_packages_page("ALL", "ALL", "ALL", 0, 1, 20, sort="pagu", direction="asc")["data"]
    assert [r["pagu"] for r in asc] == sorted(r["pagu"] for r in asc)
    inj = store.fetch_packages_page("ALL", "ALL", "ALL", 0, 1, 20, q="x' OR 1=1 --")
    assert inj["total"] == 0


def test_clean_text_decodes_double_escaped_sirup_titles():
    from api.db import clean_text

    assert clean_text("Bimtek Konseling &amp;#40;BK&amp;#41;") == "Bimtek Konseling (BK)"
    assert clean_text("Dinas A & B") == "Dinas A & B"  # & polos tidak diubah
    assert clean_text(None) is None and clean_text(5) == 5


def test_json_safe_replaces_nan_and_inf():
    from api.db import _json_safe

    assert _json_safe({"a": float("nan"), "b": [float("inf"), 1.5]}) == {"a": None, "b": [None, 1.5]}


def test_dashboard_bundle_with_lembaga_filter_is_valid_json():
    """Regresi: filter lembaga pernah 500 karena NaN pada simpul Knowledge Graph."""
    import json

    from api.deps import require_store

    try:
        store = require_store()
    except Exception:
        pytest.skip("dataset tidak tersedia")
    bundle = store.fetch_dashboard_bundle(lembaga="Kementerian Pertahanan")
    json.dumps(bundle, allow_nan=False)
    assert bundle["overview"]["total_paket"] > 0
