"""Klasifikasi pemilik paket SIRUP untuk mode peta (K/L · Pemprov · Pemkot · Lainnya)."""

from __future__ import annotations

# SQL expression → 'kl' | 'pemprov' | 'pemkot' | 'others'
# Gunakan alias tabel ``p`` untuk kolom packages (ownerType, lembaga).
OWNER_CATEGORY_EXPR = """
CASE
    WHEN COALESCE(p.ownerType, '') ILIKE '%kementerian%'
      OR COALESCE(p.ownerType, '') ILIKE '%lembaga%'
      OR COALESCE(p.ownerType, '') ILIKE '%k/l%'
      OR UPPER(TRIM(COALESCE(p.ownerType, ''))) IN ('KL', 'K/L', 'KEMENTERIAN/LEMBAGA')
      THEN 'kl'
    WHEN COALESCE(p.ownerType, '') ILIKE '%provinsi%'
      OR COALESCE(p.ownerType, '') ILIKE '%pemprov%'
      OR COALESCE(p.lembaga, '') ILIKE 'PEMERINTAH PROVINSI%'
      OR COALESCE(p.lembaga, '') ILIKE 'PEMPROV %'
      THEN 'pemprov'
    WHEN COALESCE(p.ownerType, '') ILIKE '%kabupaten%'
