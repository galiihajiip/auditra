from fastapi import APIRouter, HTTPException, Query

from api.deps import require_store
from api.filters import build_where
from api.schemas import OverviewStats

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview", response_model=OverviewStats)
def overview(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
):
    try:
        store = require_store()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    where, params = build_where(
        provinsi=provinsi, lembaga=lembaga, metode=metode, risk_min=risk_min
    )
    row = store.fetch_one(
