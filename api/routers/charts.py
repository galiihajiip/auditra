from fastapi import APIRouter, HTTPException, Query

from api.deps import require_store
from api.db import DataStore
from api.filters import build_where

router = APIRouter(prefix="/api", tags=["charts"])


def _require_store() -> DataStore:
    return require_store()


@router.get("/charts/risk-distribution")
def risk_distribution(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
):
    store = _require_store()
    where, params = build_where(
        provinsi=provinsi, lembaga=lembaga, metode=metode, risk_min=risk_min
    )
    df = store.fetch_df(
        f"""
        SELECT risk_label, COUNT(*) AS count
        FROM packages
        WHERE {where}
        GROUP BY risk_label
        """,
        params,
    )
    return df.to_dict(orient="records")


@router.get("/charts/metode")
def metode_bar(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
):
    store = _require_store()
    where, params = build_where(
        provinsi=provinsi, lembaga=lembaga, metode=metode, risk_min=risk_min
    )
    df = store.fetch_df(
        f"""
        SELECT metode, COUNT(*) AS jumlah, AVG(RPI) AS avg_rpi
        FROM packages
        WHERE {where}
        GROUP BY metode
        ORDER BY avg_rpi DESC
        """,
        params,
    )
    df["avg_rpi"] = df["avg_rpi"].round(2)
    return df.to_dict(orient="records")


@router.get("/charts/scatter")
def scatter(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
    limit: int = Query(3000, ge=100, le=10000),
):
    """Random sample for visualization — COUNT/stats still use full filtered set."""
    store = _require_store()
    where, params = build_where(
        provinsi=provinsi, lembaga=lembaga, metode=metode, risk_min=risk_min
    )
    df = store.fetch_df(
        f"""
        SELECT RPI, risk_label, pagu / 1e9 AS pagu_miliar, paket, lembaga, metode
        FROM packages
        WHERE {where}
        ORDER BY random()
        LIMIT ?
        """,
        params + [limit],
    )
    return {
        "points": df.to_dict(orient="records"),
        "note": f"Visual sample max {limit} points; aggregates use all matching rows.",
    }


