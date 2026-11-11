"""Alur penugasan audit end-to-end (SQLite sementara, tanpa dataset). Model: docs/RISET_PROSES_AUDIT.md."""

import pytest
from fastapi.testclient import TestClient

BASE = dict(paket="Pengadaan Uji", lembaga="Kementerian X", RPI=72.5, risk_label="KRITIS", pagu=350_000_000.0,
            jenisPengadaan="Pekerjaan Konstruksi", metode="Pengadaan Langsung", isUMKM=True, dalamNegeri=True,
            s1_metode=0.8, s2_pagu_anomali=0.7, s3_fragmentasi=0.9, s4_konsentrasi=0.2, s5_umkm=0.1, s6_dana_metode=0.1, s7_reputasi=0.3)


class FakeStore:
    def fetch_package(self, pid):
        return None if pid == 404 else dict(BASE, id=pid)


@pytest.fixture
def client(tmp_path, monkeypatch):
    from api import appdb, auth
    from api.routers import cases

    monkeypatch.setenv("AUDITRA_SECRET", "test-secret")
    monkeypatch.setattr(appdb, "APP_DB_PATH", tmp_path / "t.sqlite")
    monkeypatch.setattr(appdb, "_ready_for", None)
    monkeypatch.setattr(cases, "UPLOAD_DIR", tmp_path / "up")
    monkeypatch.setattr(cases, "require_store", lambda: FakeStore())
    auth.reset_rate_limits()
    auth.seed_demo_users()
    from api.main import app

    return TestClient(app)


def login(c, who):
    r = c.post("/api/auth/login", json={"email": f"{who}@auditra.demo", "password": "auditra2026"})
    assert r.status_code == 200, r.text
    return {"Authorization": "Bearer " + r.json()["token"]}


@pytest.fixture
def H(client):
    return login(client, "auditor"), login(client, "reviewer")


def go(c, cid, to, h, note=None, expect=200):
    r = c.post(f"/api/cases/{cid}/transition", json={"to": to, "note": note}, headers=h)
    assert r.status_code == expect, (to, r.status_code, r.text)
    return r.json()


def unmet(body):
    return body["detail"]["unmet"]


def plan_ready(c, cid, a):
    r = c.put(f"/api/cases/{cid}/plan", json={
        "objective": "Menguji kepatuhan pemilihan dan indikasi pemecahan paket.",
        "materiality_note": "Kuantitatif: pagu Rp350 jt mendekati batas PL; kualitatif: perhatian publik.",
        "risk_note": "Risiko bawaan tinggi; risiko kecurangan: pemecahan paket."}, headers=a)
    assert r.status_code == 200, r.text
    r = c.post(f"/api/cases/{cid}/program/generate", headers=a)
    assert r.status_code == 200, r.text
    return r.json()


def evid(c, cid, a, procedure_id, title="Dokumen", **extra):
    data = {"title": title, "url": "https://example.org/d.pdf", "procedure_id": str(procedure_id),
            "form": "catatan_transaksi", "technique": "inspeksi", "origin": "entitas", **extra}
    r = c.post(f"/api/cases/{cid}/evidence", data=data, headers=a)
    assert r.status_code == 201, r.text
    return r.json()


def test_requires_auth(client):
    assert client.get("/api/cases").status_code == 401
    assert client.get("/api/cases", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_register_always_auditor_login_rate_limit(client):
    r = client.post("/api/auth/register", json={"name": "Budi", "email": "budi@x.id", "password": "longenough1", "role": "reviewer"})
    assert r.status_code == 201 and r.json()["user"]["role"] == "auditor"
    for _ in range(8):
        assert client.post("/api/auth/login", json={"email": "x@y.z", "password": "no"}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "x@y.z", "password": "no"}).status_code == 429


