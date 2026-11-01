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

