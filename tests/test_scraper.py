"""Uji logika crawler SIRUP dengan situs tiruan (tanpa jaringan)."""

import json
import random

import pytest

from scraper import sirup
from scraper.sirup import Crawler, Node, PAGE_SIZE


class FakeSite:
    """Meniru semantik endpoint: filter inklusif pagu + bulan/metode/jenis, recordsFiltered, halaman."""

    def __init__(self, rows):
        self.rows, self.requests, self.fail_after = rows, 0, None

    delay = 0

    def search(self, node, start=0, length=PAGE_SIZE, order=(5, "desc")):
        self.requests += 1
        if self.fail_after is not None and self.requests > self.fail_after:
            raise KeyboardInterrupt  # simulasi proses dihentikan
        r = self.rows
        if node is not None:
            r = [x for x in r if node.lo <= x["pagu"] <= node.hi
                 and (node.bulan is None or x["idBulan"] == node.bulan)
                 and (node.metode is None or x["idMetode"] == node.metode)
                 and (node.jenis is None or x["idJenisPengadaan"] == node.jenis)]
        r = list(r)
        random.shuffle(r)  # tie dibuat tidak stabil (adversarial)
        key = (lambda x: x.get("paket", "")) if order[0] == 1 else (lambda x: x["idBulan"])
        r.sort(key=key, reverse=(order[1] == "desc"))
        return {"recordsFiltered": len(r), "recordsTotal": len(self.rows), "data": r[start:start + length]}


def make_rows():
    rnd = random.Random(7)
    rows, i = [], 1
    for _ in range(9000):  # sebaran luas
        rows.append(dict(id=i, pagu=int(10 ** rnd.uniform(0, 11)), idBulan=rnd.randint(1, 12),
                         idMetode=rnd.choice([7, 8, 9, 13, 14, 15, 16, 17, 20]), idJenisPengadaan=rnd.choice([0, 1, 2, 3, 4, 6]))); i += 1
    for _ in range(13000):  # satu nilai pagu yang sangat dominan (> 2 halaman)
        rows.append(dict(id=i, pagu=100_000_000, idBulan=rnd.randint(1, 12),
                         idMetode=rnd.choice([7, 8, 9, 13, 14, 15, 16, 17, 20]), idJenisPengadaan=rnd.choice([0, 1, 2, 3, 4, 6]))); i += 1
    return rows


def ids_in(out):
    import gzip
    got = []
    for f in sorted(out.glob("leaf_*.jsonl.gz")):
        with gzip.open(f, "rt") as fh:
            got += [json.loads(l)["id"] for l in fh]
    return got


def test_complete_no_duplicates_no_missing(tmp_path):
    site = FakeSite(make_rows())
    Crawler(tmp_path, site).run(len(site.rows))
    got = ids_in(tmp_path)
    assert len(got) == len(set(got)) == len(site.rows)


def test_resume_continues_without_refetching_done_leaves(tmp_path):
    rows = make_rows()
    first = FakeSite(rows)
    first.fail_after = 60
    with pytest.raises(KeyboardInterrupt):
        Crawler(tmp_path, first).run(len(rows))
    partial = len(ids_in(tmp_path))
    assert 0 < partial < len(rows)

    second = FakeSite(rows)
    Crawler(tmp_path, second).run(len(rows))
    got = ids_in(tmp_path)
    assert len(got) == len(set(got)) == len(rows)
    full = FakeSite(rows)
    Crawler(tmp_path / "fresh", full).run(len(rows))
    assert second.requests < full.requests  # resume menghemat permintaan


def test_unsplittable_node_raises():
    n = Node(5, 5, 1, 1, 1)
    with pytest.raises(RuntimeError):
        sirup._children(n, 9999)


def test_delay_floor_enforced(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["sirup", "crawl", "--out", "x", "--delay", "0.1"])
    with pytest.raises(SystemExit) as e:
        sirup.main()
    assert "0.5" in str(e.value)


def test_dense_leaf_beyond_one_page_is_fetched_completely(tmp_path):
    """5.310 baris dengan pagu/bulan/metode/jenis identik (kasus nyata SIRUP) tak bisa dipecah → fallback padat."""
    rnd = random.Random(3)
    rows = [dict(id=i, pagu=1_000_000, idBulan=1, idMetode=8, idJenisPengadaan=1,
                 paket=f"paket {rnd.randint(0, 5200)}") for i in range(1, 5311)]  # nama ganda → tie
    site = FakeSite(rows)
    Crawler(tmp_path, site).run(len(rows), edges=[1_000_000])
    got = ids_in(tmp_path)
    assert len(got) == len(set(got)) == 5310