def test_selection_gate_and_duplicate_rule(client, H):
    a, r = H
    assert client.post("/api/cases", json={"package_id": 1}, headers=r).status_code == 403
    assert client.post("/api/cases", json={"package_id": 404}, headers=a).status_code == 404
    case = client.post("/api/cases", json={"package_id": 1}, headers=a).json()
    cid = case["id"]
    assert case["phase"] == "seleksi" and case["metode"] == "Pengadaan Langsung"
    dup = client.post("/api/cases", json={"package_id": 1}, headers=a)
    assert dup.status_code == 409 and dup.json()["detail"]["case_id"] == cid
    # gerbang yang benar secara vakum tidak boleh tampil sebagai centang: ditandai 'na'
    plan_case = client.get(f"/api/cases/{cid}", headers=a).json()
    assert plan_case["transitions"][0]["gates"][0]["na"] is False
    # gerbang: alasan seleksi wajib
    assert "Alasan seleksi" in unmet(go(client, cid, "perencanaan", a, expect=422))[0]
    client.put(f"/api/cases/{cid}/plan", json={"selection_reason": "RPI kritis; pagu mendekati batas pengadaan langsung."}, headers=a)
    assert go(client, cid, "perencanaan", a)["phase"] == "perencanaan"
    # tidak boleh loncat / reviewer tak boleh memulai
    go(client, cid, "selesai", r, expect=409)
    go(client, cid, "reviu", a, expect=409)


