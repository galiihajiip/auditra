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
                         idMetode=rnd.randint(1, 12), idJenisPengadaan=rnd.randint(1, 5))); i += 1
    for _ in range(13000):  # satu nilai pagu yang sangat dominan (> 2 halaman)
        rows.append(dict(id=i, pagu=100_000_000, idBulan=rnd.randint(1, 12),
                         idMetode=rnd.randint(1, 12), idJenisPengadaan=rnd.randint(1, 5))); i += 1
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
