from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scraper.detail import parse_detail

FIX = Path(__file__).parent / "fixtures" / "sirup_detail_65871543.html"


def test_parse_detail_fixture():
    d = parse_detail(FIX.read_text())
    assert d["id"] == 65871543
    assert d["pagu"] == 9_800_000
    assert d["metode"] == "E-Purchasing"
    assert d["lembaga"] == "Kab. Banyuwangi"
    assert d["volumePekerjaan"].startswith("1")
    assert "Alat Pendingin" in d["uraianPekerjaan"]


def test_parse_detail_rejects_garbage():
    with pytest.raises(ValueError):
        parse_detail("<html><body>Halaman tidak ditemukan</body></html>")


def test_live_status_is_fail_soft_and_keeps_last_good(monkeypatch):
    from api import freshness

    freshness._cache.update(at=0.0, value=None)
    monkeypatch.setattr(freshness, "_live_total", lambda: {"total": 100, "checked_at": 1.0, "error": None})
    assert freshness.live_status(force=True)["total"] == 100
    monkeypatch.setattr(freshness, "_live_total", lambda: {"total": None, "checked_at": 2.0, "error": "down"})
    v = freshness.live_status(force=True)
    assert v["total"] == 100 and v["stale"] is True and v["error"] == "down"


def test_build_reports_gap(monkeypatch):
    from api import freshness

    monkeypatch.setattr(freshness, "live_status", lambda force=False: {"total": 1000, "checked_at": 1.0, "error": None})
    monkeypatch.setattr(freshness, "latest_delta", lambda: None)
    r = freshness.build(800)
    assert r["behind_rows"] == 200 and r["behind_pct"] == 20.0


def test_package_live_endpoint_diff_and_rate_limit(monkeypatch):
    from api.main import app
    from api.routers import freshness as fr

    class Store:
        def fetch_package(self, pid):
            return {"id": pid, "pagu": 100.0, "metode": "Tender", "paket": "A"} if pid != 9 else None

    monkeypatch.setattr(fr, "require_store", lambda: Store())
    monkeypatch.setattr("scraper.detail.fetch_detail",
                        lambda pid: {"id": pid, "pagu": 150, "metode": "Tender", "paket": "A", "uraianPekerjaan": "u"})
    fr._live_cache.clear(); fr._live_calls.clear()
    c = TestClient(app)
    r = c.get("/api/packages/1/live").json()
    assert r["in_sync"] is False and r["differences"][0]["field"] == "pagu"
    assert c.get("/api/packages/9/live").status_code == 404
    fr._live_cache.clear()
    codes = [c.get(f"/api/packages/{i}/live").status_code for i in range(100, 130)]
    assert 429 in codes
    fr._live_cache.clear(); fr._live_calls.clear()
