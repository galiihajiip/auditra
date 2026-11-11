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

## Batasan jujur
- `Dockerfile` **belum diuji dengan `docker build`** saat dibuat (daemon Docker tidak aktif di mesin pembuat). Langkah-langkahnya diuji terpisah: `npm ci` (dry-run) + `npm run build`, `pip install`, dan `uvicorn` mode parquet. Bila build gagal, kirim log-nya.
- Memori 1,5 GB dibatasi di `docker-compose.yml`; bila server hanya 1 GB, turunkan beban atau tambah swap.
- Data live SIRUP (`/api/freshness`) butuh server dapat keluar ke `sirup.inaproc.id`.
