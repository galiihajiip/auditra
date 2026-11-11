"""Penugasan audit: siklus perencanaan → pelaksanaan → reviu berjenjang → komunikasi → penyelesaian → tindak lanjut.

Dasar: docs/RISET_PROSES_AUDIT.md (SPKN PBPK 1/2026; Perban BPKP 6/2026; Perpres 16/2018 jo. 46/2025).
Aturan peran dan syarat kesiapan ("gerbang") dijaga di server, bukan hanya di antarmuka.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from api.appdb import UPLOAD_DIR, db
from api.audit_program import (
    DEFAULT_SCOPE, EVIDENCE_FORMS, SOURCE_ORIGINS, STAGE_KEYS, STAGES, TECHNIQUES, build_program,
)
from api.auth import current_user, require_role
from api.deps import require_store

router = APIRouter(prefix="/api", tags=["cases"])

PHASES = ["seleksi", "perencanaan", "pelaksanaan", "reviu", "komunikasi", "selesai", "dihentikan"]
ACTIVE = ("seleksi", "perencanaan", "pelaksanaan", "reviu", "komunikasi")

# (dari, ke) -> peran. Pemisahan tugas: pelaksana (auditor) ≠ peninjau (reviewer) — SPKN Pelaksanaan par. 43–44.
TRANSITIONS: dict[tuple[str, str], tuple[str, ...]] = {
    ("seleksi", "perencanaan"): ("auditor",),
    ("perencanaan", "pelaksanaan"): ("auditor",),
    ("pelaksanaan", "reviu"): ("auditor",),
    ("reviu", "pelaksanaan"): ("reviewer",),
    ("reviu", "komunikasi"): ("reviewer",),
    ("reviu", "selesai"): ("reviewer",),
    ("komunikasi", "selesai"): ("reviewer",),
    **{(p, "dihentikan"): ("auditor", "reviewer") for p in ACTIVE},
}
NOTE_REQUIRED = {("reviu", "pelaksanaan"), *{(p, "dihentikan") for p in ACTIVE}}

MAX_UPLOAD = 5 * 1024 * 1024
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".csv"}
ALLOWED_MAGIC = {".pdf": (b"%PDF",), ".png": (b"\x89PNG",), ".jpg": (b"\xff\xd8\xff",), ".jpeg": (b"\xff\xd8\xff",)}

TANGGAPAN = ("diterima", "diterima_sebagian", "ditolak", "tidak_ada_tanggapan")
TL_STATUS = ("belum", "dalam_proses", "sesuai", "tidak_sesuai", "tidak_dapat_ditindaklanjuti")


# ── skema request ───────────────────────────────────────────────────────────
class CaseIn(BaseModel):
    package_id: int = Field(gt=0)
    selection_reason: str | None = Field(default=None, max_length=2000)


class PlanIn(BaseModel):
    selection_reason: str | None = Field(default=None, max_length=2000)
    objective: str | None = Field(default=None, max_length=2000)
    scope_stages: list[str] | None = None
    criteria_note: str | None = Field(default=None, max_length=2000)
    materiality_note: str | None = Field(default=None, max_length=2000)
    risk_note: str | None = Field(default=None, max_length=2000)
    conclusion: str | None = Field(default=None, max_length=4000)


class TransitionIn(BaseModel):
    to: str
    note: str | None = Field(default=None, max_length=2000)


class NoteIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CriterionIn(BaseModel):
    ref: str = Field(min_length=3, max_length=200)
    text: str = Field(min_length=3, max_length=1000)


class ProcedureIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    objective: str | None = Field(default=None, max_length=1000)
    stage: str = "lintas"
    criteria: list[CriterionIn] = Field(min_length=1)
    techniques: list[str] = Field(default_factory=list)


class ResultIn(BaseModel):
    status: str
    result_note: str | None = Field(default=None, max_length=2000)


class ReviewIn(BaseModel):
    decision: str
    note: str | None = Field(default=None, max_length=1000)


class QualityIn(BaseModel):
    relevan: bool
    valid: bool
    andal: bool
    authenticity_concern: bool = False
    authenticity_note: str | None = Field(default=None, max_length=1000)


class FindingIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    procedure_id: int | None = None
    kondisi: str = Field(min_length=5, max_length=3000)
    kriteria: str = Field(min_length=5, max_length=3000)
    kriteria_sumber: str = Field(min_length=3, max_length=500)
    sebab: str | None = Field(default=None, max_length=3000)
    akibat: str | None = Field(default=None, max_length=3000)
    nilai_potensi: float | None = Field(default=None, ge=0)
    rekomendasi: str | None = Field(default=None, max_length=3000)
    rekomendasi_kepada: str | None = Field(default=None, max_length=300)
    indikasi_kecurangan: bool = False
    evidence_ids: list[int] = Field(default_factory=list)


class ResponseIn(BaseModel):
    tanggapan_status: str
    tanggapan: str | None = Field(default=None, max_length=3000)


class FollowupIn(BaseModel):
    tl_status: str
    tl_note: str | None = Field(default=None, max_length=2000)


# ── util ────────────────────────────────────────────────────────────────────
def _event(conn, case_id, user_id, type_, body=None, frm=None, to=None):
    conn.execute(
        "INSERT INTO case_events(case_id,user_id,type,from_status,to_status,body) VALUES (?,?,?,?,?,?)",
        (case_id, user_id, type_, frm, to, body),
    )
    conn.execute("UPDATE cases SET updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?", (case_id,))


def _case_or_404(conn, case_id: int):
    row = conn.execute(
        "SELECT c.*, u.name AS created_by_name FROM cases c JOIN users u ON u.id=c.created_by WHERE c.id=?", (case_id,)
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Penugasan tidak ditemukan.")
    return row


def _require_phase(case, *phases: str, what: str = "aksi ini"):
    if case["phase"] not in phases:
        raise HTTPException(status_code=409, detail=f"{what.capitalize()} hanya dapat dilakukan pada tahap: {', '.join(phases)} (saat ini: {case['phase']}).")


def _loads(s, default):
    try:
        return json.loads(s) if s else default
    except Exception:
        return default


def _procedure_dict(r) -> dict:
    d = dict(r)
    d["criteria"] = _loads(d["criteria"], [])
    d["evidence_expected"] = _loads(d["evidence_expected"], [])
    d["techniques"] = _loads(d["techniques"], [])
    d["custom"] = bool(d["custom"])
    return d


# ── gerbang kesiapan ────────────────────────────────────────────────────────
def _gate(key, label, ok, hint=None, blocking=True, na=False):
    """na = belum berlaku (benar secara vakum, belum ada yang dinilai); tidak ditampilkan sebagai centang hijau."""
    return {"key": key, "label": label, "ok": bool(ok), "hint": hint, "blocking": blocking, "na": bool(na and ok)}


def compute_gates(conn, case, to: str) -> list[dict]:
    cid = case["id"]
    frm = case["phase"]
    procs = [dict(r) for r in conn.execute("SELECT * FROM procedures WHERE case_id=?", (cid,))]
    evid = [dict(r) for r in conn.execute("SELECT * FROM evidence WHERE case_id=?", (cid,))]
    finds = [dict(r) for r in conn.execute("SELECT * FROM findings WHERE case_id=?", (cid,))]
    fe: dict[int, list[int]] = {}
    for r in conn.execute("SELECT fe.finding_id, fe.evidence_id FROM finding_evidence fe JOIN findings f ON f.id=fe.finding_id WHERE f.case_id=?", (cid,)):
        fe.setdefault(r["finding_id"], []).append(r["evidence_id"])
    ev_by_id = {e["id"]: e for e in evid}
    g: list[dict] = []

    if (frm, to) == ("seleksi", "perencanaan"):
        g.append(_gate("alasan", "Alasan seleksi sasaran diisi (≥ 10 karakter)", len((case["selection_reason"] or "").strip()) >= 10,
                       "Jelaskan faktor risiko: nilai, sinyal RPI, kompleksitas, perhatian pemangku kepentingan, permintaan pimpinan."))
    elif (frm, to) == ("perencanaan", "pelaksanaan"):
        scope = _loads(case["scope_stages"], [])
        g += [
            _gate("tujuan", "Tujuan penugasan dinyatakan jelas", bool((case["objective"] or "").strip()), "SPKN Pelaksanaan par. 9–10."),
            _gate("lingkup", "Lingkup tahap pengadaan dipilih", len(scope) > 0, "Perpres Pasal 76(3): perencanaan s.d. serah terima."),
            _gate("risiko", "Penilaian risiko (termasuk risiko kecurangan) dicatat", bool((case["risk_note"] or "").strip()), "SPKN Pelaksanaan par. 16–19."),
            _gate("materialitas", "Pertimbangan materialitas (kuantitatif & kualitatif) dicatat", bool((case["materiality_note"] or "").strip()), "SPKN Pelaksanaan par. 23–25."),
            _gate("program", "Program audit memiliki ≥ 1 prosedur", len(procs) > 0, "Bangkitkan program audit dari tab Perencanaan."),
        ]
    elif (frm, to) == ("pelaksanaan", "reviu"):
        pending = [p for p in procs if p["status"] == "belum"]
        no_ev = [p for p in procs if p["status"] in ("sesuai", "tidak_sesuai")
                 and not any(e["procedure_id"] == p["id"] for e in evid)]
        no_reason = [p for p in procs if p["status"] == "tidak_dapat_diuji" and not (p["result_note"] or "").strip()]
        bad_no_find = [p for p in procs if p["status"] == "tidak_sesuai" and not any(f["procedure_id"] == p["id"] for f in finds)]
        weak = [f for f in finds if not fe.get(f["id"])]
        unq = [f for f in finds for eid in fe.get(f["id"], []) if not all(ev_by_id[eid][k] for k in ("relevan", "valid", "andal"))]
        no_to = [f for f in finds if f["rekomendasi"] and not (f["rekomendasi_kepada"] or "").strip()]
        g += [
            _gate("prosedur", f"Semua prosedur memiliki hasil ({len(procs) - len(pending)}/{len(procs)})", not pending and procs,
                  "Isi hasil: sesuai / tidak sesuai / tidak dapat diuji.", True),
            _gate("bukti_hasil", "Setiap hasil 'sesuai'/'tidak sesuai' didukung ≥ 1 bukti", not no_ev,
                  (f"Belum ada bukti: {', '.join(p['code'] for p in no_ev)}" if no_ev else None), na=bool(pending)),
            _gate("tdu", "Prosedur 'tidak dapat diuji' disertai alasan", not no_reason,
                  (f"Alasan kosong: {', '.join(p['code'] for p in no_reason)}" if no_reason else None), na=bool(pending)),
            _gate("temuan_dari_ketidaksesuaian", "Setiap 'tidak sesuai' menghasilkan temuan (kondisi ≠ kriteria)", not bad_no_find,
                  (f"Belum ada temuan: {', '.join(p['code'] for p in bad_no_find)}" if bad_no_find else "SPKN Pelaksanaan par. 39."), na=bool(pending)),
            _gate("temuan_bukti", "Setiap temuan didukung ≥ 1 bukti", not weak,
                  (f"Temuan tanpa bukti: {', '.join('#' + str(f['id']) for f in weak)}" if weak else "SPKN Umum par. 72."), na=not finds),
            _gate("kualitas_bukti", "Bukti pendukung temuan dinilai relevan, valid, dan andal", not unq,
                  "SPKN Pelaksanaan par. 29: ketepatan = relevan, valid, andal.", na=not finds),
            _gate("rekomendasi_pihak", "Rekomendasi menyebut pihak yang bertanggung jawab", not no_to, "SPKN Pelaporan par. 24.", na=not any(f["rekomendasi"] for f in finds)),
        ]
        concern = [e for e in evid if e["authenticity_concern"]]
        if concern:
            g.append(_gate("autentisitas", f"{len(concern)} bukti ditandai diragukan keasliannya: pastikan pendalaman dilakukan", False,
                           "SPKN Pelaksanaan par. 34: wajib pendalaman bila dokumen diduga tidak autentik.", blocking=False))
    elif (frm, to) == ("reviu", "pelaksanaan"):
        pass
    elif (frm, to) in (("reviu", "komunikasi"), ("reviu", "selesai")):
        pend = [e for e in evid if e["review_status"] == "pending"]
        unsupported = [f for f in finds if not any(ev_by_id[x]["review_status"] == "verified" for x in fe.get(f["id"], []))]
        g.append(_gate("tinjau_bukti", f"Seluruh bukti telah ditinjau ({len(evid) - len(pend)}/{len(evid)})", not pend, "Tinjau tiap bukti: terima atau tolak dengan alasan."))
        if to == "komunikasi":
            g.append(_gate("ada_temuan", "Ada temuan untuk dikomunikasikan", len(finds) > 0, "Tanpa temuan: selesaikan langsung dengan kesimpulan."))
            g.append(_gate("temuan_terverifikasi", "Setiap temuan didukung ≥ 1 bukti yang diterima", not unsupported,
                           (f"Dikembalikan bila bukti ditolak: temuan {', '.join('#' + str(f['id']) for f in unsupported)}" if unsupported else None)))
        else:
            g.append(_gate("tanpa_temuan", "Tidak ada temuan (bila ada, lanjut ke komunikasi)", len(finds) == 0))
            g.append(_gate("kesimpulan", "Kesimpulan penugasan diisi", bool((case["conclusion"] or "").strip()), "Unsur LHP: kesimpulan (SPKN Pelaporan par. 12)."))
    elif (frm, to) == ("komunikasi", "selesai"):
        no_resp = [f for f in finds if f["tanggapan_status"] == "belum"]
        no_to = [f for f in finds if f["rekomendasi"] and not (f["rekomendasi_kepada"] or "").strip()]
        g += [
            _gate("tanggapan", f"Tanggapan tertulis tiap temuan tercatat ({len(finds) - len(no_resp)}/{len(finds)})", not no_resp,
                  "SPKN Pelaporan par. 26–28. Bila entitas tidak menanggapi, catat status 'tidak ada tanggapan'."),
            _gate("kesimpulan", "Kesimpulan penugasan diisi", bool((case["conclusion"] or "").strip()), "Unsur LHP: kesimpulan."),
            _gate("rekomendasi_pihak", "Rekomendasi menyebut pihak yang bertanggung jawab", not no_to, "SPKN Pelaporan par. 24."),
        ]
    elif to == "dihentikan":
        g.append(_gate("alasan_henti", "Alasan penghentian ditulis (dikomunikasikan tertulis)", True, "SPKN Pelaksanaan par. 46–47."))
    return g


# ── detail ──────────────────────────────────────────────────────────────────
def _case_detail(conn, case_id: int, user: dict | None = None) -> dict:
    case = dict(_case_or_404(conn, case_id))
    case["scope_stages"] = _loads(case["scope_stages"], [])
    row = _case_or_404(conn, case_id)
    case["procedures"] = [_procedure_dict(r) for r in conn.execute("SELECT * FROM procedures WHERE case_id=? ORDER BY id", (case_id,))]
    case["events"] = [dict(r) for r in conn.execute(
        """SELECT e.*, u.name AS user_name, u.role AS user_role FROM case_events e
           JOIN users u ON u.id=e.user_id WHERE e.case_id=? ORDER BY e.id""", (case_id,))]
    case["evidence"] = []
    for r in conn.execute(
        """SELECT v.id,v.procedure_id,v.kind,v.title,v.url,v.filename,v.mime,v.size_bytes,v.sha256,v.form,v.technique,v.origin,
                  v.doc_date,v.relevan,v.valid,v.andal,v.authenticity_concern,v.authenticity_note,v.added_at,v.added_by,
                  v.review_status,v.reviewed_at,v.review_note, a.name AS added_by_name, r.name AS reviewed_by_name
           FROM evidence v JOIN users a ON a.id=v.added_by LEFT JOIN users r ON r.id=v.reviewed_by
           WHERE v.case_id=? ORDER BY v.id""", (case_id,)):
        d = dict(r)
        for k in ("relevan", "valid", "andal", "authenticity_concern"):
            d[k] = bool(d[k])
        case["evidence"].append(d)
    fe: dict[int, list[int]] = {}
    for r in conn.execute("SELECT fe.finding_id, fe.evidence_id FROM finding_evidence fe JOIN findings f ON f.id=fe.finding_id WHERE f.case_id=?", (case_id,)):
        fe.setdefault(r["finding_id"], []).append(r["evidence_id"])
    case["findings"] = []
    for r in conn.execute("SELECT f.*, u.name AS created_by_name FROM findings f JOIN users u ON u.id=f.created_by WHERE f.case_id=? ORDER BY f.id", (case_id,)):
        d = dict(r)
        d["indikasi_kecurangan"] = bool(d["indikasi_kecurangan"])
        d["evidence_ids"] = fe.get(d["id"], [])
        case["findings"].append(d)

    case["transitions"] = []
    for (frm, to), roles in TRANSITIONS.items():
        if frm != case["phase"]:
            continue
        gates = compute_gates(conn, row, to)
        case["transitions"].append({
            "to": to, "roles": list(roles), "note_required": (frm, to) in NOTE_REQUIRED,
            "gates": gates, "ready": all(x["ok"] for x in gates if x["blocking"]),
        })
    case["advisories"] = []
    if any(f["indikasi_kecurangan"] for f in case["findings"]):
        case["advisories"].append({
            "key": "kecurangan",
            "text": "Ada temuan berindikasi awal kecurangan. SPKN (Pelaksanaan par. 42): tindak lanjuti sesuai ketentuan atau usulkan Pemeriksaan DTT Investigatif. Di laporan, sajikan dampaknya tanpa menguraikan kecurangan secara rinci (Pelaporan par. 21).",
        })
    case["meta"] = {
        "stages": [{"key": k, "label": v} for k, v in STAGES],
        "forms": EVIDENCE_FORMS, "techniques": TECHNIQUES, "origins": SOURCE_ORIGINS,
    }
    return case


# ── penugasan ───────────────────────────────────────────────────────────────
@router.post("/cases", status_code=201)
def create_case(body: CaseIn, user: dict = Depends(require_role("auditor"))):
    pkg = require_store().fetch_package(body.package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan di dataset.")
    title = str(pkg.get("paket") or f"Paket {body.package_id}")[:200]
    try:
        with db() as conn:
            cur = conn.execute(
                """INSERT INTO cases(package_id,title,lembaga,rpi,risk_label,pagu,jenis_pengadaan,metode,selection_reason,scope_stages,created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (body.package_id, title, pkg.get("lembaga"), pkg.get("RPI"), pkg.get("risk_label"), pkg.get("pagu"),
                 pkg.get("jenisPengadaan"), pkg.get("metode"), (body.selection_reason or "").strip() or None,
                 json.dumps(DEFAULT_SCOPE), user["id"]),
            )
            cid = cur.lastrowid
            _event(conn, cid, user["id"], "dibuat", body.selection_reason, None, "seleksi")
            return _case_detail(conn, cid)
    except sqlite3.IntegrityError:
        with db() as conn:
            row = conn.execute(
                "SELECT id FROM cases WHERE package_id=? AND phase NOT IN ('selesai','dihentikan')", (body.package_id,)
            ).fetchone()
        raise HTTPException(status_code=409, detail={"message": "Paket ini sudah memiliki penugasan aktif.", "case_id": row["id"] if row else None})


