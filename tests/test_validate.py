"""Unit tests for pipeline validation."""

from pathlib import Path

import pandas as pd
import pytest

from pipeline.validate import ValidationResult, validate_clean, validate_scored


@pytest.fixture
def tmp_clean_csv(tmp_path: Path) -> Path:
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "paket": ["A", "B", "C"],
        "metode": ["Tender", "Tender", "Tender"],
        "lembaga": ["K1", "K2", "K3"],
        "pagu": [100_000_000, 200_000_000, 300_000_000],
        "lokasi": ["Jakarta", "Bandung", "Surabaya"],
    })
    path = tmp_path / "clean.csv"
    df.to_csv(path, index=False)
    return path


