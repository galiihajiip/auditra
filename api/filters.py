"""Shared SQL filter builder for dashboard queries."""

from __future__ import annotations

# Alias UI / lokasi SIRUP → nama provinsi di geo_lookup (UPPERCASE)
PROVINSI_ALIASES: dict[str, str] = {
    "di yogyakarta": "DAERAH ISTIMEWA YOGYAKARTA",
    "diy": "DAERAH ISTIMEWA YOGYAKARTA",
    "daerah istimewa yogyakarta": "DAERAH ISTIMEWA YOGYAKARTA",
    "dki jakarta": "DKI JAKARTA",
    "jakarta": "DKI JAKARTA",
    "jawa barat": "JAWA BARAT",
    "jawa tengah": "JAWA TENGAH",
    "jawa timur": "JAWA TIMUR",
}


def resolve_provinsi(name: str) -> str:
    """Samakan variasi penulisan provinsi ke nama di geo_lookup."""
    key = name.strip().lower()
    return PROVINSI_ALIASES.get(key, name.strip())


def provinsi_match_sql(column: str) -> str:
    """Perbandingan provinsi case-insensitive (geo_lookup = UPPERCASE)."""
    return f"UPPER(TRIM({column})) = UPPER(TRIM(?))"