@router.get("/cases")
def list_cases(phase: str | None = None, mine: bool = False, user: dict = Depends(current_user)):
    if phase and phase not in PHASES:
        raise HTTPException(status_code=422, detail="Tahap tidak dikenal.")
    sql = """SELECT c.id,c.package_id,c.title,c.lembaga,c.rpi,c.risk_label,c.pagu,c.phase,c.outcome,
                    c.created_at,c.updated_at,u.name AS created_by_name,
                    (SELECT COUNT(*) FROM evidence e WHERE e.case_id=c.id) AS n_evidence,
                    (SELECT COUNT(*) FROM findings f WHERE f.case_id=c.id) AS n_findings,
                    (SELECT COUNT(*) FROM procedures p WHERE p.case_id=c.id AND p.status<>'belum') AS n_tested,
                    (SELECT COUNT(*) FROM procedures p WHERE p.case_id=c.id) AS n_procedures
             FROM cases c JOIN users u ON u.id=c.created_by WHERE 1=1"""
    params: list = []
    if phase:
        sql += " AND c.phase=?"; params.append(phase)
    if mine:
        sql += " AND c.created_by=?"; params.append(user["id"])
    sql += " ORDER BY c.updated_at DESC LIMIT 500"
    with db() as conn:
        return {"data": [dict(r) for r in conn.execute(sql, params)]}


