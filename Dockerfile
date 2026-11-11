# Auditra: satu image berisi API (FastAPI + DuckDB) dan UI (React, disajikan oleh API).
#   docker build -t auditra .  &&  docker run -p 8000:8000 -v auditra_data:/data auditra
# CATATAN: Dockerfile ini belum diuji dengan `docker build` (daemon Docker tidak tersedia saat dibuat);
# langkah-langkahnya sudah diuji terpisah (npm ci/build, pip install, uvicorn mode parquet).

# ── tahap 1: build frontend ─────────────────────────────────────────────────
FROM node:22-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
ENV VITE_API_URL=/api
RUN npm run build

# ── tahap 2: runtime Python ─────────────────────────────────────────────────
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements-web.txt

COPY api/ api/
COPY scraper/ scraper/
COPY geo/kabkota_clean.geojson geo/geo_lookup.csv geo/
COPY output/chunks/ output/chunks/
COPY output/kg_nodes.csv output/kg_edges.csv output/
COPY --from=web /web/dist web/dist

# Parquet dibaca langsung (tanpa membangun cache DuckDB): siap seketika, ±650 MB RAM.
# Data transaksional (SQLite + unggahan bukti) disimpan di volume /data agar tidak hilang saat redeploy.
ENV AUDITRA_USE_PARQUET_VIEWS=1 \
    AUDITRA_APP_DB=/data/auditra_app.sqlite \
    AUDITRA_UPLOAD_DIR=/data/uploads \
    PORT=8000
VOLUME ["/data"]
EXPOSE 8000

# Bukan root
# hanya /data yang perlu dapat ditulis; menghindari chown -R /app (akan menggandakan 215 MB data di layer)
RUN useradd --system --create-home --uid 10001 auditra && mkdir -p /data && chown auditra /data
USER auditra

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import os,urllib.request as u; u.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8000\")}/api/health', timeout=4)"

CMD ["sh", "-c", "exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