def test_dense_leaf_fails_loudly_when_incomplete(tmp_path):
    rows = [dict(id=i, pagu=7, idBulan=1, idMetode=1, idJenisPengadaan=1, paket="sama") for i in range(1, 12001)]

    class Capped(FakeSite):
        def search(self, node, start=0, length=PAGE_SIZE, order=(5, "desc")):
            out = super().search(node, start, length, order)
            out["data"] = out["data"][:100]  # situs "memotong" — jumlah tak pernah cocok
            return out

    with pytest.raises(RuntimeError, match="tak lengkap"):
        Crawler(tmp_path, Capped(rows)).run(len(rows), edges=[7])


def test_regression_metode_ids_are_not_1_to_12(tmp_path):
    """Kesalahan nyata: ID metode SIRUP = 7,8,9,13..17,20 (bukan 1..12). Potongan padat harus lengkap, termasuk 'Dikecualikan' (16)."""
    rnd = random.Random(11)
    rows = [dict(id=i, pagu=2_000_000, idBulan=1, idMetode=rnd.choice([8, 9, 16, 16, 16, 13, 20]),
                 idJenisPengadaan=rnd.choice([1, 4, 0, 6]), paket=f"p{i}") for i in range(1, 30001)]
    site = FakeSite(rows)
    c = Crawler(tmp_path, site)
    c.run(len(rows), edges=[2_000_000])
    got = ids_in(tmp_path)
    assert len(got) == len(set(got)) == 30000
    assert c.deficits() == []


def test_unknown_ids_are_discovered_by_repair(tmp_path):
    """ID metode yang belum pernah dikenal (33) harus ditemukan oleh audit kelengkapan, bukan hilang diam-diam."""
    rnd = random.Random(5)
    rows = [dict(id=i, pagu=7_000_000, idBulan=1, idMetode=rnd.choice([8, 9, 33]), idJenisPengadaan=1, paket=f"p{i}") for i in range(1, 24001)]
    site = FakeSite(rows)
    c = Crawler(tmp_path, site)
    c.run(len(rows), edges=[7_000_000])
    assert len(set(ids_in(tmp_path))) == 24000
    assert c.deficits() == []


def test_deficit_audit_flags_incomplete_split(tmp_path):
    """Audit harus melaporkan node yang jumlah anak-anaknya kurang dari jumlah di situs."""
    from scraper.sirup import Node
    c = Crawler(tmp_path, FakeSite([]))
    parent = Node(5, 5, 1)
    c.done[parent.key()] = {"node": parent.key(), "status": "split", "count": 100}
    kid = Node(5, 5, 1, 8)
    c.done[kid.key()] = {"node": kid.key(), "status": "leaf", "count": 60, "rows": 60, "file": None}
    assert c.deficits() == [(parent.key(), 40)]


def test_negative_and_roundtrip_keys():
    from scraper.sirup import Node, parse_key
    for n in (Node(-10**15, -1), Node(5, 5, 1, -1, 0), Node(0, 999), Node(7, 7, 12, 33, 6)):
        assert parse_key(n.key()) == n


def test_resume_never_overwrites_files_and_check_files_detects_shared(tmp_path):
    """Regresi bug nyata: potongan padat (split→leaf) tidak boleh berbagi nama berkas dengan potongan berikutnya."""
    rnd = random.Random(2)
    rows = [dict(id=i, pagu=1_000_000, idBulan=1, idMetode=8, idJenisPengadaan=rnd.choice([1, 2]), paket=f"p{rnd.randint(0, 4000)}")
            for i in range(1, 5311 + 1)]
    site = FakeSite(rows)
    c = Crawler(tmp_path, site)
    # simulasikan resume: catatan 'split' sudah ada untuk node padat sebelum diganti 'leaf'
    n = Node(1_000_000, 1_000_000, 1, 8, 1)
    n_count = sum(1 for r in rows if r["idJenisPengadaan"] == 1)
    c.done[n.key()] = {"node": n.key(), "status": "split", "count": n_count}
    c.run(len(rows), edges=[1_000_000])
    ids = ids_in(tmp_path)
    assert len(ids) == len(set(ids)) == len(rows)
    files = [r["file"] for r in c.done.values() if r["status"] == "leaf" and r.get("file")]
    assert len(files) == len(set(files))


def test_check_files_invalidates_shared_file(tmp_path):
    import gzip as gz
    c = Crawler(tmp_path, FakeSite([]))
    with gz.open(tmp_path / "leaf_000001.jsonl.gz", "wt") as f:
        f.write('{"id": 1}\n{"id": 2}\n')
    a, b = Node(1, 1, 1, 8, 1), Node(1, 1, 1, 8, 2)
    c.done[a.key()] = {"node": a.key(), "status": "leaf", "count": 5, "rows": 5, "file": "leaf_000001.jsonl.gz"}
    c.done[b.key()] = {"node": b.key(), "status": "leaf", "count": 2, "rows": 2, "file": "leaf_000001.jsonl.gz"}
    assert c.check_files() == 2
    assert c.done[a.key()]["status"] == "invalid" and c.done[b.key()]["status"] == "invalid"
