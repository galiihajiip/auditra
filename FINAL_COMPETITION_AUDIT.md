# FINAL COMPETITION AUDIT — Auditra

Evaluator stance: independent, skeptical. Everything below was observed on the **running** application
(FastAPI + DuckDB on 3,002,992 real rows; React/Vite front-end driven by headless Chromium via Playwright at
1440×900, 820×1180 and 390×844). README claims were not treated as evidence.

Date: 2026-11-01. Tester environment: macOS, Python 3.11, Node 26.

---

## 0. Headline verdict

**Auditra is a competent, data-heavy analytics dashboard. It is not the product the evaluation brief describes.**

Questions 2, 3, 4 and 5 of the brief ask about a *project discovery → evidence submission* journey, a
*Project Passport*, *source provenance*, and *moderation/verification workflows*. **None of these exist in this
codebase** (searched all Python/TS/MD for passport, moderation, evidence, provenance, submit: zero hits; the API has
only `GET` endpoints; there is no database write path, no user, no auth). I will not score them as partially met.
They are **absent**. What exists is a read-only procurement-risk explorer ("which SIRUP package should an auditor
look at first, and why").

If judges are shown this as the brief's product, it fails those criteria outright. If it is judged as what it is, it
is a strong data-science demo with real engineering problems, most of which I fixed (see §3).

**Honest score (what I observed, after fixes), judged as a read-only analytics dashboard: ~64 %.**
Against the literal brief (journey, passport, moderation scored as absent): **47 / 100** (§4). Details in §4.

---

## 1. Answers to the 13 questions

| # | Question | Finding | Evidence |
|---|----------|---------|----------|
| 1 | Value prop in 10 s? | **Before: no.** Landing view was a logo, four dropdowns and KPI numbers with no sentence saying what it is for. **After fix: yes** (hero line "Dari 3 juta paket pengadaan, mana yang harus diaudit lebih dulu?"). | screenshots `desktop-top` vs `v-d-top` |
| 2 | Discovery → evidence submission journey? | **Does not exist.** Closest: filter → rank → open package. There is no way to submit, attach or record evidence. | no write endpoints (`api/routers/*`) |
| 3 | Is the Project Passport useful? | **No passport exists.** I added a package detail panel (7-signal breakdown, metadata, caveat, SIRUP link). It is a *risk explanation card*, not a verified passport. | `PackagesTable.tsx` |
| 4 | Source provenance? | **Weak.** One global footer link to SIRUP LKPP. No per-package source link/ID lineage/ingest date. Panel now shows the SIRUP ID and a SIRUP search link, but the link is a generic search page, not a deep link to the package. | footer, detail panel |
| 5 | Moderation/verification real? | **Neither real nor simulated: absent.** (The pipeline's `05_validate.py` is a data-QA gate, not moderation.) | grep, API surface |
| 6 | FE/BE separation? | **Good.** Clean REST boundary, bundle endpoint, server-side aggregation, parameterised SQL. Minor leak: business rule `max(risk_min,30)` is duplicated in FE (`client.ts`) and BE (`db.py`). | `api/db.py`, `web/src/api/client.ts` |
| 7 | Database design? | **Adequate for read-only analytics** (DuckDB over parquet, materialised view of 32 flat columns, geo lookup join). Not a relational/transactional design; no keys/constraints; one wide denormalised table; no schema for users/evidence. Cold start reads ~440 MB parquet. | `api/db.py`, `output/chunks` |
| 8 | Validation/authz/errors/edge cases? | **Input validation: good** (422 on `page=0`, `page_size=501`, `risk_min=abc`; SQL-injection string returned 0 rows, bound params). **Authz: none** (not needed for read-only, but `/docs` and all data are public; no rate-limit). **Error handling: had a P0 bug** (cold-start 500, fixed). Edge: `page=999999` returns empty 200 instead of 404/clamp (unfixed, P3). | curl matrix §5 |
| 9 | Visually competitive? | **Mostly yes in dark mode**: consistent tokens, good KPI cards, readable table. Weak: dense, single very long scroll, tiny type (10–11 px captions), emoji-glyph icons, no empty/illustrative states, KG canvas looks cluttered with 43 overlapping nodes. Light mode only spot-checked. | screenshots |
| 10 | Mobile/tablet/desktop? | No horizontal page overflow at any width (scrollWidth == innerWidth). Table scrolls inside its wrapper (970 px in 330 px). **Mobile map was poor** (map shrunk to a sliver beside a full-height colour bar) — partly fixed. Mobile page is ~7,500 px tall: usable, not good. Tablet checked by screenshot only. | `m-map.png`, measured widths |
| 11 | Dead buttons/links/components? | Tested: map owner-mode tabs (4), metric toggle, 4 selects, sidebar lembaga select, pagination, theme toggle, row click, GitHub link present. All functioned. **Found broken:** (a) default map tab "Kementerian/Lembaga" was *always empty* (fixed); (b) radar chart threw a runtime exception on every load (fixed); (c) table rows were not interactive despite being the natural drill-down (fixed). **Not tested:** KG node click/zoom/"Gerakkan lagi", sidebar "By Pagu"/search, region click on map, PWA install/offline. | §5 |
| 12 | Claims supported by evidence? | Several were **not**: see §2 (C1–C5). | §2 |
| 13 | Reliable to demo in front of judges? | **As configured: no.** Hosted backend is dead (see P0-2), cold start broke the page (P0-3, fixed). After fixes, a local one-process demo is reliable (verified from cold start → populated in ~7 s). | §3 |

---

## 2. Claims vs. evidence

| ID | Claim | Verdict |
|----|-------|---------|
| C1 | README: "Daftar Paket … akses penuh ke dataset via API"; UI: "semua baris dapat diakses via pagination" | **False.** Both UI and API force `RPI ≥ 30`; 2.38 M "RENDAH" rows are unreachable from the table/API list (only 623,805 of 3,002,992). UI text corrected; README line still overstated (not edited). |
| C2 | README signal table: S6 = "Sentralitas jaringan", S7 = "Komunitas risiko" | **False vs code.** `02_scoring.py`: S6 = dana APBN + metode, S7 = KG reputation. README corrected. |
| C3 | "LIVE" badge in header | **Misleading.** It is a static string; it never reflects backend health. Unfixed (P2). |
| C4 | "Verified statistics" (568 KRITIS etc.) | **Numbers match the API** (568 / 3,002,992 / 1,015,601 reproduced live). That the RPI *identifies risky packages* is **not evidenced**: there is no ground truth (known audit findings) in the repo; `06_sensitivity_analysis.py` only shows weight robustness. RPI is a heuristic prioritisation, which the UI now states. |
| C5 | Deployed app (`.env.production` → railway URL) | **Dead**: `GET https://auditra-production.up.railway.app/api/health` → `404 Application not found`. |
| C6 | Map "seluruh Indonesia" | Misleading: K/L (central ministry) packages — where the largest risk values sit — have **no kab/kota location**, so K/L map mode is blank by design. |

---

## 3. Weaknesses register

Severity: P0 = demo/product-breaking, P1 = serious, P2 = noticeable, P3 = polish.

### P0

**P0-1 — Product does not implement the brief's core journey** — *Unfixed (out of scope; not "safe & feasible")*
- Module: whole product (no passport, evidence, moderation, auth, DB writes).
- Repro: open app; try to submit evidence / find a passport / moderate → no UI or endpoint (`grep -ri "passport\|moderat\|evidence" .` → nothing; `curl -X POST localhost:8010/api/packages` → 405).
- Why: judges testing the stated criteria cannot score them.
- Fix: building it properly = users + auth, `evidence`/`review` tables (Postgres), submission form w/ validation + file handling, reviewer queue with state machine (pending → verified/rejected), audit log, provenance fields. Multi-day work; faking it with UI-only buttons would violate your "no simulation" bar, so I did not.
- Partial mitigation shipped: package detail panel (explains score), honest caveat text.

**P0-2 — Hosted backend is down** — *Not fixable from here; mitigated*
- Module: `web/.env.production`, `vercel.env`, `railway.toml`.
- Repro: `curl https://auditra-production.up.railway.app/api/health` → 404 "Application not found". Production build then shows "Dataset belum siap" (observed in screenshot).
- Why: any judge opening the deployed URL sees an error page.
- Fix/mitigation: redeploy Railway service (needs your account). Meanwhile **FastAPI now serves `web/dist` itself** (`api/main.py`): `VITE_API_URL=/api npm run build` then `uvicorn api.main:app` → one process, one URL. Verified: `/`, deep links → index.html, `/api/*` unaffected, unknown `/api/x` → 404 JSON.
- Fixed: **mitigated**, root cause (deployment) open.

**P0-3 — Cold start leaves the dashboard permanently broken** — *Fixed*
- Module: `api/routers/dashboard.py`.
- Repro (before): start API, load page immediately → `/api/dashboard/bundle` returns **500** (a 503 "warming" was caught by `except Exception` and re-raised as 500); client retry only handles 502/503, so the banner "Gagal memuat data filter: 503…" stayed forever and KPIs showed "—" (observed for 40 s).
- Why: the first thing judges see after launching the server.
- Fix: re-raise `HTTPException`; hide internal exception text behind a generic message + server log. After: cold start → populated at ~7 s, no banner. Regression test `test_dashboard_bundle_preserves_503`.

### P1

**P1-1 — Default map view blank** — *Fixed.* `ChoroplethMap.tsx`. Before: K/L tab default → all zeros, "Tidak ada data" under a 0–0.01 colour bar. After: auto-selects the first non-empty mode (Pemprov). Still blank if user manually picks K/L (by design of data, see C6; no explanatory text yet — P2).

**P1-2 — No value proposition on first view** — *Fixed.* `App.tsx` hero + "RPI is a priority tool, not a verdict".

**P1-3 — 6.7 MB single JS bundle (2.08 MB gzip)** — *Fixed (partly).* `vite.config.ts`, `App.tsx`. Entry chunk now 214 KB (72 KB gz); Plotly (4.9 MB, 1.48 MB gz) is a lazy chunk that loads with the map; ECharts 1.06 MB and vis 0.5 MB separate chunks. Plotly remains heavy — the real fix is MapLibre/deck.gl or a lighter Plotly partial bundle (`plotly.js-geo-dist-min`) (unfixed, P2).

**P1-4 — Radar chart throws on every load** — *Fixed.* `Charts.tsx`: radar rendered with zero indicators before data → `TypeError … 'push'` page error. Also set `type:"value"` on scatter axes explicitly. Prod build now emits **0 page errors** (verified, desktop + mobile).

**P1-5 — Unsupported "all rows accessible" claim (C1)** — *UI fixed, README partial.*

**P1-6 — Methodology docs contradict code (C2)** — *Fixed (README).*

**P1-7 — Mobile map unusable** — *Partly fixed.* Horizontal colour bar and 300 px height under 640 px. Verified visually; the map is now legible but small. Needs a true mobile layout (collapse sidebar, sticky filter drawer) — unfixed P2.

**P1-8 — Table rows were dead; no drill-down** — *Fixed.* Keyboard-accessible (`role=button`, Enter/Space, Esc closes, `aria-modal`) detail dialog w/ per-signal bars and weights from `02_scoring.py`.

### P2 (not fixed unless stated)

| ID | Issue | Module | Repro | Fix |
|----|-------|--------|-------|-----|
| P2-1 | "LIVE" badge is decoration | `AppHeader.tsx` | Stop API → badge still says LIVE | Poll `/api/health`; show Warming/Offline |
| P2-2 | No filter reset, no URL state/deep-linking, no table search/sort | `App.tsx`, `FilterBar.tsx` | Apply 3 filters, reload → lost | Sync filters to `URLSearchParams`; add Reset |
| P2-3 | No auth, no rate limiting, `/docs` public, CORS `allow_credentials=True` with env-driven origins | `api/main.py` | `curl /docs` → 200 | Fine for public open data; add rate-limit + disable docs in prod if not intended |
| P2-4 | `page` beyond `total_pages` returns 200 empty | `api/routers/packages.py` | `?page=999999` | Clamp or 404 |
| P2-5 | Business rule `risk_min ≥ 30` duplicated FE+BE, silently changes the user's "Semua" filter semantics | `client.ts`, `db.py` | Select "Semua" → table says RPI≥30 | Return `effective_risk_min` in response; show it |
| P2-6 | Entity naming quality: "lembaga" values include regencies (e.g. scatter "Kab. Simeulue"); sidebar shows only K/L-type | `db.py` rank queries | Hover scatter | Normalise owner type in pipeline |
| P2-7 | Dev-only: React StrictMode + react-plotly throws `_scrollZoom` in `vite dev` | `main.tsx` | `npm run dev`, open console | Dev-only, absent in prod build; guard `Plot` mount or upgrade lib |
| P2-8 | Accessibility not audited: 10–11 px captions, colour-only risk encoding in map/scatter, no labelled `<label for>` verified, KG canvas not keyboard-accessible | various | — | Run axe/Lighthouse; add text alternatives |
| P2-9 | Mobile page ~7.5 k px, 5 stacked charts; KG with 43 overlapping nodes is hard to read | layout | 390 px screenshot | Tabs/accordions on mobile |
| P2-10 | Service worker caches shell cache-first-with-network; a stale shell can survive deploys (`CACHE="auditra-v5"` manual bump) | `public/sw.js` | — | Build-hash cache name |
| P2-11 | 440 MB of parquet committed/needed to run; repo not runnable without it; `npm install` fails under a root-owned npm cache (environmental) | repo | fresh clone | Git LFS / release asset + `make demo` |
| P2-12 | No front-end tests, no E2E, no CI. Only pipeline tests existed | `tests/` | — | Add Playwright smoke test (script used here is a template) |

### P3
Emoji icons (🔍, ☀, 🌙) instead of SVG icons; footer lists student names/ID but no licence/data-use statement; ECharts console warning about `alignTicks` (non-blocking); `web/package.json` lacks maplibre-gl though `package-lock.json` references it (stale lock).

---

## 4. Scorecard (skeptical, observed only)

| Criterion | Weight | Score | Notes |
|-----------|-------:|------:|-------|
| Problem clarity & first impression | 10 | 7 | Good after hero; before: 3 |
| Core journey (discover → evidence) | 15 | **2** | Absent |
| Passport / provenance | 10 | **3** | Detail card only; weak provenance |
| Moderation / verification | 10 | **0** | Absent |
| Architecture & separation | 10 | 8 | Clean REST, aggregation server-side |
| Data model | 5 | 3 | Fine for analytics only |
| Validation / errors / security | 10 | 6 | Strong input validation; one P0 error bug fixed; no authn/rate-limit |
| Visual quality | 10 | 7 | Consistent dark theme; dense |
| Responsiveness | 5 | 3 | No overflow; mobile map/page weak |
| Reliability for live demo | 10 | 5 | Hosted dead; local good after fixes |
| Evidence for claims / testing | 5 | 3 | 12 tests pass; no FE tests; RPI unvalidated against ground truth |
| **Total (after fixes)** | 100 | **≈ 47 literal brief** | |

Reading the table honestly: against **this brief** the product scores ~47 *with* the zero-score rows included;
if the judges' rubric is instead "analytics/data-science dashboard", remove the three absent rows (35 pts) and
rescale: ≈ 64 %. I did not score the pre-fix state numerically.

---

## 5. What I ran (reproducible)

```bash
# backend (Python 3.11 venv)
pip install -r requirements-web.txt pytest httpx
cd web && npm install && VITE_API_URL=/api npm run build && cd ..
uvicorn api.main:app --port 8000        # serves API + built UI, http://127.0.0.1:8000
pytest tests                            # 12 passed
```

API matrix (all against live data): `page=0`→422; `page_size=501`→422; `risk_min=abc`→422; `risk_min=-5`→200;
`risk_min=1e9`→200 empty; `lembaga=' OR 1=1--`→200 empty (bound param, not injected); unknown province→200 zeros;
`DELETE /api/packages`→405; unknown route→404 JSON; `page=999999`→200 empty (P2-4).
Timings: packages page 5–190 ms, bundle (uncached filter) ≈ 0.35 s, cold init ≈ 7 s locally.
Browser: 3 viewports, filters (province/RPI/lembaga via sidebar), pagination, theme toggle, row dialog + Esc,
4 map modes (each switch ≈ 250–370 ms), console/page errors captured: prod build **0**, before fixes **2–3**.

**Not tested (disclosure):** KG interactions (click/zoom/physics toggle), sidebar search/"By Pagu", map region click →
filter, light-mode pixel review beyond one screenshot, PWA install/offline, real touch devices, screen reader,
Lighthouse/axe, load testing, Safari/Firefox.

## 6. Files changed

`api/main.py` (static SPA serving), `api/routers/dashboard.py` (503 preserved, no error leak),
`web/src/App.tsx` (hero, lazy loading), `web/src/components/ChoroplethMap.tsx` (auto mode, mobile),
`web/src/components/Charts.tsx` (radar guard, axis types), `web/src/components/PackagesTable.tsx` (detail dialog,
honest copy), `web/vite.config.ts` (chunking, configurable proxy `AUDITRA_API_URL`), `README.md` (S6/S7),
`tests/test_api_filters.py` (new), this file.

## 7. Priority list before judging

1. Decide honestly how the product maps to the brief; if the brief really requires evidence/moderation, that is a build, not a polish task.
2. Redeploy the backend or demo from the single-process local build (§5). Pre-warm it 30 s before judges arrive.
3. Add per-package provenance (source row id, ingest date, deep link) and a filter reset/URL state.
4. Replace the Plotly map; add a mobile layout; run axe/Lighthouse; add a Playwright smoke test to CI.


---

## 8. Revisi 2 (2026-11-11): dari dashboard menjadi alur kerja end-to-end

Menindaklanjuti P0-1 ("tidak ada alur discovery → evidence"). Yang **sekarang ada dan teruji di browser**
(skrip Playwright; 20 langkah PASS, termasuk skenario negatif):

| Kemampuan | Implementasi | Bukti |
|-----------|--------------|-------|
| Autentikasi | scrypt + token HMAC 12 jam, rate-limit login (429 setelah 8 percobaan) | `tests/test_cases_workflow.py` |
| Peran & pemisahan tugas | `auditor` membuka kasus/unggah bukti; `reviewer` memverifikasi/menolak. Reviewer tidak boleh menambah bukti; pendaftaran publik selalu auditor | 403 diuji di API dan UI |
| Alur kasus (state machine di server) | baru → ditelaah → menunggu_verifikasi → terverifikasi/ditolak; reviewer dapat mengembalikan; status terminal tak bisa diubah | transisi ilegal → 409 |
| Aturan bisnis | Tidak bisa diajukan tanpa bukti; tidak bisa disetujui bila masih ada bukti pending / tak ada yang terverifikasi; penolakan wajib alasan; satu kasus aktif per paket (unique index parsial di DB) | 422/409 diuji |
| Bukti | Tautan (hanya http/https) atau berkas (pdf/png/jpg/txt/csv ≤ 5 MB, cek *magic bytes* bukan hanya ekstensi, SHA-256, nama acak di disk, unduh butuh login) | berkas "x.pdf" palsu → 415 |
| Verifikasi nyata | Review per bukti dengan catatan, tercatat siapa/kapan | UI + riwayat |
| Jejak audit | Tabel `case_events` hanya-INSERT, tampil sebagai riwayat | UI |
| Passport paket | Halaman `/paket/:id`: atribut, 7 sinyal dengan **kontribusi ke RPI** (jumlah = RPI), provenance (sumber, jumlah baris, tahapan pipeline, tautan SIRUP) | screenshot `e2e-passport` |
| Rute & UX | React Router, deep link, guard login, cetak laporan kasus (CSS print), empty state | e2e |
| Skema DB | SQLite terpisah dari DuckDB analitik; FK, CHECK, unique index parsial | `api/appdb.py` |

Status temuan lama: **P0-1 → sebagian ditutup** (alur nyata ada; lihat batasan). **Q2, Q3, Q4, Q5 tidak lagi "absen"**, tetapi
belum setara produk produksi.

### Batasan yang masih jujur harus disebut
- **Akun demo berkata sandi publik** (`auditra2026`) di-seed secara default agar juri bisa mencoba. Di server publik **setel
  `AUDITRA_SEED_DEMO=0` dan `AUDITRA_SECRET`**, lalu buat reviewer dengan `scripts/create_user.py`. Tanpa itu, siapa pun bisa
  menjadi reviewer — moderasi tetap *berfungsi*, tetapi tidak *aman*.
- Token disimpan di `localStorage` (rentan jika ada XSS); tidak ada reset kata sandi, verifikasi email, MFA, atau UI admin.
- Rate-limit in-memory (hilang saat restart, tidak dibagi antar proses).
- SQLite + berkas lokal: cukup untuk satu server, bukan untuk multi-instance; tidak ada pemindaian virus pada unggahan.
- Semua pengguna login melihat semua kasus (ruang kerja tim), tanpa izin per-kasus.
- "Provenance" masih tingkat dataset/pipeline; belum ada tautan dalam (*deep link*) ke satu paket di SIRUP dan belum ada tanggal ingest per baris.
- Reviewer menolak bukti lewat `window.prompt` (fungsional, tetapi bukan UI yang dipoles).
- Belum ada tes unit frontend; E2E adalah skrip manual (belum di CI). Skor RPI tetap belum divalidasi terhadap temuan audit nyata.
- Deploy publik (Railway) masih mati; lihat P0-2.

Skor literal terhadap brief setelah revisi 2 (penilaian saya, bukan jaminan): alur 2→9/15, passport/provenance 3→7/10,
moderasi 0→6/10 → **total ≈ 62/100** (dari 47); keandalan demo tetap 5/10 sampai deploy dibereskan.


---

## 9. Revisi 3 (2026-11-11): data live SIRUP

Temuan awal (bukti: `GET /api/freshness`, probe langsung ke SIRUP): **snapshot analisis = 3.002.992 paket, SIRUP saat ini = 3.646.128**,
yaitu **643.136 paket (17,6%) belum masuk analisis**. Label "LIVE" di versi awal tidak benar dan sudah dihapus.

Yang dibangun: `scraper/sirup.py` (crawler sopan & dapat dilanjutkan, pembagian per rentang pagu, rekonsiliasi),
`scraper/detail.py` (parser halaman detail), `scraper/delta.py` (snapshot vs live), `api/freshness.py` + endpoint
`/api/freshness` & `/api/packages/{id}/live`, panel "Kesegaran data" di dasbor, tombol "Bandingkan dengan SIRUP sekarang" di passport.
Diuji: 9 tes baru tanpa jaringan (termasuk nilai pagu identik > 1 halaman, *resume*, fail-soft, rate-limit) + uji live
(rentang 9,7–9,9 jt: 9.007 baris, cocok persis dengan hitungan situs, 0 duplikat) + cek langsung satu paket nyata (sinkron).

Batasan yang harus jujur disebut:
- **Skor RPI belum memakai data live.** Panel hanya mengukur dan menampilkan selisih. Memasukkan 643 ribu paket baru ke analisis
  = menjalankan ulang pipeline dan **mengubah semua angka** yang dipakai di esai/dokumen lomba; belum dilakukan.
- Endpoint daftar SIRUP **tidak memuat uraian/volume/spesifikasi**; sinyal fragmentasi (bobot 15%) memakainya. Paket baru
  hanya bisa memakai nama paket sebagai pengganti, atau halaman detail per paket (±643 ribu permintaan, tidak dilakukan).
- Scraper bergantung pada struktur endpoint yang tidak resmi/tidak berdokumen; bisa berubah tanpa pemberitahuan. Ia gagal dengan jelas
  (bukan diam-diam) dan panel memakai mode *fail-soft*.
- Izin: situs tidak punya `robots.txt`, data adalah publikasi publik; pemilik tim menyatakan boleh. Syarat penggunaan resmi LKPP belum saya baca/verifikasi.
- Tanggal ekspor snapshot lama tetap tidak tercatat (isi `data/snapshot.json` bila diketahui).


---

## 10. Revisi 4 (2026-11-11): UI/UX dan alur pengguna

Masalah yang dikeluhkan dan diverifikasi di tangkapan layar awal: 37 teks 10–11 px, palet slate generik, emoji sebagai ikon, satu
halaman dasbor sangat panjang (≈4.500 px desktop / 7.500 px ponsel), tanpa nilai jual di layar pertama, tabel sebagai satu-satunya jalan ke paket,
`window.prompt` untuk input alasan, pesan status inline.

| Area | Sebelum → sesudah |
|------|-------------------|
| Tipografi | Tidak ada teks < 12 px (0 kemunculan `text-[10px]/[11px]`); basis 15 px; judul Plus Jakarta Sans; angka tabular |
| Identitas visual | Palet navy-tinta + aksen teal khas merek, gradient hero + grid, kartu 16 px, ikon SVG (menggantikan emoji), cincin skor RPI sebagai elemen khas |
| Layar pertama | Hero berisi nilai jual + CTA "Coba demo" satu klik + strip alur 4 langkah + pratinjau passport dari **paket teratas nyata** |
| Alur | Dasbor memberi urutan Temukan → Pahami konteks → Tindaklanjuti; kartu "Prioritas audit teratas" langsung membuka passport; passport punya satu CTA kontekstual (Masuk / Buka kasus / Lanjutkan kasus) + bar lengket di ponsel; stepper 4 langkah di passport & kasus |
| Konteks | Filter, halaman, dan tab tersimpan di URL; tombol "Kembali ke hasil" mengembalikan filter yang sama (diuji E2E) |
| Panjang halaman | Analitik dipecah jadi 3 tab (Peta, Analitik, Jaringan) yang di-render saat dibuka; tabel menjadi kartu di ponsel |
| Kasus | Papan Kanban + daftar; kartu "Langkah berikutnya" sesuai peran/status; dropzone unggah; riwayat bergaya timeline; toast + dialog menggantikan `prompt` dan pesan inline |
| Umpan balik | *Skeleton* (bukan "—"/"Memuat"), bar progres, empty state dengan tindakan, error ramah |
| Aksesibilitas | Fokus keyboard terlihat, `aria` pada tab/radio/dialog/progress/status, judul langkah berikutnya sebagai heading, `prefers-reduced-motion` dihormati |
| Responsif | Overflow horizontal ditemukan (679/390 px, akar: peta Plotly memaksa kolom grid melebar) dan diperbaiki; kini 390/390 di `/`, `/masuk`, `/kasus/:id` |

Bukti: `tests/e2e/smoke.mjs` (29 pemeriksaan di browser: demo login, filter di URL, passport, buka kasus, bukti tautan/berkas, berkas palsu ditolak,
aturan server, peninjauan reviewer, persetujuan, papan, tanpa overflow ponsel, tanpa error halaman) **29/29 lulus**; `pytest` 28 lulus.
Temuan selama pengujian dan sudah diperbaiki: overflow ponsel; judul panduan bukan heading; *crawler* berhenti pada potongan data padat (lihat §9).

Batasan jujur: **belum ada uji kegunaan dengan pengguna nyata** (penilaian di sini berdasarkan tangkapan layar dan skrip, bukan manusia);
belum diaudit dengan axe/Lighthouse; kontras mode terang hanya diperiksa visual; peta Plotly (±4,9 MB) tetap berat dan belum diganti;
ukuran total `dist` ≈ 6,8 MB (sebagian besar chunk Plotly yang dimuat malas); hanya Chromium yang diuji (bukan Safari/Firefox/perangkat sungguhan).


---

## 11. Revisi 5 (2026-11-11): alur audit berdasarkan riset proses audit nyata

Permintaan: riset sedalam mungkin cara auditor mengaudit pengadaan, lalu implementasikan **tanpa mengarang alur**. Hasil riset lengkap, dengan nomor
pasal/paragraf dan status verifikasi tiap sumber, ada di `docs/RISET_PROSES_AUDIT.md` (dan ringkasannya di aplikasi: `/metodologi`).

**Sumber primer yang dibaca langsung:** PBPK 1/2026 (SPKN; 117 ribu karakter), Perban BPKP 3/2019 (batang tubuh), teks konsolidasi Perpres 16/2018 jo. 12/2021 jo. 46/2025
(JDIH LKPP; 146 ribu karakter), IACRC red flags. **Sekunder:** Perban BPKP 6/2026 (pasal.id), ringkasan Lampiran III 2019, berita KPK/BPK.

**Temuan riset yang mengubah desain** (semua bersumber teks, bukan dugaan):
1. Alur nyata = perencanaan → pelaksanaan → komunikasi hasil → pemantauan tindak lanjut, dengan **supervisi berjenjang** (SPKN Pelaksanaan par. 43–45).
2. Bukti dinilai **cukup** (kuantitas) dan **tepat** (relevan, valid, andal) (par. 29); bentuk (par. 31) dan teknik (par. 32) baku; dokumen diragukan wajib didalami (par. 34).
3. Temuan hanya bila **kondisi ≠ kriteria**; unsur kondisi, kriteria, akibat, sebab; sumber kriteria wajib; indikasi kecurangan diperlakukan khusus (par. 39–42; Pelaporan 18–21).
4. Tanggapan tertulis entitas wajib didokumentasikan; rekomendasi harus menyebut pihak bertanggung jawab (Pelaporan 22–28).
5. **Perubahan regulasi** yang berdampak: PBPK 1/2026 baru berlaku 2 tahun setelah diundangkan; Perban BPKP 6/2026 mencabut 3/2019; Perpres 46/2025 menaikkan batas pengadaan langsung **konstruksi menjadi Rp400 jt**.
6. **Koreksi terhadap metodologi RPI kita** (belum diterapkan ke skor): batas konstruksi Rp400 jt (S3 memakai Rp200 jt untuk semua), paket ≤ Rp15 M diperuntukkan UMK (Pasal 65(3); S5 memakai persentil), HPS bukan dasar kerugian negara (Pasal 26(6); S2 tak boleh dibaca "kemahalan").
7. Larangan memecah paket ada di **Pasal 20(2)(d)** dan mensyaratkan *maksud menghindari tender*, bukan Pasal 21 seperti yang sempat tertulis di dokumentasi lama.

**Yang diimplementasikan** (tahap: seleksi → perencanaan → pelaksanaan → reviu berjenjang → komunikasi → selesai/dihentikan → pemantauan tindak lanjut):
- **Program audit dibangkitkan** dari atribut dan sinyal paket (`api/audit_program.py`): tiap prosedur memuat kriteria bersumber pasal, bukti yang diharapkan, teknik, dan peringatan
  (mis. batas pengadaan langsung per jenis; dasar "keadaan tertentu" penunjukan langsung + Pasal 41A; dasar pengecualian Pasal 61; HPS Pasal 26(6)).
- **Gerbang kesiapan** per transisi, dihitung dan ditegakkan server (422 + daftar syarat), ditampilkan sebagai checklist; syarat yang benar secara vakum ditandai "belum berlaku".
- Bukti dengan bentuk/teknik/asal, penilaian relevan-valid-andal, penanda keaslian, SHA-256; temuan berunsur lengkap; tanggapan entitas; tindak lanjut per rekomendasi; riwayat tak dapat diubah.
- Pemisahan tugas dan peran dijaga di server; migrasi skema aman (berkas lama dicadangkan, tidak dihapus).

**Bukti pengujian:** pytest 39 lulus (siklus penuh, gerbang, peran, migrasi, program audit); E2E browser **40/40** (siklus penuh auditor ↔ reviewer + mobile + halaman metodologi).

**Pengakuan koreksi proses (penting):** pada revisi-revisi sebelumnya saya melaporkan "typecheck bersih", padahal `tsc -p tsconfig.app.json` memeriksa **0 berkas**
(`tsconfig.app.json` berisi `"files": []`). Pemeriksaan nyata baru berjalan di revisi ini (`npm run typecheck` memakai `tsconfig.json`) dan menemukan 11 error yang semuanya ada di kode yang
sedang saya ubah (bukan di kode lama). Kini `npm run build` menjalankan typecheck lebih dulu sehingga tidak bisa lolos diam-diam.

**Batasan yang harus jujur disebut:**
- **Belum divalidasi auditor praktisi.** Alur disusun dari standar tertulis, bukan wawancara. Ini risiko terbesar untuk klaim "sesuai praktik".
- **Lampiran pedoman audit BPKP (langkah kerja rinci, kertas kerja) tidak dapat diakses**; program audit disusun dari pasal Perpres dan SPKN, bukan salinan pedoman itu.
- Perban BPKP 6/2026 dibaca dari salinan pasal.id (belum ditinjau); OECD (403) dan materi Inspektorat DIY (404) tidak terbaca; red flags diambil dari IACRC.
- Tidak dimodelkan: persetujuan program audit oleh pengendali teknis, surat tugas, management representation letter, PDTT Investigatif sebagai jenis terpisah, penilaian SPIP, tenggat tindak lanjut baku (60 hari hanya terverifikasi untuk BPK).
- Data kita hanya tahap **perencanaan (RUP)**; bukti pelaksanaan kontrak/serah terima tetap harus dikumpulkan dari entitas. Auditra membantu seleksi, dokumentasi, dan disiplin proses; ia **tidak** menggantikan pemeriksaan.
- Skor RPI tidak berubah; koreksi metodologi no. 6 menunggu keputusan menjalankan ulang pipeline.
