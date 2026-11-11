# Deploy Auditra dengan Docker

Satu container berisi API **dan** UI (satu port, satu domain). Server yang cukup: Linux, **Docker + Docker Compose**, RAM ≥ 2 GB, disk ≥ 2 GB kosong.

## Langkah (±5 menit)
```bash
git clone https://github.com/galiihajiip/auditra.git && cd auditra     # pastikan versi terbaru sudah di-push!
cp .env.docker.example .env
sed -i "s/^AUDITRA_SECRET=.*/AUDITRA_SECRET=$(openssl rand -hex 32)/" .env
docker compose up -d --build        # build ±3–6 mnt (npm build + pip install)
curl localhost:8000/api/health      # {"status":"ok",...}
```
Buka `http://IP-SERVER:8000`. Pemuatan dasbor pertama ±6 detik (mode parquet, ±650 MB RAM), selanjutnya cepat.

## HTTPS + domain (disarankan untuk pitching)
Arahkan record A domain/subdomain ke IP server, lalu pasang Caddy (sertifikat otomatis):
```bash
sudo apt install -y caddy
echo 'auditra.domainanda.id { reverse_proxy localhost:8000 }' | sudo tee /etc/caddy/Caddyfile && sudo systemctl reload caddy
```

## Wajib sebelum publik
- `AUDITRA_SECRET` acak panjang (sudah dibuat di atas); **jangan** commit file `.env`.
- Akun demo (`auditor@auditra.demo`, `reviewer@auditra.demo`, kata sandi `auditra2026`) dibuat bila `AUDITRA_SEED_DEMO=1`. Itu untuk pitching; **siapa pun bisa login sebagai reviewer**. Setelah selesai: set `AUDITRA_SEED_DEMO=0`, hapus volume atau ganti kata sandi, buat reviewer asli dengan `docker compose exec auditra python -c "..."` (lihat `scripts/create_user.py`).
- Data penugasan dan unggahan bukti ada di volume `auditra_data` (cadangkan bila penting).

## Operasi
```bash
docker compose logs -f auditra       # log
docker compose up -d --build         # perbarui setelah git pull
docker compose down                  # berhenti (data tetap di volume)
```

## Checklist untuk yang men-deploy (jalankan berurutan)
1. `git pull` pastikan commit terbaru, lalu `cp .env.docker.example .env` dan isi `AUDITRA_SECRET` (acak panjang).
2. `docker compose up -d --build` (di server itu sendiri, jangan memindahkan image dari Mac ke Linux amd64).
3. `docker compose ps` harus `healthy`, dan `curl localhost:8000/api/health` mengembalikan `"database_ready":true`.
4. Buka `http://IP-SERVER:8000`. Dasbor pertama sekitar 6 detik (memuat Parquet), selanjutnya cepat. Satu port melayani **frontend dan backend sekaligus**.
5. Uji cepat: klik "Coba demo sekarang", buka satu paket, buka penugasan. Cek juga `/api/freshness` (butuh server dapat keluar ke sirup.inaproc.id).
6. Pitching: biarkan `AUDITRA_SEED_DEMO=1` agar akun demo satu klik ada. Setelah acara: set ke `0`.
7. Cadangan offline: jalankan hal yang sama di laptop (`docker compose up -d --build`) dan buka `http://localhost:8000`.

## Mode pengembangan (backend dan frontend langsung terlihat saat diubah)
```bash
# terminal 1: backend
pip install -r requirements-web.txt && AUDITRA_USE_PARQUET_VIEWS=1 uvicorn api.main:app --reload --port 8000
# terminal 2: frontend (proxy /api ke :8000, hot reload)
cd web && npm install && npm run dev        # http://localhost:5173
```

## Yang sudah diuji (11 Nov 2026, Docker 29.6.2, Mac Apple silicon / arm64)
- Terbaru: `docker compose -p auditra-qa up -d --build`, E2E browser **43/43** (siklus audit penuh, pencarian, urutan, unduh CSV, mobile tanpa overflow), 50 uji pytest lolos, restart menjaga data, memori ±330 MB saat idle.
- `docker compose up -d --build`: build ±2 menit, image 1,1 GB, container berjalan sebagai **user non-root**, memakai ±550 MB RAM.
- Dasbor pertama ±6 detik, login demo berhasil, UI + API melayani dari satu port.
- **Restart container mempertahankan data** (SQLite di volume `auditra_data`): 2 penugasan ada sebelum dan sesudah restart.
- Seluruh siklus audit dijalankan di browser terhadap container: **40/40 pemeriksaan lolos**.

## Batasan jujur
- Diuji di arm64. Server Linux biasa umumnya amd64: `docker compose up --build` **di server itu** membangun image amd64 sendiri (jangan memindahkan image dari Mac). Wheel `duckdb`/`pandas` tersedia untuk keduanya, tetapi build amd64 belum saya jalankan.
- Memori 1,5 GB dibatasi di `docker-compose.yml`; bila server hanya 1 GB, tambah swap.
- Data live SIRUP (`/api/freshness`) butuh server dapat keluar ke `sirup.inaproc.id`.
- Belum diuji dari internet/domain/HTTPS (Caddy); langkahnya mengikuti dokumentasi standar Caddy.
