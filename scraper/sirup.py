"""Client & crawler SIRUP LKPP (endpoint DataTables publik `caripaketctr/search`).

Prinsip:
  * Sopan   — 1 koneksi, jeda antar-permintaan, User-Agent jujur, backoff, dan BERHENTI bila
              situs menolak (403/429 berulang). Tidak ada rotasi IP / penyamaran.
  * Akurat  — ruang data dipecah per rentang pagu (inklusif, bilangan bulat) sehingga tiap
              potongan ≤ PAGE_SIZE baris dan diambil dalam SATU halaman: tanpa offset-paging,
              jadi tidak ada duplikat/baris hilang akibat urutan tak stabil. Potongan satu-nilai
              pagu yang masih terlalu besar dipecah lagi per bulan → metode → jenis pengadaan.
  * Tahan   — manifest JSONL per potongan; proses dapat dihentikan & dilanjutkan.
  * Teruji  — rekonsiliasi akhir: jumlah baris unik vs `recordsTotal` situs.

Pakai:
    python -m scraper.sirup probe
    python -m scraper.sirup crawl --out data/live/2026-11-11 [--delay 1.0]
    python -m scraper.sirup verify --out data/live/2026-11-11
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

BASE = "https://sirup.inaproc.id/sirup/caripaketctr/search"
USER_AGENT = "AuditraResearchBot/1.0 (riset akademik; data publik SIRUP; 1 koneksi)"
PAGE_SIZE = 5000
YEAR = 2026
PAGU_MAX = 10**15

# Pembagi awal (batas bawah tiap ember pagu) agar rekursi tidak mulai dari rentang 0..1e15.
SEED_EDGES = [0, 1]
for _exp in range(3, 14):
    SEED_EDGES += [m * 10**_exp for m in (1, 2, 3, 4, 5, 6, 7, 8, 9)]
SEED_EDGES = sorted(set(SEED_EDGES))

BULAN = list(range(1, 13))
# ID metode/jenis di SIRUP BUKAN 1..12 (kesalahan asumsi awal yang membuat ~47 rb baris hilang).
# Nilai di bawah dari data hasil crawl; ID tak dikenal ditemukan otomatis oleh audit kelengkapan (_repair).
METODE_IDS = [-1, 0, 7, 8, 9, 13, 14, 15, 16, 17, 20]
JENIS_IDS = [0, 1, 2, 3, 4, 5, 6]
PROBE_METODE = [i for i in range(-5, 60) if i not in METODE_IDS]
PROBE_JENIS = [i for i in range(-2, 15) if i not in JENIS_IDS]
NODE_RE = re.compile(r"^(-?\d+)-(-?\d+)\|b(\w+)\|m(-?\w+)\|j(-?\w+)$")


class Blocked(Exception):
    """Situs menolak permintaan (403/429 berulang): hentikan, jangan dihindari."""


@dataclass(frozen=True)
class Node:
    lo: int
    hi: int
    bulan: int | None = None
    metode: int | None = None
    jenis: int | None = None

    def key(self) -> str:
        return f"{self.lo}-{self.hi}|b{self.bulan}|m{self.metode}|j{self.jenis}"


class Client:
    def __init__(self, delay: float = 1.0, timeout: int = 60, retries: int = 5) -> None:
        self.delay, self.timeout, self.retries = delay, timeout, retries
        self.requests = 0
        self._blocked_streak = 0
        self._last = 0.0

    def _sleep_polite(self) -> None:
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)

    def search(self, node: Node | None, start: int = 0, length: int = PAGE_SIZE, order: tuple[int, str] = (5, "desc")) -> dict:
        params = {
            "tahunAnggaran": YEAR,
            "jenisPengadaan": "" if node is None or node.jenis is None else node.jenis,
            "metodePengadaan": "" if node is None or node.metode is None else node.metode,
            "minPagu": "" if node is None else node.lo,
            "maxPagu": "" if node is None else node.hi,
            "bulan": "" if node is None or node.bulan is None else node.bulan,
            "lokasi": "", "kldi": "", "pdn": "", "ukm": "",
            "draw": 1, "start": start, "length": length,
            # server menolak (body kosong) bila parameter order tidak ada
            "order[0][column]": order[0], "order[0][dir]": order[1],
        }
        url = BASE + "?" + urllib.parse.urlencode(params)
        return self._get_json(url)

    def _get_json(self, url: str) -> dict:
        last_err: Exception | None = None
        for attempt in range(self.retries):
            self._sleep_polite()
            self._last = time.monotonic()
            self.requests += 1
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read()
                    if resp.headers.get("Content-Encoding") == "gzip":
                        raw = gzip.decompress(raw)
                self._blocked_streak = 0
                if not raw:
                    raise ValueError("respons kosong")
                data = json.loads(raw)
                if "recordsFiltered" not in data:
                    raise ValueError("bentuk respons tak dikenal")
                return data
            except urllib.error.HTTPError as e:
                if e.code in (403, 429):
                    self._blocked_streak += 1
                    if self._blocked_streak >= 3:
                        raise Blocked(f"HTTP {e.code} berulang — berhenti (hormati pembatasan situs)") from e
                    ra = e.headers.get("Retry-After")
                    time.sleep(max(60, int(ra)) if ra and ra.isdigit() else 60)
                last_err = e
            except Exception as e:  # timeout, JSON rusak, 5xx, jaringan
                last_err = e
            time.sleep(min(60, 2 ** (attempt + 1)))
        raise RuntimeError(f"gagal setelah {self.retries} percobaan: {last_err}")


def total_records(client: Client | None = None) -> int:
    """Jumlah paket yang saat ini tercatat di SIRUP (1 permintaan ringan)."""
    c = client or Client(delay=0)
    return int(c.search(None, 0, 1)["recordsTotal"])


# ── crawl ────────────────────────────────────────────────────────────────────
def _children(node: Node, count: int, metode_ids=METODE_IDS, jenis_ids=JENIS_IDS) -> list[Node]:
    if node.hi > node.lo:
        mid = (node.lo + node.hi) // 2
        return [Node(node.lo, mid, node.bulan, node.metode, node.jenis),
                Node(mid + 1, node.hi, node.bulan, node.metode, node.jenis)]
    # satu nilai pagu, masih terlalu banyak → pecah per dimensi lain
    if node.bulan is None:
        return [Node(node.lo, node.hi, b) for b in BULAN]
    if node.metode is None:
        return [Node(node.lo, node.hi, node.bulan, m) for m in metode_ids]
    if node.jenis is None:
        return [Node(node.lo, node.hi, node.bulan, node.metode, j) for j in jenis_ids]
    raise RuntimeError(f"potongan tak dapat dipecah lagi ({count} baris): {node.key()}")


def parse_key(k: str) -> Node:
    m = NODE_RE.match(k)
    if not m:
        raise ValueError(f"kunci node tidak dikenal: {k}")
    lo, hi, b, mm, j = m.groups()
    cv = lambda x: None if x == "None" else int(x)  # noqa: E731
    return Node(int(lo), int(hi), cv(b), cv(mm), cv(j))


class Crawler:
    def __init__(self, out: Path, client: Client) -> None:
        self.out, self.client = out, client
        out.mkdir(parents=True, exist_ok=True)
        self.manifest_path = out / "manifest.jsonl"
        self.done: dict[str, dict] = {}
        if self.manifest_path.exists():
            for line in self.manifest_path.read_text().splitlines():
                if line.strip():
                    rec = json.loads(line)
                    self.done[rec["node"]] = rec
        # penomoran berkas SELALU naik (bukan len(done): catatan 'split' yang diganti 'leaf' tidak menambah ukuran dict,
        # sehingga berkas berikutnya dulu menimpa potongan padat; bug nyata yang membuat 5.310 baris hilang)
        existing = [int(m.group(1)) for f in out.glob("leaf_*.jsonl.gz") if (m := re.match(r"leaf_(\d+)\.jsonl\.gz$", f.name))]
        self._file_seq = (max(existing) + 1) if existing else 0
        self.leaves = sum(1 for r in self.done.values() if r["status"] == "leaf")
        self.rows = sum(r.get("rows", 0) for r in self.done.values() if r["status"] == "leaf")

    def _log(self, rec: dict) -> None:
        self.done[rec["node"]] = rec
        with self.manifest_path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def _fetch_dense(self, node: Node, count: int) -> list[dict]:
        """Potongan padat yang tak bisa dipecah lagi: ambil berhalaman dari beberapa urutan lalu gabungkan.
        Urutan bertumpu (tie) bisa tidak stabil, jadi hasil WAJIB cocok dengan jumlah situs — bila tidak, gagal keras."""
        got: dict[int, dict] = {}
        for col in (1, 3, 4, 5, 6):  # kolom DataTables yang dapat diurutkan
            for direction in ("asc", "desc"):
                start = 0
                while start < count and len(got) < count:
                    data = self.client.search(node, start, PAGE_SIZE, order=(col, direction))
                    for r in data["data"]:
                        got[int(r["id"])] = r
                    start += PAGE_SIZE
                if len(got) >= count:
                    return list(got.values())
        raise RuntimeError(f"potongan padat tak lengkap: {len(got)}/{count} baris untuk {node.key()}")

    def _save_leaf(self, node: Node, rows: list[dict]) -> None:
        fname = f"leaf_{self._file_seq:06d}.jsonl.gz"
        self._file_seq += 1
        with gzip.open(self.out / fname, "wt", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        self._log({"node": node.key(), "status": "leaf", "count": len(rows), "rows": len(rows), "file": fname})
        self.leaves += 1
        self.rows += len(rows)

    def check_files(self) -> int:
        """Cocokkan manifest dengan berkas: berkas yang dipakai >1 potongan atau jumlah barisnya tak cocok → catatan ditandai
        'invalid' agar diambil ulang. Mengembalikan jumlah catatan yang diinvalidasi."""
        by_file: dict[str, list[str]] = {}
        for key, rec in self.done.items():
            if rec["status"] == "leaf" and rec.get("file"):
                by_file.setdefault(rec["file"], []).append(key)
        bad: list[str] = []
        for fname, keys in by_file.items():
            path = self.out / fname
            n = sum(1 for _ in gzip.open(path, "rt", encoding="utf-8")) if path.exists() else -1
            if len(keys) > 1 or n != self.done[keys[0]]["rows"]:
                bad += keys
        for key in bad:
            self._log({"node": key, "status": "invalid", "count": self.done[key].get("count"), "rows": 0, "file": None})
        self.leaves = sum(1 for r in self.done.values() if r["status"] == "leaf")
        self.rows = sum(r.get("rows", 0) for r in self.done.values() if r["status"] == "leaf")
        return len(bad)

    # ── audit kelengkapan ────────────────────────────────────────────────
    def _wide_children(self, node: Node, count: int) -> list[Node]:
        """Semua kemungkinan anak (ID dikenal + ID yang pernah diperiksa) — dipakai untuk menjumlah yang sudah terambil."""
        return _children(node, count, METODE_IDS + PROBE_METODE, JENIS_IDS + PROBE_JENIS)

    def _accounted(self, key: str, memo: dict) -> int:
        if key in memo:
            return memo[key]
        rec = self.done.get(key)
        if rec is None or rec["status"] == "invalid":
            out = 0
        elif rec["status"] == "leaf":
            out = rec.get("rows", 0)
        else:
            node = parse_key(key)
            try:
                kids = self._wide_children(node, rec["count"])
            except RuntimeError:
                kids = []
            out = sum(self._accounted(k.key(), memo) for k in kids)
        memo[key] = out
        return out

    def deficits(self) -> list[tuple[str, int]]:
        """Node 'split' yang jumlah anak-anaknya < jumlah di situs (= baris hilang akibat pembagian yang tak mencakup semua nilai)."""
        memo: dict = {}
        out = []
        for key, rec in self.done.items():
            if rec["status"] != "split":
                continue
            node = parse_key(key)
            try:
                kids = self._wide_children(node, rec["count"])
            except RuntimeError:
                continue
            gap = rec["count"] - sum(self._accounted(k.key(), memo) for k in kids)
            if gap > 0:
                out.append((key, gap))
        return out

    def run(self, target_total: int, edges: list[int] | None = None) -> None:
        bad = self.check_files()
        if bad:
            print(f"[audit] {bad} catatan tidak cocok dengan berkas → diambil ulang", flush=True)
        self._run_once(target_total, edges)
        # Repair: untuk node bercelah, periksa ID metode/jenis lain yang mungkin ada; ulangi sampai tuntas.
        for _ in range(3):
            gaps = self.deficits()
            if not gaps:
                break
            todo = 0
            for key, _g in gaps:
                node = parse_key(key)
                for kid in self._wide_children(node, self.done[key]["count"]):
                    if kid.key() not in self.done:
                        todo += 1
            print(f"[repair] {len(gaps)} node bercelah ({sum(g for _, g in gaps):,} baris); {todo} potongan baru diperiksa", flush=True)
            self._run_once(target_total, edges, only_nodes=[k for k, _ in gaps])
        left = self.deficits()
        if left:
            raise RuntimeError(f"audit kelengkapan gagal: {len(left)} node masih bercelah ({sum(g for _, g in left):,} baris), contoh {left[:3]}")

    def _run_once(self, target_total: int, edges: list[int] | None = None, only_nodes: list[str] | None = None) -> None:
        use_default = edges is None
        edges = edges or SEED_EDGES
        if only_nodes is not None:
            stack = [parse_key(k) for k in only_nodes]
        else:
            stack = [Node(lo, (edges[i + 1] - 1) if i + 1 < len(edges) else PAGU_MAX) for i, lo in enumerate(edges)]
            if use_default:
                stack.append(Node(-PAGU_MAX, -1))  # pagu negatif (ada beberapa baris)
        stack.reverse()
        t0 = time.time()
        while stack:
            node = stack.pop()
            rec = self.done.get(node.key())
            if rec and rec["status"] == "invalid":
                rec = None
            if rec and rec["status"] == "leaf":
                continue
            count = rec["count"] if rec else None
            if count is None:
                data = self.client.search(node)
                count = int(data["recordsFiltered"])
                rows = data["data"]
                if count == 0:
                    self._log({"node": node.key(), "status": "leaf", "count": 0, "rows": 0, "file": None})
                    continue
                if count <= PAGE_SIZE:
                    if len(rows) != count:
                        raise RuntimeError(f"{node.key()}: diminta {count}, diterima {len(rows)}")
                    self._save_leaf(node, rows)
                    continue
            try:
                kids = (self._wide_children(node, count) if only_nodes is not None else _children(node, count))
            except RuntimeError:  # tidak dapat dipecah lagi → ambil padat
                self._save_leaf(node, self._fetch_dense(node, count))
                continue
            if not (rec and rec["status"] == "split"):
                self._log({"node": node.key(), "status": "split", "count": count})
            stack.extend(reversed(kids))
            if self.client.requests % 25 == 0:
                el = time.time() - t0
                print(f"[crawl] req={self.client.requests} leaf={self.leaves} rows={self.rows:,}/{target_total:,} "
                      f"({self.rows / max(target_total, 1):.1%}) {el / 60:.1f} mnt", flush=True)


def verify(out: Path) -> dict:
    """Rekonsiliasi: baris unik hasil crawl vs total situs."""
    ids: set[int] = set()
    dup = 0
    n = 0
    for f in sorted(out.glob("leaf_*.jsonl.gz")):
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                n += 1
                i = json.loads(line)["id"]
                if i in ids:
                    dup += 1
                ids.add(i)
    site_total = total_records()
    return {"rows": n, "unique_ids": len(ids), "duplicates": dup, "site_total_now": site_total,
            "missing_vs_site": site_total - len(ids)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    c = sub.add_parser("crawl")
    c.add_argument("--out", required=True)
    c.add_argument("--delay", type=float, default=1.0, help="jeda minimal antar-permintaan (detik)")
    v = sub.add_parser("verify")
    v.add_argument("--out", required=True)
    a = ap.parse_args()

    if a.cmd == "probe":
        print(json.dumps({"site_total": total_records(), "year": YEAR}))
    elif a.cmd == "crawl":
        if a.delay < 0.5:
            sys.exit("--delay minimal 0.5 detik (kesopanan terhadap situs publik).")
        client = Client(delay=a.delay)
        target = total_records(client)
        print(f"[crawl] total di SIRUP saat ini: {target:,}", flush=True)
        try:
            Crawler(Path(a.out), client).run(target)
        except Blocked as e:
            sys.exit(f"[crawl] DIHENTIKAN: {e}")
        print(json.dumps(verify(Path(a.out)), indent=2))
    elif a.cmd == "verify":
        print(json.dumps(verify(Path(a.out)), indent=2))


if __name__ == "__main__":
    main()
