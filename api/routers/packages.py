from fastapi import APIRouter, HTTPException, Query

from api.deps import require_store
from api.schemas import PaginatedPackages

router = APIRouter(prefix="/api", tags=["packages"])


@router.get("/packages", response_model=PaginatedPackages)
def list_packages(
    provinsi: str = Query("ALL"),
    lembaga: str = Query("ALL"),
    metode: str = Query("ALL"),
    risk_min: float = Query(0),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    try:
        store = require_store()
        return store.fetch_packages_page(
            provinsi, lembaga, metode, risk_min, page, page_size
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


SIGNAL_META = [
    ("s1_metode", "Metode pemilihan", 0.20),
    ("s2_pagu_anomali", "Anomali pagu", 0.20),
    ("s3_fragmentasi", "Fragmentasi / split contract", 0.15),
    ("s4_konsentrasi", "Konsentrasi metode berisiko", 0.15),
    ("s5_umkm", "Anomali UMKM", 0.10),
    ("s6_dana_metode", "Sumber dana + metode", 0.10),
    ("s7_reputasi", "Reputasi lembaga (KG)", 0.10),
]


@router.get("/packages/{package_id}")
def get_package(package_id: int):
    """Passport paket: atribut, sinyal berbobot (kontribusi ke RPI), dan provenance data."""
    store = require_store()
    pkg = store.fetch_package(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan.")
    signals = []
    for key, label, weight in SIGNAL_META:
        v = float(pkg.get(key) or 0)
        signals.append(
            {"key": key, "label": label, "value": round(v, 4), "weight": weight,
             "contribution": round(v * weight * 100, 2)}
        )
    meta = store.meta()
    return {
        "package": pkg,
        "signals": signals,
        "provenance": {
            "source": "SIRUP LKPP — Rencana Umum Pengadaan",
            "source_url": "https://sirup.inaproc.id/sirup/caripaketctr/index",
            "sirup_id": pkg["id"],
            "dataset_rows": meta["total_rows"],
            "pipeline": [
                "01 cleaning", "02 scoring (7 sinyal)", "03 network/KG", "03b geo matching", "05 validate",
            ],
            "methodology_doc": "docs/METODOLOGI.md",
            "caveat": "RPI adalah skor prioritas audit, bukan temuan pelanggaran.",
        },
    }
