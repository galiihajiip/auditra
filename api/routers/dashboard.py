import logging

from fastapi import APIRouter, HTTPException, Query

from api.deps import require_store

log = logging.getLogger("auditra.dashboard")
router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard/bundle")
def dashboard_bundle(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
):
    """
    Single request for all chart data — one DuckDB session, cached per filter combo.
    Replaces 9 separate API calls from the frontend.
    """
    try:
        store = require_store()
        return store.fetch_dashboard_bundle(provinsi, lembaga, metode, risk_min)
    except HTTPException:
        # mis. 503 "database sedang disiapkan" dari require_store — jangan diubah jadi 500
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        log.exception("dashboard bundle failed")
        raise HTTPException(status_code=500, detail="Gagal menghitung dashboard.") from exc