def test_program_is_criteria_aware(client, H):
    a, _ = H
    cid = client.post("/api/cases", json={"package_id": 2, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    case = plan_ready(client, cid, a)
    codes = {p["code"]: p for p in case["procedures"]}
    assert {"P-RUP", "P-PEMAKETAN", "P-HPS", "P-MET-PL", "P-RF"} <= codes.keys()
    pl = codes["P-MET-PL"]
    assert "Rp400.000.000" in " ".join(c["text"] for c in pl["criteria"])   # konstruksi 400 jt (Perpres 46/2025)
    assert "Rp 400.000.000" in pl["objective"] and "MELEBIHI" not in pl["objective"]
    assert all(c["ref"] for p in case["procedures"] for c in p["criteria"])  # tiap kriteria bersumber
    assert codes["P-PEMAKETAN"]["caution"] and "maksud" in codes["P-PEMAKETAN"]["caution"]
    assert "Pasal 26(6)" in " ".join(c["ref"] for c in codes["P-HPS"]["criteria"])
    # lingkup memengaruhi program
    client.put(f"/api/cases/{cid}/plan", json={"scope_stages": ["perencanaan", "serah_terima"]}, headers=a)
    codes2 = {p["code"] for p in client.post(f"/api/cases/{cid}/program/generate", headers=a).json()["procedures"]}
    assert "P-BAST" in codes2 and "P-MET-PL" not in codes2
    assert client.put(f"/api/cases/{cid}/plan", json={"scope_stages": ["ngawur"]}, headers=a).status_code == 422


def test_planning_gates_block_execution(client, H):
    a, _ = H
    cid = client.post("/api/cases", json={"package_id": 3, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    labels = " | ".join(unmet(go(client, cid, "pelaksanaan", a, expect=422)))
    assert all(k in labels for k in ("Tujuan", "risiko", "materialitas", "Program"))
    plan_ready(client, cid, a)
    assert go(client, cid, "pelaksanaan", a)["phase"] == "pelaksanaan"


def test_full_audit_cycle_with_findings(client, H):
    a, r = H
    cid = client.post("/api/cases", json={"package_id": 5, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    case = plan_ready(client, cid, a)
    go(client, cid, "pelaksanaan", a)
    procs = {p["code"]: p["id"] for p in case["procedures"]}

    # belum ada hasil → tidak bisa ke reviu
    assert any("memiliki hasil" in u for u in unmet(go(client, cid, "reviu", a, expect=422)))
    # hasil 'tidak sesuai' wajib catatan
    assert client.put(f"/api/procedures/{procs['P-PEMAKETAN']}/result", json={"status": "tidak_sesuai"}, headers=a).status_code == 422
    # reviewer tidak boleh mencatat hasil / bukti / temuan
    assert client.put(f"/api/procedures/{procs['P-RUP']}/result", json={"status": "sesuai"}, headers=r).status_code == 403
    assert client.post(f"/api/cases/{cid}/evidence", data={"title": "x", "url": "https://a.b"}, headers=r).status_code == 403

    # bukti: validasi enumerasi, tautan, berkas palsu
    bad = client.post(f"/api/cases/{cid}/evidence", data={"title": "x", "url": "javascript:alert(1)"}, headers=a)
    assert bad.status_code == 422
    assert client.post(f"/api/cases/{cid}/evidence", data={"title": "x", "url": "https://a.b", "form": "ngawur"}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/evidence", data={"title": "x", "url": "https://a.b", "procedure_id": "99999"}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/evidence", data={"title": "x", "url": "https://a.b", "authenticity_concern": "true"}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/evidence", data={"title": "pdf palsu"}, files={"file": ("a.pdf", b"bukan pdf", "application/pdf")}, headers=a).status_code == 415
    e1 = evid(client, cid, a, procs["P-PEMAKETAN"], "Daftar paket serupa")
    pdf = client.post(f"/api/cases/{cid}/evidence", data={"title": "Scan", "procedure_id": str(procs["P-RUP"]), "technique": "inspeksi", "origin": "entitas", "form": "catatan_transaksi"},
                      files={"file": ("rup.pdf", b"%PDF-1.4 x", "application/pdf")}, headers=a)
    assert pdf.status_code == 201 and pdf.json()["evidence"][1]["sha256"]
    ev_ids = [e["id"] for e in pdf.json()["evidence"]]

    # temuan: kondisi+kriteria+sumber wajib; rekomendasi wajib menyebut pihak
    f = dict(title="Indikasi pemecahan paket", procedure_id=procs["P-PEMAKETAN"], kondisi="Tiga paket serupa di satker sama tepat di bawah batas.",
             kriteria="Dilarang memecah paket dengan maksud menghindari tender.", kriteria_sumber="Perpres 16/2018 jo. 46/2025 Pasal 20(2)(d)",
             rekomendasi="Evaluasi pemaketan.", evidence_ids=[ev_ids[0]])
    assert client.post(f"/api/cases/{cid}/findings", json={**f, "kondisi": "x"}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/findings", json=f, headers=a).status_code == 422   # rekomendasi tanpa pihak
    assert client.post(f"/api/cases/{cid}/findings", json={**f, "rekomendasi_kepada": "PA", "evidence_ids": [99999]}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/findings", json={**f, "rekomendasi_kepada": "PA"}, headers=r).status_code == 403
    fin = client.post(f"/api/cases/{cid}/findings", json={**f, "rekomendasi_kepada": "Pengguna Anggaran", "indikasi_kecurangan": True}, headers=a)
    assert fin.status_code == 201 and fin.json()["advisories"][0]["key"] == "kecurangan"
    fid = fin.json()["findings"][0]["id"]

    # semua prosedur diberi hasil
    assert client.put(f"/api/procedures/{procs['P-PEMAKETAN']}/result", json={"status": "tidak_sesuai", "result_note": "Pola terbukti"}, headers=a).status_code == 200
    for code, pid in procs.items():
        if code == "P-PEMAKETAN":
            continue
        if code == "P-RUP":
            client.put(f"/api/procedures/{pid}/result", json={"status": "sesuai"}, headers=a)
        else:
            assert client.put(f"/api/procedures/{pid}/result", json={"status": "tidak_dapat_diuji"}, headers=a).status_code == 422  # alasan wajib
            client.put(f"/api/procedures/{pid}/result", json={"status": "tidak_dapat_diuji", "result_note": "Dokumen belum diserahkan entitas"}, headers=a)
    # kualitas bukti belum dinilai → terblokir
    assert any("relevan, valid, dan andal" in u for u in unmet(go(client, cid, "reviu", a, expect=422)))
    for eid in ev_ids:
        assert client.put(f"/api/evidence/{eid}/quality", json={"relevan": True, "valid": True, "andal": True}, headers=a).status_code == 200
    # bukti P-RUP sudah ada; sisanya 'tidak dapat diuji' tak butuh bukti
    assert go(client, cid, "reviu", a)["phase"] == "reviu"

    # pelaksana tidak boleh mengubah lagi; reviewer meninjau bukti
    assert client.put(f"/api/procedures/{procs['P-RUP']}/result", json={"status": "sesuai"}, headers=a).status_code == 409
    assert client.post(f"/api/evidence/{ev_ids[0]}/review", json={"decision": "verified"}, headers=a).status_code == 403
    assert any("ditinjau" in u for u in unmet(go(client, cid, "komunikasi", r, expect=422)))
    assert client.post(f"/api/evidence/{ev_ids[0]}/review", json={"decision": "rejected"}, headers=r).status_code == 422
    for eid in ev_ids:
        assert client.post(f"/api/evidence/{eid}/review", json={"decision": "verified", "note": "sesuai"}, headers=r).status_code == 200

    # dikembalikan wajib catatan; lalu lanjut
    go(client, cid, "pelaksanaan", r, expect=422)
    assert go(client, cid, "komunikasi", r)["phase"] == "komunikasi"

    # komunikasi: tanggapan tertulis wajib sebelum selesai; kesimpulan wajib
    assert client.put(f"/api/findings/{fid}/response", json={"tanggapan_status": "diterima"}, headers=a).status_code == 422
    assert any("Tanggapan" in u for u in unmet(go(client, cid, "selesai", r, expect=422)))
    assert client.put(f"/api/findings/{fid}/response", json={"tanggapan_status": "diterima_sebagian", "tanggapan": "Sebagian setuju; paket dipisah karena lokasi berbeda."}, headers=a).status_code == 200
    assert any("Kesimpulan" in u for u in unmet(go(client, cid, "selesai", r, expect=422)))
    client.put(f"/api/cases/{cid}/plan", json={"conclusion": "Terdapat 1 temuan ketidakpatuhan pemaketan."}, headers=r)
    done = go(client, cid, "selesai", r)
    assert done["phase"] == "selesai" and done["outcome"] == "dengan_temuan"

    # pemantauan tindak lanjut hanya setelah selesai; 'sesuai' wajib catatan
    assert client.put(f"/api/findings/{fid}/followup", json={"tl_status": "sesuai"}, headers=a).status_code == 422
    out = client.put(f"/api/findings/{fid}/followup", json={"tl_status": "dalam_proses", "tl_note": "PA menerbitkan nota dinas perbaikan."}, headers=a).json()
    assert out["findings"][0]["tl_status"] == "dalam_proses"
    go(client, cid, "pelaksanaan", r, "x", expect=409)  # terminal
    types = [e["type"] for e in out["events"]]
    assert types[0] == "dibuat" and {"rencana", "program", "hasil", "bukti", "temuan", "tinjau_bukti", "tanggapan", "tindak_lanjut"} <= set(types)


def test_rejected_evidence_blocks_finding_and_return_flow(client, H):
    a, r = H
    cid = client.post("/api/cases", json={"package_id": 6, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    case = plan_ready(client, cid, a)
    go(client, cid, "pelaksanaan", a)
    procs = {p["code"]: p["id"] for p in case["procedures"]}
    ev = evid(client, cid, a, procs["P-PEMAKETAN"], "Satu-satunya bukti", relevan="true", valid="true", andal="true")["evidence"][0]
    client.post(f"/api/cases/{cid}/findings", json=dict(title="Temuan", procedure_id=procs["P-PEMAKETAN"], kondisi="Kondisi cukup jelas.", kriteria="Kriteria cukup jelas.",
                kriteria_sumber="Perpres Pasal 20(2)(d)", evidence_ids=[ev["id"]]), headers=a)
    client.put(f"/api/procedures/{procs['P-PEMAKETAN']}/result", json={"status": "tidak_sesuai", "result_note": "n"}, headers=a)
    for code, pid in procs.items():
        if code != "P-PEMAKETAN":
            client.put(f"/api/procedures/{pid}/result", json={"status": "tidak_dapat_diuji", "result_note": "belum ada dokumen"}, headers=a)
    go(client, cid, "reviu", a)
    client.post(f"/api/evidence/{ev['id']}/review", json={"decision": "rejected", "note": "dokumen tidak valid"}, headers=r)
    assert any("didukung" in u for u in unmet(go(client, cid, "komunikasi", r, expect=422)))
    back = go(client, cid, "pelaksanaan", r, "Bukti ditolak, lengkapi pembanding independen.")
    assert back["phase"] == "pelaksanaan"


def test_clean_audit_without_findings_and_stop(client, H):
    a, r = H
    cid = client.post("/api/cases", json={"package_id": 7, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    case = plan_ready(client, cid, a)
    go(client, cid, "pelaksanaan", a)
    for p in case["procedures"]:
        evid(client, cid, a, p["id"], p["code"], relevan="true", valid="true", andal="true")
        client.put(f"/api/procedures/{p['id']}/result", json={"status": "sesuai"}, headers=a)
    go(client, cid, "reviu", a)
    for e in client.get(f"/api/cases/{cid}", headers=r).json()["evidence"]:
        client.post(f"/api/evidence/{e['id']}/review", json={"decision": "verified"}, headers=r)
    assert any("Kesimpulan" in u for u in unmet(go(client, cid, "selesai", r, expect=422)))
    client.put(f"/api/cases/{cid}/plan", json={"conclusion": "Tidak ditemukan ketidaksesuaian atas prosedur yang diuji."}, headers=r)
    assert go(client, cid, "selesai", r)["outcome"] == "tanpa_temuan"

    cid2 = client.post("/api/cases", json={"package_id": 8}, headers=a).json()["id"]
    go(client, cid2, "dihentikan", a, expect=422)   # alasan wajib
    stopped = go(client, cid2, "dihentikan", a, "Entitas tidak menyediakan akses data.")
    assert stopped["phase"] == "dihentikan" and stopped["stop_reason"]
    assert client.post("/api/cases", json={"package_id": 8}, headers=a).status_code == 201  # boleh dibuka lagi


def test_manual_procedure_and_notes(client, H):
    a, r = H
    cid = client.post("/api/cases", json={"package_id": 9, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    ok = client.post(f"/api/cases/{cid}/procedures", json={"title": "Uji konfirmasi penyedia", "criteria": [{"ref": "SPKN Pelaksanaan par. 32", "text": "Konfirmasi ke pihak ketiga."}], "techniques": ["konfirmasi"]}, headers=a)
    assert ok.status_code == 201 and ok.json()["procedures"][0]["code"] == "M-1"
    assert client.post(f"/api/cases/{cid}/procedures", json={"title": "x y z", "criteria": []}, headers=a).status_code == 422
    assert client.post(f"/api/cases/{cid}/notes", json={"body": "catatan"}, headers=r).status_code == 201
    assert client.post(f"/api/cases/{cid}/program/generate", headers=a).json()["procedures"][0]["code"] != "x"  # manual dipertahankan
    assert any(p["custom"] for p in client.get(f"/api/cases/{cid}", headers=a).json()["procedures"])


def test_schema_migration_backs_up_old_database(tmp_path, monkeypatch):
    import sqlite3

    from api import appdb

    old = tmp_path / "old.sqlite"
    c = sqlite3.connect(old)
    c.execute("CREATE TABLE cases (id INTEGER, status TEXT)")
    c.execute("INSERT INTO cases VALUES (1, 'baru')")
    c.commit(); c.close()
    monkeypatch.setattr(appdb, "APP_DB_PATH", old)
    monkeypatch.setattr(appdb, "_ready_for", None)
    appdb.init_db()
    assert list(tmp_path.glob("old.v0*.bak")), "berkas lama harus dicadangkan, bukan dihapus"
    n = sqlite3.connect(old)
    assert n.execute("PRAGMA user_version").fetchone()[0] == appdb.SCHEMA_VERSION
    assert n.execute("SELECT COUNT(*) FROM procedures").fetchone()[0] == 0


def test_vacuous_gates_are_marked_not_applicable(client, H):
    a, _ = H
    cid = client.post("/api/cases", json={"package_id": 21, "selection_reason": "alasan seleksi cukup panjang"}, headers=a).json()["id"]
    go(client, cid, "perencanaan", a)
    plan_ready(client, cid, a)
    case = go(client, cid, "pelaksanaan", a)
    gates = {g["key"]: g for g in next(t for t in case["transitions"] if t["to"] == "reviu")["gates"]}
    assert gates["prosedur"]["ok"] is False and gates["prosedur"]["na"] is False
    for k in ("bukti_hasil", "tdu", "temuan_dari_ketidaksesuaian", "temuan_bukti", "kualitas_bukti"):
        assert gates[k]["ok"] is True and gates[k]["na"] is True, k
