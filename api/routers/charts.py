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


