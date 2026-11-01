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