@router.get("/cases/stats")
def case_stats(user: dict = Depends(current_user)):
    with db() as conn:
        counts = {p: 0 for p in PHASES}
        for r in conn.execute("SELECT phase, COUNT(*) n FROM cases GROUP BY phase"):
            counts[r["phase"]] = r["n"]
    return {"counts": counts, "total": sum(counts.values())}


@router.get("/cases/by-package/{package_id}")
def case_for_package(package_id: int, user: dict = Depends(current_user)):
    with db() as conn:
        rows = conn.execute("SELECT id,phase,updated_at FROM cases WHERE package_id=? ORDER BY id DESC", (package_id,)).fetchall()
    return {"data": [dict(r) for r in rows]}


@router.get("/cases/{case_id}")
def get_case(case_id: int, user: dict = Depends(current_user)):
    with db() as conn:
        return _case_detail(conn, case_id)


@router.put("/cases/{case_id}/plan")
def update_plan(case_id: int, body: PlanIn, user: dict = Depends(current_user)):
    with db() as conn:
        case = _case_or_404(conn, case_id)
        fields = body.model_dump(exclude_unset=True)
        # kesimpulan ditulis menjelang penyelesaian oleh auditor (draft) atau reviewer (final)
        if "conclusion" in fields:
            _require_phase(case, "pelaksanaan", "reviu", "komunikasi", what="menulis kesimpulan")
        if {"selection_reason"} & fields.keys():
            _require_phase(case, "seleksi", "perencanaan", what="mengubah alasan seleksi")
        plan_keys = {"objective", "scope_stages", "criteria_note", "materiality_note", "risk_note"}
        if plan_keys & fields.keys():
            _require_phase(case, "seleksi", "perencanaan", what="mengubah rencana penugasan")
        if user["role"] != "auditor" and (plan_keys | {"selection_reason"}) & fields.keys():
            raise HTTPException(status_code=403, detail="Hanya auditor yang menyusun rencana penugasan.")
        if "conclusion" in fields and user["role"] == "reviewer" and case["phase"] == "pelaksanaan":
            raise HTTPException(status_code=403, detail="Reviewer menulis kesimpulan pada tahap reviu/komunikasi.")
        if "scope_stages" in fields:
            sc = fields["scope_stages"] or []
            bad = [s for s in sc if s not in STAGE_KEYS]
            if bad:
                raise HTTPException(status_code=422, detail=f"Tahap tidak dikenal: {', '.join(bad)}")
            fields["scope_stages"] = json.dumps(sc)
        if not fields:
            raise HTTPException(status_code=422, detail="Tidak ada perubahan.")
        sets = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE cases SET {sets} WHERE id=?", [*fields.values(), case_id])
        _event(conn, case_id, user["id"], "rencana", "Memperbarui: " + ", ".join(fields.keys()))
        return _case_detail(conn, case_id)


