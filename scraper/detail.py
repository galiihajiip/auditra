"""Halaman detail paket SIRUP (`detailPaketPenyedia2020`) → dict. Dipakai untuk cek langsung per paket
dan untuk memperkaya uraian/volume/spesifikasi sesuai permintaan (bukan untuk 3 juta paket sekaligus)."""

from __future__ import annotations

import re
import urllib.request

DETAIL_URL = "https://sirup.inaproc.id/sirup/rup/detailPaketPenyedia2020?idPaket={id}"
USER_AGENT = "AuditraResearchBot/1.0 (riset akademik; data publik SIRUP; 1 koneksi)"

# label di halaman → nama field
FIELDS = {
    "Kode RUP": "id",
    "Nama Paket": "paket",
    "Nama KLPD": "lembaga",
    "Satuan Kerja": "satker",
    "Volume Pekerjaan": "volumePekerjaan",
    "Uraian Pekerjaan": "uraianPekerjaan",
    "Spesifikasi Pekerjaan": "spesifikasiPekerjaan",
    "Total Pagu": "pagu",
    "Metode Pemilihan": "metode",
}


def _tokens(html: str) -> list[str]:
    html = re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", html)
    return [t.strip() for t in text.replace("&nbsp;", " ").splitlines() if t.strip()]


def parse_detail(html: str) -> dict:
    toks = _tokens(html)
    out: dict = {}
    for i, tok in enumerate(toks[:-1]):
        field = FIELDS.get(tok)
        if field and field not in out:
            out[field] = toks[i + 1]
    if "id" not in out:
        raise ValueError("halaman detail tidak dikenali (paket tidak ada / struktur berubah)")
    out["id"] = int(out["id"])
    if "pagu" in out:
        digits = re.sub(r"[^\d]", "", out["pagu"])
        out["pagu"] = int(digits) if digits else None
    return out


def fetch_detail(package_id: int, timeout: int = 15) -> dict:
    req = urllib.request.Request(DETAIL_URL.format(id=int(package_id)), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return parse_detail(resp.read().decode("utf-8", "replace"))
