# Sumber Data — Provenance

## Data Utama

| Atribut | Nilai |
|---------|-------|
| **Nama** | SIRUP (Sistem Informasi Rencana Umum Pengadaan) |
| **Penyedia** | LKPP — Lembaga Kebijakan Pengadaan Barang/Jasa Pemerintah |
| **URL** | https://sirup.lkpp.go.id/ |
| **File lokal** | `data/year-2026_merged.csv` |
| **Periode** | Rencana pengadaan 2026 |
| **Baris mentah** | 3.009.760 |
| **Baris setelah cleaning** | 3.002.992 |
| **Kolom dipakai** | 16 field SIRUP murni (+ 1 derived) |

## Kolom yang Digunakan

`id`, `paket`, `jenisPengadaan`, `metode`, `lembaga`, `satker`, `lokasi`, `pagu`, `pemilihanDate`, `sumberDana`, `isUMKM`, `volumePekerjaan`, `uraianPekerjaan`, `spesifikasiPekerjaan`, `ownerType`, `dalamNegeri`

## Kolom yang Dihapus (Preprocessing)

Kolom enrichment pihak ketiga (bukan data resmi SIRUP): `potensiPemborosan`, `tags.isInappropriate`, dll.

## Data Pendukung

| File | Sumber | Lisensi |
|------|--------|---------|
| `kabkota.geojson` | [eppofahmi/geojson-indonesia](https://github.com/eppofahmi/geojson-indonesia) | Open |
| `geo/kabkota_clean.geojson` | Derived (514 features) | — |