@router.post("/cases/{case_id}/program/generate")
def generate_program(case_id: int, user: dict = Depends(require_role("auditor"))):
    """Bangkitkan prosedur dari atribut/sinyal paket. Menggantikan prosedur otomatis yang belum diuji; prosedur manual dipertahankan."""
    pkg = None
    with db() as conn:
        case = _case_or_404(conn, case_id)
        _require_phase(case, "perencanaan", what="membangkitkan program audit")
        scope = _loads(case["scope_stages"], DEFAULT_SCOPE)
        tested = conn.execute("SELECT COUNT(*) FROM procedures WHERE case_id=? AND custom=0 AND status<>'belum'", (case_id,)).fetchone()[0]
        if tested:
            raise HTTPException(status_code=409, detail="Program tidak dapat dibangkitkan ulang karena sudah ada hasil pengujian.")
        package_id = case["package_id"]
    pkg = require_store().fetch_package(package_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan di dataset.")
    procs = build_program(pkg, scope)
    with db() as conn:
        conn.execute("DELETE FROM procedures WHERE case_id=? AND custom=0", (case_id,))
        for p in procs:
            conn.execute(
                """INSERT INTO procedures(case_id,code,stage,title,objective,criteria,evidence_expected,techniques,caution,custom)
                   VALUES (?,?,?,?,?,?,?,?,?,0)""",
                (case_id, p["code"], p["stage"], p["title"], p["objective"], json.dumps(p["criteria"], ensure_ascii=False),
                 json.dumps(p["evidence_expected"], ensure_ascii=False), json.dumps(p["techniques"]), p.get("caution")),
            )
        _event(conn, case_id, user["id"], "program", f"{len(procs)} prosedur dibangkitkan dari sinyal & atribut paket")
        return _case_detail(conn, case_id)


@router.post("/cases/{case_id}/procedures", status_code=201)
def add_procedure(case_id: int, body: ProcedureIn, user: dict = Depends(require_role("auditor"))):
    bad_t = [t for t in body.techniques if t not in TECHNIQUES]
    if bad_t or (body.stage != "lintas" and body.stage not in STAGE_KEYS):
        raise HTTPException(status_code=422, detail="Teknik atau tahap tidak dikenal.")
    with db() as conn:
        case = _case_or_404(conn, case_id)
        _require_phase(case, "perencanaan", "pelaksanaan", what="menambah prosedur")
        n = conn.execute("SELECT COUNT(*) FROM procedures WHERE case_id=? AND custom=1", (case_id,)).fetchone()[0]
        conn.execute(
            """INSERT INTO procedures(case_id,code,stage,title,objective,criteria,evidence_expected,techniques,custom)
               VALUES (?,?,?,?,?,?,?,?,1)""",
            (case_id, f"M-{n + 1}", body.stage, body.title.strip(), body.objective,
             json.dumps([c.model_dump() for c in body.criteria], ensure_ascii=False), "[]", json.dumps(body.techniques)),
        )
        _event(conn, case_id, user["id"], "program", f"Prosedur manual: {body.title.strip()}")
        return _case_detail(conn, case_id)


@router.put("/procedures/{procedure_id}/result")
def set_result(procedure_id: int, body: ResultIn, user: dict = Depends(require_role("auditor"))):
    if body.status not in ("belum", "sesuai", "tidak_sesuai", "tidak_dapat_diuji"):
        raise HTTPException(status_code=422, detail="Status hasil tidak dikenal.")
    note = (body.result_note or "").strip()
    if body.status in ("tidak_sesuai", "tidak_dapat_diuji") and not note:
        raise HTTPException(status_code=422, detail="Catatan hasil wajib untuk 'tidak sesuai' atau 'tidak dapat diuji'.")
    with db() as conn:
        p = conn.execute("SELECT * FROM procedures WHERE id=?", (procedure_id,)).fetchone()
        if not p:
            raise HTTPException(status_code=404, detail="Prosedur tidak ditemukan.")
        case = _case_or_404(conn, p["case_id"])
        _require_phase(case, "pelaksanaan", what="mencatat hasil prosedur")
        conn.execute(
            "UPDATE procedures SET status=?, result_note=?, tested_by=?, tested_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (body.status, note or None, user["id"], procedure_id),
        )
        _event(conn, case["id"], user["id"], "hasil", f"{p['code']} → {body.status}" + (f": {note}" if note else ""))
        return _case_detail(conn, case["id"])


# ── transisi ────────────────────────────────────────────────────────────────
@router.post("/cases/{case_id}/transition")
def transition(case_id: int, body: TransitionIn, user: dict = Depends(current_user)):
    with db() as conn:
        case = _case_or_404(conn, case_id)
        frm, to = case["phase"], body.to
        roles = TRANSITIONS.get((frm, to))
        if roles is None:
            raise HTTPException(status_code=409, detail=f"Transisi {frm} → {to} tidak diizinkan.")
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail=f"Hanya {' / '.join(roles)} yang boleh melakukan transisi ini.")
        note = (body.note or "").strip()
        if (frm, to) in NOTE_REQUIRED and not note:
            raise HTTPException(status_code=422, detail="Catatan/alasan wajib diisi untuk aksi ini.")
        unmet = [g for g in compute_gates(conn, case, to) if g["blocking"] and not g["ok"]]
        if unmet:
            raise HTTPException(status_code=422, detail={"message": "Syarat tahap berikutnya belum terpenuhi.", "unmet": [g["label"] for g in unmet]})
        if to == "dihentikan":
            conn.execute("UPDATE cases SET phase=?, stop_reason=? WHERE id=?", (to, note, case_id))
        elif to == "selesai":
            n = conn.execute("SELECT COUNT(*) FROM findings WHERE case_id=?", (case_id,)).fetchone()[0]
            conn.execute("UPDATE cases SET phase=?, outcome=? WHERE id=?", (to, "dengan_temuan" if n else "tanpa_temuan", case_id))
        else:
            conn.execute("UPDATE cases SET phase=? WHERE id=?", (to, case_id))
        _event(conn, case_id, user["id"], "status", note or None, frm, to)
        return _case_detail(conn, case_id)


