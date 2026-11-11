from api.audit_program import DEFAULT_SCOPE, STAGE_KEYS, build_program, pl_limit_for


def pkg(**kw):
    base = dict(metode="Tender", jenisPengadaan="Barang", pagu=500_000_000, isUMKM=False, dalamNegeri=True,
                s1_metode=0, s2_pagu_anomali=0, s3_fragmentasi=0, s4_konsentrasi=0, s5_umkm=0, s6_dana_metode=0, s7_reputasi=0)
    base.update(kw)
    return base


def codes(**kw):
    scope = kw.pop("scope", None)
    return {p["code"]: p for p in build_program(pkg(**kw), scope)}


def test_thresholds_follow_perpres_46_2025():
    assert pl_limit_for("Barang") == 200_000_000
    assert pl_limit_for("Jasa Lainnya") == 200_000_000
    assert pl_limit_for("Pekerjaan Konstruksi") == 400_000_000
    assert pl_limit_for("Jasa Konsultansi") == 100_000_000
    assert pl_limit_for("???") is None


def test_pengadaan_langsung_flags_over_limit_by_jenis():
    barang = codes(metode="Pengadaan Langsung", jenisPengadaan="Barang", pagu=300_000_000)["P-MET-PL"]
    konst = codes(metode="Pengadaan Langsung", jenisPengadaan="Pekerjaan Konstruksi", pagu=300_000_000)["P-MET-PL"]
    assert "MELEBIHI" in barang["objective"] and "MELEBIHI" not in konst["objective"]


def test_method_specific_criteria_are_cited():
    assert "Pasal 41A" in " ".join(c["ref"] for c in codes(metode="Penunjukan Langsung")["P-MET-PUL"]["criteria"])
    assert any("Pasal 61" in c["ref"] for c in codes(metode="Dikecualikan")["P-MET-KEC"]["criteria"])
    assert "P-MET-DAR" in codes(metode="Darurat") and "P-MET-EP" in codes(metode="E-Purchasing") and "P-MET-TC" in codes(metode="Tender Cepat")


def test_signals_trigger_procedures_and_umk_rule():
    c = codes(s3_fragmentasi=0.9, s2_pagu_anomali=0.8, isUMKM=True, pagu=20_000_000_000)
    assert {"P-PEMAKETAN", "P-HPS", "P-UMK"} <= c.keys()
    assert "15 miliar" in c["P-UMK"]["objective"]
    assert "P-PEMAKETAN" not in codes(s3_fragmentasi=0.2)


def test_scope_selects_stage_procedures_and_everything_has_a_basis():
    full = build_program(pkg(metode="Penunjukan Langsung"), STAGE_KEYS)
    assert {"P-KONTRAK", "P-BAST", "P-MANFAAT"} <= {p["code"] for p in full}
    default = build_program(pkg(), DEFAULT_SCOPE)
    assert "P-BAST" not in {p["code"] for p in default}
    for p in full:
        assert p["criteria"] and all(c["ref"] and c["text"] for c in p["criteria"]), p["code"]
        assert p["evidence_expected"] and all(e["form"] for e in p["evidence_expected"]), p["code"]
