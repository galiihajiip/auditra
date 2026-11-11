import threading
import time
from collections import deque

from fastapi import APIRouter, HTTPException

from api.deps import require_store
from api.freshness import build, live_status

router = APIRouter(prefix="/api", tags=["freshness"])

_live_calls: deque = deque()
_live_cache: dict[int, tuple[float, dict]] = {}
_lock = threading.Lock()
MAX_LIVE_PER_MIN = 20  # lindungi situs sumber dari beban berlebih


@router.get("/freshness")
def freshness(refresh: bool = False):
    store = require_store()
    if refresh:
        live_status(force=True)
    return build(store.meta()["total_rows"])


@router.get("/packages/{package_id}/live")
def package_live(package_id: int):
    """Bandingkan satu paket di snapshot dengan halaman detail SIRUP saat ini."""
    from scraper.detail import fetch_detail

    store = require_store()
    snap = store.fetch_package(package_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Paket tidak ada di snapshot.")

    now = time.time()
    with _lock:
        hit = _live_cache.get(package_id)
        if hit and now - hit[0] < 300:
            return hit[1]
        while _live_calls and _live_calls[0] < now - 60:
            _live_calls.popleft()
        if len(_live_calls) >= MAX_LIVE_PER_MIN:
            raise HTTPException(status_code=429, detail="Terlalu banyak pengecekan langsung; coba lagi sebentar.")
        _live_calls.append(now)

    try:
        live = fetch_detail(package_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"SIRUP tidak dapat dihubungi atau paket sudah tidak ada ({type(exc).__name__}).") from exc

    diffs = []
    for field, label in (("pagu", "Pagu"), ("metode", "Metode"), ("paket", "Nama paket")):
        a, b = snap.get(field), live.get(field)
        same = (float(a) == float(b)) if field == "pagu" and a is not None and b is not None else (a == b)
        if not same:
            diffs.append({"field": field, "label": label, "snapshot": a, "live": b})
    result = {
        "package_id": package_id,
        "checked_at": now,
        "in_sync": not diffs,
        "differences": diffs,
        "live": {k: live.get(k) for k in ("uraianPekerjaan", "volumePekerjaan", "spesifikasiPekerjaan", "pagu", "metode")},
    }
    with _lock:
        _live_cache[package_id] = (now, result)
    return result
