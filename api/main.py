import os
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.config import CORS_ORIGINS
from api.db import DataStore, _use_parquet_views
from api.routers import charts, dashboard, filters, geo, kg, meta, overview, packages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm DuckDB in background on Railway (parquet view mode); optional full warm-up."""
    warmup_enabled = os.getenv("AUDITRA_WARMUP_ON_STARTUP", "0").lower() in {
        "1",
        "true",
        "yes",
    }
    if warmup_enabled:
        store = DataStore.get()
        store.fetch_dashboard_bundle()
        print("[Auditra] Startup warm-up complete.")
    elif _use_parquet_views():
        DataStore.begin_background_init()
        print("[Auditra] Background database init started (parquet view mode).")
    else:
        print("[Auditra] Lazy init on first request.")
    yield


app = FastAPI(
    title="Auditra API",
    description=(
        "Backend dashboard Auditra. Data materialized in DuckDB untuk query cepat. "
        "Seluruh baris tetap utuh; API mengembalikan agregat/pagination."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(filters.router)
app.include_router(dashboard.router)
app.include_router(overview.router)
app.include_router(packages.router)
app.include_router(charts.router)
app.include_router(kg.router)
app.include_router(geo.router)


# ── Single-process demo mode ────────────────────────────────────────────────
# Jika frontend sudah di-build (web/dist, VITE_API_URL=/api), API ikut menyajikannya
# sehingga demo hanya butuh satu perintah: `uvicorn api.main:app` → http://127.0.0.1:8000
_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"
if _DIST.is_dir() and (_DIST / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
