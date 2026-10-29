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