@router.post("/cases/{case_id}/notes", status_code=201)
def add_note(case_id: int, body: NoteIn, user: dict = Depends(current_user)):
    with db() as conn:
        _case_or_404(conn, case_id)
        _event(conn, case_id, user["id"], "catatan", body.body.strip())
        return _case_detail(conn, case_id)


# ── bukti ───────────────────────────────────────────────────────────────────
def _safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name)[:100] or "file"


def _b(v: str | None) -> bool:
    return str(v).strip().lower() in ("1", "true", "on", "yes", "ya")


@router.post("/cases/{case_id}/evidence", status_code=201)
async def add_evidence(
    case_id: int,
    title: str = Form(..., min_length=2, max_length=160),
    url: str | None = Form(default=None, max_length=500),
    procedure_id: int | None = Form(default=None),
    form: str = Form(default="catatan_transaksi"),
    technique: str = Form(default="inspeksi"),
    origin: str = Form(default="entitas"),
    doc_date: str | None = Form(default=None, max_length=20),
    relevan: str | None = Form(default=None),
    valid: str | None = Form(default=None),
    andal: str | None = Form(default=None),
    authenticity_concern: str | None = Form(default=None),
    authenticity_note: str | None = Form(default=None, max_length=1000),
    file: UploadFile | None = File(default=None),
    user: dict = Depends(require_role("auditor")),
):
    if form not in EVIDENCE_FORMS or technique not in TECHNIQUES or origin not in SOURCE_ORIGINS:
        raise HTTPException(status_code=422, detail="Bentuk, teknik, atau asal bukti tidak dikenal.")
    concern = _b(authenticity_concern)
    if concern and not (authenticity_note or "").strip():
        raise HTTPException(status_code=422, detail="Jelaskan alasan dokumen diragukan keasliannya.")
    has_file = file is not None and bool(file.filename)
    has_url = bool(url and url.strip())
    if has_file == has_url:
        raise HTTPException(status_code=422, detail="Isi tepat satu: tautan ATAU berkas.")

    with db() as conn:
        case = _case_or_404(conn, case_id)
        _require_phase(case, "perencanaan", "pelaksanaan", what="menambah bukti")
        if procedure_id is not None:
            if not conn.execute("SELECT 1 FROM procedures WHERE id=? AND case_id=?", (procedure_id, case_id)).fetchone():
                raise HTTPException(status_code=422, detail="Prosedur tidak termasuk penugasan ini.")

    values: dict = {"kind": "link", "url": None, "filename": None, "stored": None, "mime": None, "size": None, "sha": None}
    if has_url:
        u = url.strip()
        parsed = urlparse(u)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise HTTPException(status_code=422, detail="Tautan harus diawali http:// atau https://")
        values["url"] = u
    else:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            raise HTTPException(status_code=415, detail=f"Tipe berkas tidak diizinkan. Boleh: {', '.join(sorted(ALLOWED_EXT))}")
        data = await file.read(MAX_UPLOAD + 1)
        if len(data) > MAX_UPLOAD:
            raise HTTPException(status_code=413, detail="Berkas melebihi 5 MB.")
        if not data:
            raise HTTPException(status_code=422, detail="Berkas kosong.")
        magic = ALLOWED_MAGIC.get(ext)
        if magic and not data.startswith(magic):
            raise HTTPException(status_code=415, detail="Isi berkas tidak sesuai ekstensinya.")
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        stored = f"{uuid.uuid4().hex}{ext}"
        (UPLOAD_DIR / stored).write_bytes(data)
        values.update(kind="file", filename=_safe_name(file.filename), stored=stored, mime=file.content_type, size=len(data),
                      sha=hashlib.sha256(data).hexdigest())

    with db() as conn:
        conn.execute(
            """INSERT INTO evidence(case_id,procedure_id,kind,title,url,filename,stored_name,mime,size_bytes,sha256,form,technique,origin,
                                   doc_date,relevan,valid,andal,authenticity_concern,authenticity_note,added_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (case_id, procedure_id, values["kind"], title.strip(), values["url"], values["filename"], values["stored"], values["mime"],
             values["size"], values["sha"], form, technique, origin, (doc_date or None), int(_b(relevan)), int(_b(valid)), int(_b(andal)),
             int(concern), (authenticity_note or None), user["id"]),
        )
        _event(conn, case_id, user["id"], "bukti", f"{values['kind']}: {title.strip()}" + (" (diragukan keasliannya)" if concern else ""))
        return _case_detail(conn, case_id)


@router.put("/evidence/{evidence_id}/quality")
def set_quality(evidence_id: int, body: QualityIn, user: dict = Depends(require_role("auditor"))):
    if body.authenticity_concern and not (body.authenticity_note or "").strip():
        raise HTTPException(status_code=422, detail="Jelaskan alasan dokumen diragukan keasliannya.")
    with db() as conn:
        ev = conn.execute("SELECT * FROM evidence WHERE id=?", (evidence_id,)).fetchone()
        if not ev:
            raise HTTPException(status_code=404, detail="Bukti tidak ditemukan.")
        case = _case_or_404(conn, ev["case_id"])
        _require_phase(case, "perencanaan", "pelaksanaan", what="menilai kualitas bukti")
        conn.execute(
            "UPDATE evidence SET relevan=?, valid=?, andal=?, authenticity_concern=?, authenticity_note=? WHERE id=?",
            (int(body.relevan), int(body.valid), int(body.andal), int(body.authenticity_concern), body.authenticity_note, evidence_id),
        )
        _event(conn, ev["case_id"], user["id"], "kualitas_bukti", f"{ev['title']}: relevan={body.relevan}, valid={body.valid}, andal={body.andal}")
        return _case_detail(conn, ev["case_id"])


@router.post("/evidence/{evidence_id}/review")
def review_evidence(evidence_id: int, body: ReviewIn, user: dict = Depends(require_role("reviewer"))):
    if body.decision not in ("verified", "rejected"):
        raise HTTPException(status_code=422, detail="decision harus 'verified' atau 'rejected'.")
    note = (body.note or "").strip()
    if body.decision == "rejected" and not note:
        raise HTTPException(status_code=422, detail="Alasan penolakan wajib diisi.")
    with db() as conn:
        ev = conn.execute("SELECT e.*, c.phase AS case_phase FROM evidence e JOIN cases c ON c.id=e.case_id WHERE e.id=?", (evidence_id,)).fetchone()
        if not ev:
            raise HTTPException(status_code=404, detail="Bukti tidak ditemukan.")
        if ev["added_by"] == user["id"]:
            raise HTTPException(status_code=403, detail="Tidak boleh meninjau bukti yang Anda unggah sendiri.")
        if ev["case_phase"] != "reviu":
            raise HTTPException(status_code=409, detail="Bukti hanya dapat ditinjau pada tahap reviu.")
        conn.execute(
            """UPDATE evidence SET review_status=?, reviewed_by=?, review_note=?,
               reviewed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?""",
            (body.decision, user["id"], note or None, evidence_id),
        )
        _event(conn, ev["case_id"], user["id"], "tinjau_bukti", f"{ev['title']} → {body.decision}" + (f" ({note})" if note else ""))
        return _case_detail(conn, ev["case_id"])


@router.get("/evidence/{evidence_id}/file")
def download_evidence(evidence_id: int, user: dict = Depends(current_user)):
    with db() as conn:
        ev = conn.execute("SELECT * FROM evidence WHERE id=? AND kind='file'", (evidence_id,)).fetchone()
    if not ev:
        raise HTTPException(status_code=404, detail="Berkas tidak ditemukan.")
    path = (UPLOAD_DIR / ev["stored_name"]).resolve()
    if UPLOAD_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="Berkas tidak ada di penyimpanan.")
    return FileResponse(path, filename=ev["filename"], media_type="application/octet-stream", headers={"X-Content-Type-Options": "nosniff"})


# ── temuan ──────────────────────────────────────────────────────────────────
def _validate_finding(conn, case_id: int, body: FindingIn) -> None:
    if body.rekomendasi and not (body.rekomendasi_kepada or "").strip():
        raise HTTPException(status_code=422, detail="Rekomendasi harus menyebut pihak yang bertanggung jawab (SPKN Pelaporan par. 24).")
    if body.procedure_id is not None and not conn.execute("SELECT 1 FROM procedures WHERE id=? AND case_id=?", (body.procedure_id, case_id)).fetchone():
        raise HTTPException(status_code=422, detail="Prosedur tidak termasuk penugasan ini.")
    for eid in body.evidence_ids:
        if not conn.execute("SELECT 1 FROM evidence WHERE id=? AND case_id=?", (eid, case_id)).fetchone():
            raise HTTPException(status_code=422, detail=f"Bukti #{eid} tidak termasuk penugasan ini.")


@router.post("/cases/{case_id}/findings", status_code=201)
def add_finding(case_id: int, body: FindingIn, user: dict = Depends(require_role("auditor"))):
    with db() as conn:
        case = _case_or_404(conn, case_id)
        _require_phase(case, "pelaksanaan", what="menyusun temuan")
        _validate_finding(conn, case_id, body)
        cur = conn.execute(
            """INSERT INTO findings(case_id,procedure_id,title,kondisi,kriteria,kriteria_sumber,sebab,akibat,nilai_potensi,
                                    rekomendasi,rekomendasi_kepada,indikasi_kecurangan,created_by)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (case_id, body.procedure_id, body.title.strip(), body.kondisi.strip(), body.kriteria.strip(), body.kriteria_sumber.strip(),
             body.sebab, body.akibat, body.nilai_potensi, body.rekomendasi, (body.rekomendasi_kepada or None),
             int(body.indikasi_kecurangan), user["id"]),
        )
        fid = cur.lastrowid
        for eid in set(body.evidence_ids):
            conn.execute("INSERT INTO finding_evidence(finding_id,evidence_id) VALUES (?,?)", (fid, eid))
        _event(conn, case_id, user["id"], "temuan", body.title.strip() + (" [indikasi kecurangan]" if body.indikasi_kecurangan else ""))
        return _case_detail(conn, case_id)


