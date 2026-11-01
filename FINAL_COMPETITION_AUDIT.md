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