@router.put("/findings/{finding_id}")
def update_finding(finding_id: int, body: FindingIn, user: dict = Depends(require_role("auditor"))):
    with db() as conn:
        f = conn.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        if not f:
            raise HTTPException(status_code=404, detail="Temuan tidak ditemukan.")
        case = _case_or_404(conn, f["case_id"])
        _require_phase(case, "pelaksanaan", what="mengubah temuan")
        _validate_finding(conn, f["case_id"], body)
        conn.execute(
            """UPDATE findings SET procedure_id=?,title=?,kondisi=?,kriteria=?,kriteria_sumber=?,sebab=?,akibat=?,nilai_potensi=?,
                                   rekomendasi=?,rekomendasi_kepada=?,indikasi_kecurangan=? WHERE id=?""",
            (body.procedure_id, body.title.strip(), body.kondisi.strip(), body.kriteria.strip(), body.kriteria_sumber.strip(), body.sebab,
             body.akibat, body.nilai_potensi, body.rekomendasi, body.rekomendasi_kepada or None, int(body.indikasi_kecurangan), finding_id),
        )
        conn.execute("DELETE FROM finding_evidence WHERE finding_id=?", (finding_id,))
        for eid in set(body.evidence_ids):
            conn.execute("INSERT INTO finding_evidence(finding_id,evidence_id) VALUES (?,?)", (finding_id, eid))
        _event(conn, f["case_id"], user["id"], "temuan", f"Diubah: {body.title.strip()}")
        return _case_detail(conn, f["case_id"])


@router.put("/findings/{finding_id}/response")
def record_response(finding_id: int, body: ResponseIn, user: dict = Depends(require_role("auditor"))):
    if body.tanggapan_status not in TANGGAPAN:
        raise HTTPException(status_code=422, detail="Status tanggapan tidak dikenal.")
    text = (body.tanggapan or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Isi tanggapan atau alasan 'tidak ada tanggapan' wajib dicatat (SPKN Pelaporan par. 28).")
    with db() as conn:
        f = conn.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        if not f:
            raise HTTPException(status_code=404, detail="Temuan tidak ditemukan.")
        case = _case_or_404(conn, f["case_id"])
        _require_phase(case, "komunikasi", what="mencatat tanggapan entitas")
        conn.execute(
            "UPDATE findings SET tanggapan_status=?, tanggapan=?, tanggapan_by=?, tanggapan_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (body.tanggapan_status, text, user["id"], finding_id),
        )
        _event(conn, f["case_id"], user["id"], "tanggapan", f"Temuan #{finding_id}: {body.tanggapan_status}")
        return _case_detail(conn, f["case_id"])


@router.put("/findings/{finding_id}/followup")
def record_followup(finding_id: int, body: FollowupIn, user: dict = Depends(current_user)):
    if body.tl_status not in TL_STATUS:
        raise HTTPException(status_code=422, detail="Status tindak lanjut tidak dikenal.")
    note = (body.tl_note or "").strip()
    if body.tl_status != "belum" and not note:
        raise HTTPException(status_code=422, detail="Catatan/bukti tindak lanjut wajib diisi.")
    with db() as conn:
        f = conn.execute("SELECT * FROM findings WHERE id=?", (finding_id,)).fetchone()
        if not f:
            raise HTTPException(status_code=404, detail="Temuan tidak ditemukan.")
        if not f["rekomendasi"]:
            raise HTTPException(status_code=409, detail="Temuan ini tidak memiliki rekomendasi untuk dipantau.")
        case = _case_or_404(conn, f["case_id"])
        _require_phase(case, "selesai", what="memantau tindak lanjut")
        conn.execute(
            "UPDATE findings SET tl_status=?, tl_note=?, tl_by=?, tl_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (body.tl_status, note or None, user["id"], finding_id),
        )
        _event(conn, f["case_id"], user["id"], "tindak_lanjut", f"Temuan #{finding_id}: {body.tl_status}")
        return _case_detail(conn, f["case_id"])
